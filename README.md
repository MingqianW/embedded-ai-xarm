# Embedded AI xArm – Step 1

This repository contains the first stage of an embedded AI project. In this step we define manipulation tasks, generate trajectories on a real xArm 6 robot, and record the data in a clean format suitable for demonstration learning.

## Contents

- `docs/task_specs/` — YAML files defining each manipulation task.
- `scripts/teleop_collect.py` — skeleton script for collecting teleoperation demonstrations.
- `scripts/validate_dataset.py` — script to validate demonstration datasets.
- `scripts/prepare_openpi_lerobot.py` — converts raw xArm HDF5 demonstrations to LeRobot for OpenPI fine-tuning.
- `fine_tune/` — OpenPI config snippet and fine-tuning helper script.
- `requirements.txt` — list of Python dependencies.

More detailed documentation will be added as the project progresses.
See `docs/step1_data_collection.md` for guidelines on Step 1 data collection, including task families, hours allocation and dataset quality.
See `docs/step2_openpi_finetuning.md` for the raw data format, LeRobot conversion, and OpenPI pi0.5 fine-tuning instructions.
