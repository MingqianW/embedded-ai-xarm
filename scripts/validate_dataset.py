"""
validate_dataset.py

Validates demonstration dataset files for xArm manipulation tasks.

This script checks HDF5 demonstration files for consistency, e.g. matching image/action counts,
presence of required datasets and attributes, and prints summary statistics.

Usage:
    python validate_dataset.py --input path/to/dataset.hdf5
"""

import argparse
import h5py

REQUIRED_DATASETS = ["images", "states", "actions"]

def validate_episode(grp):
    errors = []
    for ds_name in REQUIRED_DATASETS:
        if ds_name not in grp:
            errors.append(f"Missing dataset '{ds_name}'")
    lengths = [grp[ds].shape[0] for ds in REQUIRED_DATASETS if ds in grp]
    if len(set(lengths)) > 1:
        errors.append(f"Mismatched lengths: {lengths}")
    if "task_name" not in grp.attrs:
        errors.append("Missing task_name attribute")
    return errors

def main():
    parser = argparse.ArgumentParser(description="Validate demonstration dataset.")
    parser.add_argument("--input", type=str, required=True, help="Path to HDF5 dataset.")
    args = parser.parse_args()

    with h5py.File(args.input, "r") as f:
        if "data" not in f:
            print("Error: top-level 'data' group not found.")
            return
        errors_total = 0
        for episode_name, grp in f["data"].items():
            errs = validate_episode(grp)
            if errs:
                errors_total += len(errs)
                print(f"{episode_name}:")
                for e in errs:
                    print(f"  - {e}")
        if errors_total == 0:
            print("Dataset validation passed with no errors.")
        else:
            print(f"Dataset validation completed with {errors_total} errors.")

if __name__ == "__main__":
    main()
