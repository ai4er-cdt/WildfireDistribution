import os
import yaml
from docopt import docopt
import pytorch_lightning as pl
from pytorch_lightning.loggers import WandbLogger
from pytorch_lightning import Trainer
from src.datamodules import MODISJDLandcoverSimpleDataModule

# from torchgeo.trainers import SemanticSegmentationTask
from src.tasks import SemanticSegmentationTask  # use this when overfitting/debuging
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint
from src.evaluation import LogPredictionsCallback

from torchgeo.datasets import BoundingBox


# use this for debugging outputs with a single sample
TEST_OVERFIT = [
    BoundingBox(
        minx=27.108280665817976,
        maxx=27.15499306059219,
        miny=51.56347697151736,
        maxy=51.61018936629158,
        mint=1543622399.999999,
        maxt=1543622399.999999,
    ),
]


def main(conf):

    datamodule = MODISJDLandcoverSimpleDataModule(
        modis_root_dir=conf["datamodule"]["modis_root_dir"],
        landcover_root_dir=conf["datamodule"]["landcover_root_dir"],
        sentinel_root_dir=conf["datamodule"]["sentinel_root_dir"],
        patch_size=conf["datamodule"]["patch_size"],
        length=conf["datamodule"]["length"],
        batch_size=conf["datamodule"]["batch_size"],
        num_workers=conf["datamodule"]["num_workers"],
        balance_samples=conf["datamodule"]["balance_samples"],
    )

    model = SemanticSegmentationTask(
        segmentation_model=conf["module"]["segmentation_model"],
        encoder_name=conf["module"]["encoder_name"],
        encoder_weights=conf["module"]["encoder_weights"],
        in_channels=conf["module"]["in_channels"],
        num_classes=conf["module"]["num_classes"],
        num_filters=conf["module"]["num_filters"],
        loss=conf["module"]["loss"],
        ignore_zeros=conf["module"]["ignore_zeros"],
        learning_rate=conf["module"]["learning_rate"],
        learning_rate_schedule_patience=conf["module"][
            "learning_rate_schedule_patience"
        ],
    )

    wandb_logger = WandbLogger(
        project="GTC",
        log_model="all",
        name="auto_lr_batch_16_len_2048_burn_prop_1.0",
        save_dir="/gws/nopw/j04/bas_climate/projects/WildfireDistribution/wandb/",
    )

    callbacks = [
        LogPredictionsCallback(),
        ModelCheckpoint(monitor="val_loss", mode="max"),
        ModelCheckpoint(monitor="train_Accuracy", mode="max"),
        ModelCheckpoint(monitor="val_Accuracy", mode="max"),
        EarlyStopping(
            monitor="val_loss",
            min_delta=0.00,
            patience=3,
        ),
    ]

    trainer = Trainer(
        logger=wandb_logger,
        callbacks=callbacks,
        default_root_dir=conf["trainer"]["default_root_dir"],
        gpus=conf["trainer"]["gpus"],
        max_epochs=conf["trainer"]["max_epochs"],
        log_every_n_steps=conf["trainer"]["log_every_n_steps"],
        precision=conf["trainer"]["precision"],
        auto_lr_find=conf["trainer"]["auto_lr_find"],
    )

    wandb_logger.watch(model)

    if conf["trainer"]["auto_lr_find"]:
        trainer.tune(model, datamodule)

    trainer.fit(model, datamodule)


if __name__ == "__main__":

    # Read input args
    args = docopt(__doc__)

    # Load config file
    with open(args["--cfg"], "r") as f:
        cfg = yaml.safe_load(f)

    # set random seed for reproducibility
    pl.seed_everything(12)

    # TRAIN
    main(cfg)
