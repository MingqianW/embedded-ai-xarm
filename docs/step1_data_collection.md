# Step 1 Data Collection Guidelines

This document outlines the task families and guidelines for collecting 100 hours of teleoperated demonstrations on an xArm 6 robot as part of Step 1 of the embodied AI project. The goal is to create a diverse, high‑quality dataset for imitation learning.

## Task Families and Hours Allocation

| Task family | Examples | Approx. hours | Purpose |
|---|---|---|---|
| **Reach/touch** | Move the gripper above an object; touch a block | **5 h** | Calibration and spatial control |
| **Single-object pick** | Pick up a cube or cylinder | **10 h** | Isolate grasping |
| **Pick-and-place zones** | Pick and place objects into colour‑coded zones | **25 h** | Core pick‑and‑place primitive |
| **Sorting** | Sort objects by colour or shape into trays | **15 h** | Object and language grounding |
| **Stacking** | Stack one block atop another | **10 h** | Precise placement |
| **Push/slide** | Push objects to target locations | **10 h** | Non‑prehensile manipulation |
| **Container placement** | Place objects into bowls, trays or boxes | **10 h** | More realistic placement |
| **Short multi‑step tasks** | Two–three step sequences (e.g., pick then push) | **15 h** | Long‑horizon behaviour |

## Objects and Environment

* Use simple, rigid objects: coloured cubes, cylinders, lightweight blocks.
* Avoid transparent, glossy or deformable objects until later stages.
* Start with a fixed camera and optionally a wrist camera for observations.

## Episode Metadata

Each recorded episode should include: timestamped RGB images, robot joint positions, end‑effector pose, gripper state, actions, language instruction, task name, success label and failure reason. Include calibration identifiers and operator IDs so datasets remain consistent over time.

## Dataset Quality Checklist

Before scaling up, ensure that:

* Images, robot states and actions are synchronized and of equal length.
* Language instructions and task names are recorded.
* Success or failure labels are present.
* Episodes can be replayed to visualize results.
* A small behavioural cloning model can train on the data without errors.

## Data Collection Process

1. Collect a small pilot set (e.g., 5 episodes per task) to verify the pipeline.
2. Validate and replay the data; fix any synchronization or logging issues.
3. Collect larger batches (e.g., 50–100 episodes) and train baseline models.
4. Only after verifying baseline performance, scale up to the full 100 hour dataset.

## Randomization and Balance

* Randomize one or two factors at a time (object position, colour or target location), not everything simultaneously.
* Balance the dataset across object colours, shapes and positions.
* Keep action representation consistent across tasks: `[dx, dy, dz, droll, dpitch, dyaw, gripper]`, with deltas in metres/radians and gripper in {0,1}.

Refer to the `docs/task_specs` directory for concrete YAML definitions of individual tasks. Additional task specifications for each family should be added there, following the template in `task_001_pick_place.yaml`.
