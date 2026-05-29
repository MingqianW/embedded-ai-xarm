#!/usr/bin/env python3
"""
teleop_collect.py
==================

Collect teleoperated demonstrations on an xArm 6 robot.  This script
initialises the robot and RealSense cameras, logs observations and
actions into an HDF5 dataset and applies user‑provided actions to the
robot in real time.  The RealSense device whose serial number ends
with ``246322303938`` is treated as the wrist camera; the first
additional device is treated as a fixed camera.

Edit the `get_user_action` function to read from your preferred
teleoperation device (keyboard, joystick, SpaceMouse, etc.).  Actions
should be numpy arrays of shape (7,) containing `[dx, dy, dz,
droll, dpitch, dyaw, gripper]` where translations are in metres,
rotations in radians and gripper commands in [0, 1].

Example usage:
    python teleop_collect.py --task docs/task_specs/task_001_pick_place.yaml --output data/raw/pick_place.hdf5
"""

import argparse
import os
import time
import math
from pathlib import Path

import h5py
import numpy as np
import yaml

from xarm.wrapper import XArmAPI
import pyrealsense2 as rs

# Global handles for the robot and cameras
_arm = None
_cameras = {}

def connect_robot():
    global _arm
    if _arm:
        return _arm
    robot_ip = os.getenv('XARM_IP', '192.168.1.200')
    arm = XArmAPI(robot_ip, baud_checkset=False)
    arm.clean_warn()
    arm.clean_error()
    arm.motion_enable(True)
    arm.set_mode(0)
    arm.set_state(0)
    try:
        arm.set_gripper_enable(True)
        arm.set_gripper_mode(0)
        arm.clean_gripper_error()
    except Exception:
        pass
    _arm = arm
    return arm

def connect_cameras():
    global _cameras
    if _cameras:
        return _cameras
    ctx = rs.context()
    devices = [d for d in ctx.devices if d.get_info(rs.camera_info.name).lower() != 'platform camera']
    wrist_hint = '246322303938'
    for d in devices:
        serial = d.get_info(rs.camera_info.serial_number)
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_device(serial)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        try:
            pipeline.start(config)
        except Exception:
            continue
        if wrist_hint in serial and 'wrist_camera_rgb' not in _cameras:
            _cameras['wrist_camera_rgb'] = pipeline
        elif 'fixed_camera_rgb' not in _cameras:
            _cameras['fixed_camera_rgb'] = pipeline
        else:
            pipeline.stop()
    return _cameras

def get_user_action():
    """
    Return the next user action as a 7‑D vector [dx, dy, dz, droll, dpitch, dyaw, gripper].
    Replace this placeholder to read from your teleop device.
    """
    return np.zeros(7, dtype=np.float32)

def capture_observations():
    if _arm is None:
        raise RuntimeError("Robot not initialised")
    obs = {}
    for name, pipeline in _cameras.items():
        try:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if color_frame:
                obs[name] = np.asanyarray(color_frame.get_data())
        except Exception:
            pass
    code_j, joints = _arm.get_servo_angle()
    code_p, pose_mm = _arm.get_position()
    if code_j != 0 or code_p != 0:
        raise RuntimeError("Failed to read robot state")
    obs['robot_joint_positions'] = np.array(joints, dtype=np.float32)
    x, y, z = pose_mm[0]/1000.0, pose_mm[1]/1000.0, pose_mm[2]/1000.0
    r, p, y_ = [math.radians(a) for a in pose_mm[3:6]]
    obs['end_effector_pose'] = np.array([x, y, z, r, p, y_], dtype=np.float32)
    return obs

def record_episode(hdf, task, frequency):
    dt = 1.0 / frequency
    demo_id = f"demo_{len(hdf['data'])+1:06d}"
    input(f"Press Enter to start recording {demo_id} (Ctrl-C to abort)...")
    grp = hdf['data'].create_group(demo_id)
    grp.attrs['task_name'] = task['task_name']
    grp.attrs['language_instruction'] = task['language_instruction']
    grp.create_dataset('task_spec', data=np.string_(yaml.dump(task)))
    timestamps, joints, poses, grippers, actions = [], [], [], [], []
    obs_buf = {k: [] for k in task['observations']}
    last_step = time.time()
    try:
        while True:
            now = time.time()
            if now - last_step < dt:
                time.sleep(max(0.0, dt - (now - last_step)))
                continue
            last_step = now
            action = get_user_action()
            obs = capture_observations()
            timestamps.append(now)
            joints.append(obs['robot_joint_positions'].copy())
            poses.append(obs['end_effector_pose'].copy())
            grippers.append(float(action[-1]))
            actions.append(action.copy())
            for k, v in obs.items():
                obs_buf[k].append(v)
            # apply action
            cur_xyz = obs['end_effector_pose'][:3]
            cur_rpy = obs['end_effector_pose'][3:]
            delta_xyz = action[:3]
            delta_rpy = action[3:6]
            new_xyz = cur_xyz + delta_xyz
            new_rpy = cur_rpy + delta_rpy
            target_mm = [float(c*1000.0) for c in new_xyz]
            target_deg = [float(math.degrees(a)) for a in new_rpy]
            _arm.set_position(target_mm[0], target_mm[1], target_mm[2], target_deg[0], target_deg[1], target_deg[2], wait=False)
            if action[6] >= 0.5:
                _arm.set_gripper_position(0, wait=False)
            else:
                _arm.set_gripper_position(830, wait=False)
    except KeyboardInterrupt:
        print("Episode interrupted")
    grp.create_dataset('timestamps', data=np.array(timestamps, dtype=np.float64))
    grp.create_dataset('joint_positions', data=np.array(joints, dtype=np.float32))
    grp.create_dataset('end_effector_pose', data=np.array(poses, dtype=np.float32))
    grp.create_dataset('gripper', data=np.array(grippers, dtype=np.float32))
    grp.create_dataset('actions', data=np.array(actions, dtype=np.float32))
    for k, frames in obs_buf.items():
        grp.create_dataset(f'observations/{k}', data=np.stack(frames, axis=0))
    grp.attrs['success'] = False
    print(f"Saved {demo_id} with {len(actions)} steps")

def parse_args():
    parser = argparse.ArgumentParser(description="Collect teleoperated demonstrations for xArm 6")
    parser.add_argument('--task', required=True, help='Path to task specification YAML')
    parser.add_argument('--output', required=True, help='Output HDF5 file path')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing file')
    parser.add_argument('--frequency', type=float, default=None, help='Control frequency in Hz')
    return parser.parse_args()

def main():
    args = parse_args()
    with open(args.task, 'r') as f:
        task = yaml.safe_load(f)
    freq = args.frequency or task.get('control_frequency_hz', 10.0)
    connect_robot()
    connect_cameras()
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    mode = 'w' if args.overwrite else 'a'
    with h5py.File(out_path, mode) as hdf:
        if 'data' not in hdf:
            hdf.create_group('data')
        while True:
            record_episode(hdf, task, freq)
            cont = input('Record another episode? [y/N]: ').strip().lower()
            if cont != 'y':
                break
    for pipeline in _cameras.values():
        try:
            pipeline.stop()
        except Exception:
            pass

if __name__ == '__main__':
    main()
