from ..data_loading import MODIS_JD, LandcoverSimple, Landsat7

from typing import Any, Dict, Optional

import torch
import pytorch_lightning as pl
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchgeo.samplers.batch import RandomBatchGeoSampler
from torchgeo.samplers.single import GridGeoSampler
from torchgeo.datasets import stack_samples
from torchgeo.datasets import BoundingBox


class MODISJDLandcoverSimpleLandsatDataModule(pl.LightningDataModule):

    # TODO: tune these hyperparams
    # stride is not trivial to choose
    # patch_size - stride should approx equal
    # the receptive field of a CNN

    length = 100
    stride = 0.01

    simple_classes = {
        "invalid": 0,
        "deciduous forests": 1,
        "coniferous forests": 2,
        "swamp forests": 3,
        "meadows": 4,
        "agriculture": 5,
        "bogs and mires": 6,
        "clearings and cuttings": 7,
        "water": 8,
        "urban": 9,
    }

    def __init__(
        self,
        modis_root_dir: str,
        landcover_root_dir: str,
        landsat_root_dir: str,
        batch_size: int = 64,
        num_workers: int = 8,
        patch_size: int = 0.04,
        **kwargs: Any,
    ) -> None:
        """Initialize a LightningDataModule for MODIS, LANDSAT and Landcover based DataLoaders.

        Args:
            modis_root_dir: directory containing MODIS data
            landsat_root_dir: directory containing Landsat data
            landcover_root_dir: directory containing (Polesia) landcover data
            batch_size: number of samples in batch
            num_workers:
            patch_size:

        """
        super().__init__()  # type: ignore[no-untyped-call]
        self.modis_root_dir = modis_root_dir
        self.landcover_root_dir = landcover_root_dir
        self.landsat_root_dir = landsat_root_dir

        self.batch_size = batch_size
        self.num_workers = num_workers
        self.patch_size = patch_size

    def modis_transforms(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        # Binarize the samples
        sample["mask"] = torch.where(
            sample["mask"] > 0,
            torch.ones(sample["mask"].shape, dtype=torch.int32),
            sample["mask"],
        )
        sample["mask"] = torch.where(
            sample["mask"] < 0,
            torch.zeros(sample["mask"].shape, dtype=torch.int32),
            sample["mask"],
        )

        sample_ = {"mask": sample["mask"].long().squeeze()}

        return sample_

    def landcover_transforms(
        self,
        sample: Dict[str, Any],
    ) -> Dict[str, Any]:

        x_shape = sample["image"].shape

        input_mask = sample["image"]
        # Get the one-hot encodings, which are a tensor of: (batch_idx, lat, lon, band_idx)
        encodings = F.one_hot(
            input_mask.to(torch.int64), num_classes=len(self.simple_classes)
        )

        # not sure this is the right shape we want for the mask – here the batch idx is missing
        # but maybe that gets added in the dataloader
        new_mask = torch.zeros([len(self.simple_classes), x_shape[1], x_shape[2]])
        for band_idx in range(0, len(self.simple_classes)):
            new_mask[band_idx, :, :] = encodings[0, :, :, band_idx]

        # Write one-hot encodings to the output tensor
        # outputs = sample
        sample["image"] = new_mask.to(torch.int32)

        sample_ = {"image": sample["image"].float()}

        return sample_

    def setup(self, stage: Optional[str] = None) -> None:
        """Initialize the main ``Dataset`` objects.

        This method is called once per GPU per run.

        Args:
            stage: state to set up
        """
        # consider whether we should pass the res and crs from one to another here

        landcover = LandcoverSimple(
            self.landcover_root_dir,
            transforms=self.landcover_transforms,
        )

        modis = MODIS_JD(
            self.modis_root_dir,
            landcover.crs,
            landcover.res,
            transforms=self.modis_transforms,
        )

        landsat = Landsat7(self.landsat_root_dir, landcover.crs, landcover.res)

        self.dataset = landcover & modis & landsat

        roi = self.dataset.bounds

        self.train_sampler = RandomBatchGeoSampler(
            landcover, self.patch_size, self.batch_size, self.length, roi
        )
        self.val_sampler = GridGeoSampler(landcover, self.patch_size, self.stride, roi)
        self.test_sampler = GridGeoSampler(landcover, self.patch_size, self.stride, roi)

    def train_dataloader(self) -> DataLoader[Any]:
        """Return a DataLoader for training.

        Returns:
            training data loader
        """
        return DataLoader(
            self.dataset,
            batch_sampler=self.train_sampler,
            num_workers=self.num_workers,
            collate_fn=stack_samples,
        )

    def val_dataloader(self) -> DataLoader[Any]:
        """Return a DataLoader for validation.

        Returns:
            validation data loader
        """
        return DataLoader(
            self.dataset,
            batch_size=self.batch_size,
            sampler=self.val_sampler,
            num_workers=self.num_workers,
            collate_fn=stack_samples,
        )

    def test_dataloader(self) -> DataLoader[Any]:
        """Return a DataLoader for testing.

        Returns:
            testing data loader
        """
        return DataLoader(
            self.dataset,
            batch_size=self.batch_size,
            sampler=self.test_sampler,
            num_workers=self.num_workers,
            collate_fn=stack_samples,
        )
