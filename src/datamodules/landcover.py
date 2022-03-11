from typing import Any, Dict, Optional

from ..data_loading import LandcoverSimple, MODIS_JD, Sentinel2, Landsat7
from ..samplers import ConstrainedRandomBatchGeoSampler

import torch
import pytorch_lightning as pl
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchgeo.samplers.batch import RandomBatchGeoSampler
from torchgeo.samplers.single import GridGeoSampler
from torchgeo.datasets import stack_samples
from torchgeo.samplers.constants import Units


class MODISJDLandcoverSimpleDataModule(pl.LightningDataModule):

    # TODO: tune these hyperparams
    # stride is not trivial to choose
    # patch_size - stride should approx equal
    # the receptive field of a CNN

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
        sentinel_root_dir: Optional[str] = None,
        landsat_root_dir: Optional[str]=None,
        batch_size: int = 64,
        length: int = 256,
        num_workers: int = 0,
        patch_size: int = 256,  # dav version
        # patch_size: int = 0.0459937425469195,  # stable version
        one_hot_encode: bool = False,
        balance_samples: bool = False,  # whether or not to constrain the sampler
        burn_prop: float = 0.5,
        grid_sampler: bool = False,
        units: Units = Units.PIXELS,
        **kwargs: Any,
    ) -> None:
        """Initialize a LightningDataModule for MODIS and Landcover based DataLoaders.

        Args:
            modis_root_dir: directory containing MODIS data
            landcover_root_dir: directory containing (Polesia) landcover data
            sentinel_root_dir: directory of sentinel 2 band data
            landast_root_dir: directory of landsat 7 data
            batch_size: number of samples in batch
            num_workers:
            patch_size:
            one_hot_encode: set True to one hot encode landcover classes
            balance_samples: set True to get more samples with fires in training
            burn_prop: the proportion of burned samples to take per batch
            grid_sampler: set True to use a grid sampler for val/test
            units: whether to use pixels or CRS units for sizes

        """
        super().__init__()  # type: ignore[no-untyped-call]
        self.modis_root_dir = modis_root_dir
        self.landcover_root_dir = landcover_root_dir
        self.sentinel_root_dir = sentinel_root_dir
        self.landsat_root_dir = landsat_root_dir
        self.batch_size = batch_size
        self.length = length
        self.num_workers = num_workers
        self.patch_size = patch_size
        self.stride = patch_size - 1
        self.one_hot_encode = one_hot_encode
        self.balance_samples = balance_samples
        self.burn_prop = burn_prop
        self.grid_sampler = grid_sampler
        self.units = units

    def modis_transforms(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        # Binarize the samples
        sample["mask"] = torch.where(
            sample["mask"] > 0,
            torch.ones(sample["mask"].shape, dtype=torch.int16),  # torchgeo dev req
            # torch.ones(sample["mask"].shape, dtype=torch.int32),
            sample["mask"],
        )
        sample["mask"] = torch.where(
            sample["mask"] < 0,
            torch.zeros(sample["mask"].shape, dtype=torch.int16),  # torchgeo dev req
            # torch.zeros(sample["mask"].shape, dtype=torch.int32),
            sample["mask"],
        )

        sample_ = {"mask": sample["mask"].long().squeeze()}

        return sample_

    def landcover_transforms(
        self,
        sample: Dict[str, Any],
    ) -> Dict[str, Any]:

        if self.one_hot_encode:

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

    def get_sample(
        self,
        sample: Dict[str, Any],
    ) -> Dict[str, Any]:

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

        self.dataset = landcover & modis

        if self.sentinel_root_dir is not None:
            sentinel = Sentinel2(
                self.sentinel_root_dir,
                landcover.crs,
                landcover.res,
                bands=["B03", "B04", "B08"],
                transforms = self.get_sample,
            )
            self.dataset = self.dataset & sentinel

        if self.landsat_root_dir is not None:
            landsat = Landsat7(
                self.landsat_root_dir,
                landcover.crs,
                landcover.res,
                bands=["B2", "B3", "B4", "B5"],
                transforms = self.get_sample,
            )
            self.dataset = self.dataset & landsat

        roi = self.dataset.bounds

        if self.balance_samples:
            print("Using a constrained sampler to get more samples with fires.")
            self.train_sampler = ConstrainedRandomBatchGeoSampler(
                dataset=self.dataset,
                size=self.patch_size,
                batch_size=self.batch_size,
                length=self.length,
                burn_prop=self.burn_prop,
                roi=roi,
                units=self.units,
            )

        else:
            self.train_sampler = RandomBatchGeoSampler(
                self.dataset, self.patch_size, self.batch_size, self.length, roi
            )
            
        if self.grid_sampler:
            # TODO: we probably want to change the ROI's to some consistent sub-area rather than the whole Polesia region!
            self.val_sampler = GridGeoSampler(
                self.dataset, self.patch_size, self.stride, roi
            )
            self.test_sampler = GridGeoSampler(
                self.dataset, self.patch_size, self.stride, roi
            )
            
        else:
            self.val_sampler = RandomBatchGeoSampler(
                self.dataset, self.patch_size, self.batch_size, self.length, roi
            )
            self.test_sampler = RandomBatchGeoSampler(
                self.dataset, self.patch_size, self.batch_size, self.length, roi
            )

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
        if self.grid_sampler:
            return DataLoader(
                self.dataset,
                batch_size=self.batch_size,
                sampler=self.val_sampler,
                num_workers=self.num_workers,
                collate_fn=stack_samples,
                shuffle=False,
            )
        
        else:
            return DataLoader(
                self.dataset,
                batch_sampler=self.val_sampler,
                num_workers=self.num_workers,
                collate_fn=stack_samples,
            )

    def test_dataloader(self) -> DataLoader[Any]:
        """Return a DataLoader for testing.

        Returns:
            testing data loader
        """
        if self.grid_sampler:
            return DataLoader(
                self.dataset,
                batch_size=self.batch_size,
                sampler=self.test_sampler,
                num_workers=self.num_workers,
                collate_fn=stack_samples,
                shuffle=False,
            )
        
        else:
            return DataLoader(
                self.dataset,
                batch_sampler=self.test_sampler,
                num_workers=self.num_workers,
                collate_fn=stack_samples,
            )
