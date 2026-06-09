# Pick-Up Data Collection Plan

Goal: collect pick-up demonstrations for three blocks:

- `dark_blue_block`
- `light_blue_block`
- `red_block`

Scope: **pick up only**. Do not collect place, stack, or put-on-top tasks for this dataset.

## Current Dataset

| Existing Pick-Up Task | Episodes |
|---|---:|
| `pick_up_blue_block` | 20 |

The existing `place_red_on_blue` data should not be used for this pick-up-only training round unless you intentionally train a mixed-task model later.

## Dataset Target

Preferred full pick-up dataset:

```text
500 pick-up episodes
Average episode length: 12-16 seconds
Approximate effective duration: 125 minutes
```

## Pick-Up Motion Style Rule

For clean success pick-up demonstrations, use the following canonical motion style:

1. Start with the gripper open and above the workspace.
2. Move laterally at a safe height until the gripper is above the target block.
3. Align the gripper with the block while staying above the block.
4. Descend mostly vertically.
5. Close the gripper.
6. Lift the block vertically.
7. Hold the lifted block for at least 0.5 seconds.

## Episode Plan

| Stage | Episodes | Purpose |
|---|---:|---|
| Stage 0 | 40 | pipeline validation |
| Stage 1 | 120 | single-block basic pick-up |
| Stage 2 | 120 | single-block pick-up with stronger randomness |
| Stage 3 | 130 | three-block target selection pick-up |
| Stage 4 | 60 | hard pick-up cases and boundary positions |
| Stage 5 | 40 | recovery pick-up |
| **Total** | **500** | pick-up-only dataset |

## Stage 0: Pipeline Validation

Episodes:

```text
30 total
10 dark blue
10 light blue
10 red
```

Scene:

```text
Only one block visible.
```


Check:

```text
camera recording
state/action alignment
gripper command
LeRobot conversion
training pipeline
```

## Stage 1: Single-Block Basic Pick-Up

Episodes:

```text
120 total
40 dark blue
40 light blue
40 red
```

Scene:

```text
Only one block visible.
```

Randomness:

```text
object x/y: +/- 5 cm
object yaw: +/- 20-30 deg
gripper initial x/y/z: +/- 2-3 cm
gripper initial yaw: +/- 10 deg
lighting: fixed
background: clean
```

Features:

```text
clean successful pick-up only
smooth motion
no recovery
no long pause
block lifted and held for at least 0.3 seconds
```

## Stage 2: Single-Block Pick-Up With Stronger Randomness

Episodes:

```text
120 total
40 dark blue
40 light blue
40 red
```

Scene:

```text
Only one block visible.
```

Randomness:

```text
object x/y: +/- 8-10 cm
object yaw: +/- 45 deg
gripper initial x/y/z: +/- 3-5 cm
gripper initial yaw: +/- 15-20 deg
lighting: fixed or mild variation
background: clean
```

Coverage:

```text
left / center / right
near / middle / far
```

For each block, cover all major workspace regions.

## Stage 3: Three-Block Target Selection

Episodes:

```text
130 total
45 dark blue target
45 light blue target
40 red target
```

Scene:

```text
All three blocks visible.
Prompt specifies the target block.
Only the target block should be picked up.
No placing after lift.
```

Randomness:

```text
target block x/y: +/- 8-12 cm
distractor block x/y: randomized
block yaw: +/- 45 deg
minimum distance between blocks: 6-10 cm
gripper initial x/y/z: +/- 3-5 cm
lighting: fixed or mild variation
background: clean
```

Critical rule:

```text
Do not let color correlate with position.
```

Bad:

```text
red always on right
dark blue always on left
light blue always in center
```

Good:

```text
each block appears left, center, and right
dark blue and light blue often swap positions
red sometimes appears between the two blue blocks
```

Discard or label separately if the wrong block is picked or contacted first.

## Stage 4: Hard Pick-Up Cases And Boundary Positions

Episodes:

```text
60 total
20 dark blue
20 light blue
20 red
```

Scene split:

```text
30 single-block hard pick-up cases
30 three-block hard target-selection cases
```

Randomness:

```text
object near workspace boundary: 30 percent
object yaw: +/- 60-90 deg
gripper initial pose farther from object: +/- 5-8 cm
target close to distractor: 20 percent
lighting: mild variation only
```

Include:

```text
block near left workspace edge
block near right workspace edge
block near far side
diagonal block orientation
dark blue close to light blue
large block close to small block
```

Avoid:

```text
unsafe reach
severe occlusion
table-edge instability
robot joint limit
camera cannot see target
```

## Stage 5: Recovery Pick-Up

Episodes:

```text
40 total
15 missed-grasp recovery
10 object-pushed recovery
10 bad-alignment recovery
5 partial-grasp recovery
```

Scene:

```text
Start from the near-failure state directly.
Must end in successful pick-up.
No final failure episodes in main training data.
No placing after recovery.
```

Good starts:

```text
gripper slightly misaligned
block slightly pushed away
gripper close to block but not grasped
partial contact but no lift yet
```

Avoid:

```text
normal start -> intentionally miss -> retry -> success
```

Randomness:

```text
misalignment: 1-4 cm
block pushed distance: 2-6 cm
block yaw after disturbance: +/- 30-60 deg
gripper initial pose: close to failure state
```



## Task Prompts

Use only three stable task names. Do not put scene type, distractors, or recovery in the prompt.

| Raw Task Folder | Prompt |
|---|---|
| `pick_up_dark_blue_block` | `pick up dark blue block` |
| `pick_up_light_blue_block` | `pick up light blue block` |
| `pick_up_red_block` | `pick up red block` |

Stages 3-5 should still use the same three task folders/prompts. Record scene type in metadata or collection notes instead.

Recommended episode ranges inside each task folder:

| Episode Range | Stage | Scene Type | Episode Type | Notes |
|---|---|---|---|---|
| `episode_000-009` | Stage 0 | `single_block_pipeline_validation` | `clean_success` | easy pipeline check |
| `episode_010-049` | Stage 1 | `single_block_basic` | `clean_success` | one block visible, basic randomness |
| `episode_050-089` | Stage 2 | `single_block_randomized` | `clean_success` | one block visible, stronger randomness |
| `episode_090-134` | Stage 3 | `three_block_selection` | `clean_success` | all three blocks visible, target from prompt |
| `episode_135-154` | Stage 4 | `hard_pick_up` | `clean_success` | boundary positions / close distractors |
| `episode_155-167` | Stage 5 | `recovery_pick_up` | `recovery_success` | near-failure starts, must end in success |







## Data Format

Current xArm dataset convention:

```text
image       = realsense_0
wrist_image = realsense_1
state       = [j1_rad, j2_rad, j3_rad, j4_rad, j5_rad, j6_rad, gripper_mm]
actions     = next-frame absolute state
fps         = 10 Hz
```

OpenPI config:

```text
use_delta_joint_actions = True
extra_delta_transform = False
```

Meaning:

```text
first 6 action dims become joint deltas during training
gripper remains absolute
```

## Collection Strategy

Recommended order:

```text
1. Stage 0: 40 episodes
2. Train quick baseline and verify pipeline
3. Stage 1 + Stage 2 until 250 total pick-up episodes
4. Train/evaluate pick-up baseline
5. Add Stage 3, 4, 5 based on failures
6. Train full 500-episode pick-up model
```



