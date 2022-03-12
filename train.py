# from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint
import os
# from argparse import ArgumentParser
# from pytorch_lightning.callbacks import Callback
from omegaconf import DictConfig, OmegaConf
import pytorch_lightning as pl
from pytorch_lightning.loggers import WandbLogger
# from torchgeo.trainers import SemanticSegmentationTask
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
        grid_sampler=False,
    )

    
    model = BinarySemanticSegmentationTask(
     segmentation_model="unet",
     encoder_name="resnet18",
     encoder_weights="imagenet",
     in_channels=1,
     num_filters=64,
     num_classes=2, 
     loss="jaccard",
     learning_rate=0.1,
     ignore_zeros=None,
     learning_rate_schedule_patience=5,
    )
    
    wandb_logger = WandbLogger(project="Wildfires", log_model="all", name="jaccard_balanced_sampler_w_callbacks")
    
    
    callbacks = [ModelCheckpoint(monitor="train_Accuracy", mode="max"),
                        ModelCheckpoint(monitor='val_Accuracy', mode='max'),
                        ModelCheckpoint(monitor="val_loss", mode="max")]
    
    
    trainer = Trainer(
        gpus=1, min_epochs=1, max_epochs=20,
        logger=wandb_logger, 
        log_every_n_steps=2,
        callbacks=callbacks,
        # auto_lr_find=True,
    )
    
    wandb_logger.watch(model)

    # load args from the config file
    
#     datamodule_args = cast(
#         Dict[str, Any], OmegaConf.to_object(conf.datamodule)
#     )    
#     datamodule = MODISJDLandcoverSimpleDataModule(**datamodule_args)

#     task_args = cast(Dict[str, Any], OmegaConf.to_object(conf.module))
#     model = SemanticSegmentationTask(**task_args)
    
#     checkpoint_callback = ModelCheckpoint(
#         monitor="val_loss", dirpath=experiment_dir, save_top_k=1, save_last=True
#     )
#     early_stopping_callback = EarlyStopping(
#         monitor="val_loss", min_delta=0.00, patience=18
#     )

#     trainer_args = cast(Dict[str, Any], OmegaConf.to_object(conf.trainer))

#     trainer_args["callbacks"] = [checkpoint_callback, early_stopping_callback]
#     trainer_args["logger"] = wandb_logger
#     trainer_args["default_root_dir"] = experiment_dir
#     trainer = pl.Trainer(**trainer_args)
    
    # if trainer_args.get("auto_lr_find"):
        # trainer.tune(model=model, datamodule=datamodule)
    # trainer.tune(model=model, datamodule=datamodule)
    trainer.fit(model, datamodule)


if __name__ == "__main__":
    # root_dir = os.path.dirname(os.path.realpath(__file__))
    # parser = ArgumentParser(add_help=False)

    # add PROGRAM level args
    # parser.add_argument("--conda_env", type=str, default="torchgeo")
    #     parser.add_argument("--notification_email", type=str, default="ss2536@cam.ac.uk")

    #     # add all the available trainer options to argparse
    #     # ie: now --gpus --num_nodes ... --fast_dev_run all work in the cli
    #     parser = Trainer.add_argparse_args(parser)

    #     hyperparams = parser.parse_args()

    # set random seed for reproducibility
    pl.seed_everything(42)
    
    # TRAIN
    main()
