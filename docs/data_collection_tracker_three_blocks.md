# Three-Block Pick-Up Tracker

Use only these three task folders/prompts:

| Task Folder | Prompt | Target Episodes | Done |
|---|---|---:|---:|
| `pick_up_dark_blue_block` | `pick up dark blue block` | 168 | 50 |
| `pick_up_light_blue_block` | `pick up light blue block` | 168 | 50 |
| `pick_up_red_block` | `pick up red block` | 168 | 50 |
| **Total** |  | **504** | **0** |

Scene type, distractors, hard cases, and recovery are metadata/notes only. Do not put them in the prompt.

## Episode Ranges

Use the same ranges inside each task folder.

| Range | Stage | Count / Block | Scene Type | Notes |
|---|---|---:|---|---|
| `000-009` | Stage 0 | 10 | `single_block_pipeline_validation` | easy pipeline check |
| `010-049` | Stage 1 | 40 | `single_block_basic` | one block, basic randomness |
| `050-089` | Stage 2 | 40 | `single_block_randomized` | one block, stronger randomness |
| `090-134` | Stage 3 | 45 | `three_block_selection` | all three blocks visible |
| `135-154` | Stage 4 | 20 | `hard_pick_up` | boundary / close distractors |
| `155-167` | Stage 5 | 13 | `recovery_pick_up` | near-failure starts |

## Milestones

| Milestone | Collect Through | Total Episodes | Done |
|---|---|---:|---|
| Minimum | `episode_049` for each block | 150 | [x] |
| Pilot | `episode_089` for each block | 270 | [x] |
| Full | `episode_167` for each block | 504 | [ ] |

## Progress By Block

| Block | Stage 0 | Stage 1 | Stage 2 | Stage 3 | Stage 4 | Stage 5 | Total Done |
|---|---:|---:|---:|---:|---:|---:|---:|
| Dark blue | 10/10 | 40/40 | 40/40 | 0/45 | 0/20 | 0/13 | 0/168 |
| Light blue | 10/10 | 40/40 | 40/40 | 0/45 | 0/20 | 0/13 | 0/168 |
| Red | 10/10 | 40/40 | 40/40 | 0/45 | 0/20 | 0/13 | 0/168 |

## Active Session Notes

```text
Date:
Collector:
Blocks used:
Lighting/camera notes:
Issues:
```

