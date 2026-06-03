#!/usr/bin/env python3
"""
Convert this project's xArm HDF5 demonstrations into a LeRobot dataset for OpenPI.

The collector does not need to be tied to xArm directly. It only needs to write the
HDF5 structure documented in docs/step2_openpi_finetuning.md.

Example:
    python scripts/prepare_openpi_lerobot.py \
        --input data/raw/pick_place.hdf5 \
        --repo-id your_hf_username/xarm_pick_place \
        --robot-type xarm6
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Any

import cv2
import h5py
import numpy as np


IMAGE_SIZE = (256, 256)
STATE_DIM = 13
ACTION_DIM = 7


def _import_lerobot() -> tuple[Any, Path]:
    try:
        from lerobot.common.datasets.lerobot_dataset import HF_LEROBOT_HOME
        from lerobot.common.datasets.lerobot_dataset import LeRobotDataset
    except ImportError as exc:
        raise SystemExit(
            "LeRobot is not installed. Run this from the OpenPI environment after "
            "`GIT_LFS_SKIP_SMUDGE=1 uv sync` and `GIT_LFS_SKIP_SMUDGE=1 uv pip install -e .`."
        ) from exc
    return LeRobotDataset, HF_LEROBOT_HOME


def _read_attr(grp: h5py.Group, key: str, default: str = "") -> str:
    value = grp.attrs.get(key, default)
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)


def _episode_len(grp: h5py.Group) -> int:
    if "actions" not in grp:
        raise ValueError(f"{grp.name} is missing actions")
    return int(grp["actions"].shape[0])


def _image_at(grp: h5py.Group, key: str, index: int, input_color: str) -> np.ndarray:
    path = f"observations/{key}"
    if path not in grp:
        return np.zeros((IMAGE_SIZE[1], IMAGE_SIZE[0], 3), dtype=np.uint8)

    image = np.asarray(grp[path][index])
    if image.ndim != 3 or image.shape[-1] != 3:
        raise ValueError(f"{grp.name}/{path} must have shape [T,H,W,3]")
    if input_color == "bgr":
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, IMAGE_SIZE, interpolation=cv2.INTER_AREA)
    return image.astype(np.uint8)


def _state_at(grp: h5py.Group, index: int) -> np.ndarray:
    joints = np.asarray(grp["joint_positions"][index], dtype=np.float32)
    pose = np.asarray(grp["end_effector_pose"][index], dtype=np.float32)
    gripper = np.asarray([grp["gripper"][index]], dtype=np.float32)
    state = np.concatenate([joints, pose, gripper], axis=0)
    if state.shape != (STATE_DIM,):
        raise ValueError(f"{grp.name} state must be {STATE_DIM} values, got {state.shape}")
    return state


def _action_at(grp: h5py.Group, index: int) -> np.ndarray:
    action = np.asarray(grp["actions"][index], dtype=np.float32)
    if action.shape != (ACTION_DIM,):
        raise ValueError(f"{grp.name} action must be {ACTION_DIM} values, got {action.shape}")
    return action


def convert_dataset(
    input_path: Path,
    repo_id: str,
    robot_type: str,
    fps: int,
    input_color: str,
    overwrite: bool,
    push_to_hub: bool,
) -> Path:
    LeRobotDataset, hf_lerobot_home = _import_lerobot()
    output_path = hf_lerobot_home / repo_id
    if output_path.exists():
        if not overwrite:
            raise SystemExit(f"{output_path} already exists. Pass --overwrite to replace it.")
        shutil.rmtree(output_path)

    dataset = LeRobotDataset.create(
        repo_id=repo_id,
        robot_type=robot_type,
        fps=fps,
        features={
            "image": {
                "dtype": "image",
                "shape": (IMAGE_SIZE[1], IMAGE_SIZE[0], 3),
                "names": ["height", "width", "channel"],
            },
            "wrist_image": {
                "dtype": "image",
                "shape": (IMAGE_SIZE[1], IMAGE_SIZE[0], 3),
                "names": ["height", "width", "channel"],
            },
            "state": {
                "dtype": "float32",
                "shape": (STATE_DIM,),
                "names": ["state"],
            },
            "actions": {
                "dtype": "float32",
                "shape": (ACTION_DIM,),
                "names": ["actions"],
            },
        },
        image_writer_threads=8,
        image_writer_processes=2,
    )

    with h5py.File(input_path, "r") as hdf:
        if "data" not in hdf:
            raise ValueError("Expected top-level group named 'data'")

        for episode_name in sorted(hdf["data"].keys()):
            grp = hdf["data"][episode_name]
            prompt = _read_attr(grp, "language_instruction")
            if not prompt:
                prompt = _read_attr(grp, "task_name", episode_name)

            length = _episode_len(grp)
            for step in range(length):
                dataset.add_frame(
                    {
                        "image": _image_at(grp, "fixed_camera_rgb", step, input_color),
                        "wrist_image": _image_at(grp, "wrist_camera_rgb", step, input_color),
                        "state": _state_at(grp, step),
                        "actions": _action_at(grp, step),
                        "task": prompt,
                    }
                )
            dataset.save_episode()
            print(f"Converted {episode_name}: {length} frames")

    if push_to_hub:
        dataset.push_to_hub(
            tags=["xarm", "openpi", "lerobot"],
            private=False,
            push_videos=True,
            license="apache-2.0",
        )

    print(f"Saved LeRobot dataset to {output_path}")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert xArm HDF5 demos to LeRobot for OpenPI.")
    parser.add_argument("--input", required=True, type=Path, help="Raw xArm HDF5 dataset.")
    parser.add_argument("--repo-id", required=True, help="LeRobot repo id, e.g. username/xarm_pick_place.")
    parser.add_argument("--robot-type", default="xarm6", help="Robot type stored in LeRobot metadata.")
    parser.add_argument("--fps", type=int, default=10, help="Dataset frame rate.")
    parser.add_argument(
        "--input-color",
        choices=["bgr", "rgb"],
        default="bgr",
        help="Color order in the raw HDF5 images. RealSense/OpenCV collection is usually BGR.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing LeRobot dataset.")
    parser.add_argument("--push-to-hub", action="store_true", help="Upload the converted dataset to Hugging Face.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    convert_dataset(
        input_path=args.input,
        repo_id=args.repo_id,
        robot_type=args.robot_type,
        fps=args.fps,
        input_color=args.input_color,
        overwrite=args.overwrite,
        push_to_hub=args.push_to_hub,
    )


if __name__ == "__main__":
    main()
