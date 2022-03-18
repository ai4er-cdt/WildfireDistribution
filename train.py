import os
import pytorch_lightning as pl
from pytorch_lightning.loggers import WandbLogger
from pytorch_lightning import Trainer
from src.datamodules import MODISJDLandcoverSimpleDataModule
# from torchgeo.trainers import SemanticSegmentationTask
from src.tasks import SemanticSegmentationTask # use this when overfitting/debuging 

from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint
from src.evaluation import LogPredictionsCallback

from torchgeo.datasets import BoundingBox


# use this for debugging outputs with a single sample
TEST_OVERFIT = [
    BoundingBox(
        minx=27.108280665817976,
        maxx=27.15499306059219,
        miny=51.56347697151736,
        maxy=51.61018936629158,
        mint=1543622399.999999,
        maxt=1543622399.999999),
]


def main():
    
    datamodule = MODISJDLandcoverSimpleDataModule(
        modis_root_dir="/gws/nopw/j04/bas_climate/projects/WildfireDistribution/modis_fire/test_fire/",
        landcover_root_dir="/gws/nopw/j04/bas_climate/projects/WildfireDistribution/Classified/",
        sentinel_root_dir="/gws/nopw/j04/bas_climate/projects/WildfireDistribution/cloudless/",
        patch_size=256,
        length=2048, #256, #8481,
        batch_size=16,
        num_workers=0,
        balance_samples=True,
        burn_prop=1.0,
    )
    
    model = SemanticSegmentationTask(
        segmentation_model="unet",
        encoder_name="resnet18",
        encoder_weights=None,
        in_channels=4,
        num_classes=2,
        num_filters=32,
        loss="ce",
        ignore_zeros=True, 
        learning_rate=0.0001,
        learning_rate_schedule_patience=5,
    )
    
    
    wandb_logger = WandbLogger(
        project="GTC",
        log_model="all",
        name="auto_lr_batch_16_len_2048_burn_prop_1.0",
        # name="test_logging",
        save_dir="/gws/nopw/j04/bas_climate/projects/WildfireDistribution/wandb/",
    )
    
    callbacks = [
        LogPredictionsCallback(),
        ModelCheckpoint(monitor="val_loss", mode="max"),
        ModelCheckpoint(monitor="train_Accuracy", mode="max"),
        ModelCheckpoint(monitor="val_Accuracy", mode="max"),
        EarlyStopping(monitor="val_loss", min_delta=0.00, patience=3,),
    ]
    
    trainer = Trainer(
        default_root_dir="experiments/",
        gpus=1,
        max_epochs=100,
        logger=wandb_logger,
        log_every_n_steps=50,
        callbacks=callbacks,
        precision=16,
        # fast_dev_run=5,
        auto_lr_find=True,
    )

    wandb_logger.watch(model)

    # this is used when automatically finding the learning rate
    trainer.tune(
        model, datamodule
    )
    trainer.fit(model, datamodule)


if __name__ == "__main__":
    
    _rasterio_best_practices = {
        "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
        "AWS_NO_SIGN_REQUEST": "YES",
        "GDAL_MAX_RAW_BLOCK_CACHE_SIZE": "200000000",
        "GDAL_SWATH_SIZE": "200000000",
        "VSI_CURL_CACHE_SIZE": "200000000",
    }
    os.environ.update(_rasterio_best_practices)


    # set random seed for reproducibility
    pl.seed_everything(12)

    # TRAIN
    main()
