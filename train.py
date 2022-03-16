import os
import pytorch_lightning as pl
from pytorch_lightning.loggers import WandbLogger
from pytorch_lightning import Trainer
from src.datamodules import MODISJDLandcoverSimpleDataModule
from src.tasks import BinarySemanticSegmentationTask

from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.callbacks import Callback
from src.evaluation import LogPredictionsCallback

from torchgeo.datasets import BoundingBox


TEST_OVERFIT = [
    BoundingBox(
        minx=26.602169834745037,
        maxx=26.648882229519252,
        miny=50.72804375728621,
        maxy=50.77475615206043,
        mint=1472687999.999999,
        maxt=1472687999.999999,
    ),
    BoundingBox(
        minx=26.32387175972481,
        maxx=26.370584154499024,
        miny=51.797218608445256,
        maxy=51.843931003219474,
        mint=1456790399.999999,
        maxt=1456790399.999999,
    ),
    BoundingBox(
        minx=30.285262499635078,
        maxx=30.331974894409292,
        miny=50.579821735406476,
        maxy=50.626534130180694,
        mint=1443657599.999999,
        maxt=1443657599.999999,
    ),
]


def main():

    datamodule = MODISJDLandcoverSimpleDataModule(
        modis_root_dir="data/modis/",
        landcover_root_dir="data/landcover/",
        patch_size=256,
        length=512,
        batch_size=1,
        num_workers=0,
        one_hot_encode=False,
        balance_samples=False,
        # burn_prop=1.0,
        test_roi=TEST_OVERFIT[0],
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
        loss="tversky",
        tversky_alpha=0.1,
        tversky_beta=0.9,
        tversky_gamma=1.0,
        learning_rate=0.001,
        ignore_zeros=True,
        learning_rate_schedule_patience=None,
    )

    wandb_logger = WandbLogger(
        project="Wildfires",
        log_model="all",
        name="overfitting_one_tversky_alpha_0.9",
    )

    callbacks = [
        LogPredictionsCallback(),
        ModelCheckpoint(monitor="train_Accuracy", mode="max"),
        ModelCheckpoint(monitor="val_Accuracy", mode="max"),
        ModelCheckpoint(monitor="val_loss", mode="max"),
    ]

    trainer = Trainer(
        gpus=1,
        min_epochs=1,
        max_epochs=50,
        logger=wandb_logger,
        log_every_n_steps=2,
        callbacks=callbacks,
        # auto_lr_find=True,
    )

    # trainer = Trainer(gpus=1, fast_dev_run=2)

    wandb_logger.watch(model)

    # this is used when automatically finding the learning rate
    # trainer.tune(
    #     model, datamodule
    # )
    trainer.fit(model, datamodule)


if __name__ == "__main__":

    # set random seed for reproducibility
    pl.seed_everything(0)

    # TRAIN
    main()
