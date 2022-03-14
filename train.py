import os
import pytorch_lightning as pl
from pytorch_lightning.loggers import WandbLogger
from pytorch_lightning import Trainer
from src.datamodules import MODISJDLandcoverSimpleDataModule
from src.tasks import BinarySemanticSegmentationTask

from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.callbacks import Callback


def main():

    datamodule = MODISJDLandcoverSimpleDataModule(
        modis_root_dir="data/modis/2017/",
        landcover_root_dir="data/landcover/",
        patch_size=256,
        length=512,
        batch_size=64,
        num_workers=0,
        one_hot_encode=False,
        balance_samples=True,
        burn_prop=1.0,
    )

    # ignore_zeros=True corresponds to ignoring the background class
    # in metrics evaluation
    model = BinarySemanticSegmentationTask(
        segmentation_model="unet",
        encoder_name="resnet18",
        encoder_weights="imagenet",
        in_channels=1,
        num_filters=64,
        num_classes=2,
        loss="jaccard",
        learning_rate=0.1,
        ignore_zeros=True,
        learning_rate_schedule_patience=5,
    )

    wandb_logger = WandbLogger(
        project="Wildfires",
        log_model="all",
        name="all_fire_training_ignore_background_in_jaccardIndex",
    )

    callbacks = [
        ModelCheckpoint(monitor="train_Accuracy", mode="max"),
        ModelCheckpoint(monitor="val_Accuracy", mode="max"),
        ModelCheckpoint(monitor="val_loss", mode="max"),
    ]

    trainer = Trainer(
        gpus=1,
        min_epochs=1,
        max_epochs=10,
        logger=wandb_logger,
        log_every_n_steps=2,
        callbacks=callbacks,
        auto_lr_find=True,
    )

    wandb_logger.watch(model)

    trainer.tune(
        model, datamodule
    )  # this is used when automatically finding the learning rate
    trainer.fit(model, datamodule)


if __name__ == "__main__":

    # set random seed for reproducibility
    pl.seed_everything(42)

    # TRAIN
    main()
