"""
OpenPI config snippet for xArm LeRobot fine-tuning.

Copy the class and config entry into Physical-Intelligence/openpi's
src/openpi/training/config.py, then replace `your_hf_username/xarm_pick_place`
with the repo id produced by scripts/prepare_openpi_lerobot.py.
"""

# Add these imports in openpi/src/openpi/training/config.py if they are not present:
# import dataclasses
# import tyro
# import openpi.transforms as _transforms
# import openpi.models.model as _model


XARM_CONFIG_SNIPPET = r'''
@dataclasses.dataclass(frozen=True)
class LeRobotXArmDataConfig(DataConfigFactory):
    """Data config for this repository's xArm LeRobot dataset."""

    default_prompt: str | None = None

    @override
    def create(self, assets_dirs: pathlib.Path, model_config: _model.BaseModelConfig) -> DataConfig:
        repack_transform = _transforms.Group(
            inputs=[
                _transforms.RepackTransform(
                    {
                        "observation/image": "image",
                        "observation/wrist_image": "wrist_image",
                        "observation/state": "state",
                        "actions": "actions",
                        "prompt": "prompt",
                    }
                )
            ]
        )

        data_transforms = _transforms.Group()
        model_transforms = ModelTransformFactory(default_prompt=self.default_prompt)(model_config)

        return dataclasses.replace(
            self.create_base_config(assets_dirs, model_config),
            repack_transforms=repack_transform,
            data_transforms=data_transforms,
            model_transforms=model_transforms,
            action_sequence_keys=("actions",),
        )


# Add this TrainConfig entry to _CONFIGS:
TrainConfig(
    name="pi05_xarm",
    model=pi0_config.Pi0Config(model_type=ModelType.PI05, action_dim=7, action_horizon=10),
    data=LeRobotXArmDataConfig(repo_id="your_hf_username/xarm_pick_place"),
    weight_loader=weight_loaders.CheckpointWeightLoader("gs://openpi-assets/checkpoints/pi05_base/params"),
    batch_size=16,
    num_train_steps=30_000,
    save_interval=1_000,
)
'''


if __name__ == "__main__":
    print(XARM_CONFIG_SNIPPET)
