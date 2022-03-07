# from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint
import os

# from argparse import ArgumentParser

# from pytorch_lightning.callbacks import Callback
from omegaconf import DictConfig, OmegaConf
import pytorch_lightning as pl
from pytorch_lightning.loggers import WandbLogger
from torchgeo.trainers import SemanticSegmentationTask
from pytorch_lightning import Trainer
from src.datamodules import MODISJDLandcoverSimpleDataModule


def main():

    datamodule = MODISJDLandcoverSimpleDataModule(
        modis_root_dir="data/MODIS/*/",
        landcover_root_dir="data/Classified/",
        batch_size=1,
        num_workers=1,
        # constrained=True,
    )
    
    model = SemanticSegmentationTask(
        segmentation_model="fcn",
        in_channels=10,
        num_classes=2,
        num_filters=5,
        loss="ce",
        ignore_zeros=False,
        learning_rate=0.1,
        learning_rate_schedule_patience=5,
    )
    
    # wandb_logger = WandbLogger(project="Wildfires", log_model="all")
    
    # fast dev mode
    trainer = Trainer(gpus=1, 
                      fast_dev_run=True,)
    
    # trainer = Trainer(
    #     gpus=1, logger=wandb_logger, min_epochs=1, max_epochs=5,
    #     auto_lr_find=True,
    # )
    
    # wandb_logger.watch(model)

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
