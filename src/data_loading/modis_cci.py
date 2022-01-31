import torch
from torchgeo.datasets.geo import RasterDataset
from typing import Any, Callable, Dict, Optional

from rasterio.crs import CRS

# import matplotlib.pyplot as plt


class MODIS_CCI(RasterDataset):
    """Abstract class for all MODIS CCI datasets."""


class MODIS_JD(MODIS_CCI):
    filename_glob = "*JD.tif"
    filename_regex = "(?P<date>\d{6})\S{33}(?P<tile_number>\d).*"
    date_format = "%Y%m"
    # is_image = False
    all_bands = ["Julian Day"]

    def __init__(
        self,
        root: str = None,
        crs: Optional[CRS] = None,
        res: Optional[float] = None,
        transforms: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
        cache: bool = True,
    ) -> None:
        """Initialize a new Dataset instance.

        Args:
            root: root directory where dataset can be found
            crs: :term:`coordinate reference system (CRS)` to warp to
                (defaults to the CRS of the first file found)
            res: resolution of the dataset in units of CRS
                (defaults to the resolution of the first file found)
            transforms: a function/transform that takes an input sample
                and returns a transformed version
            cache: if True, cache file handle to speed up repeated sampling
        Raises:
            FileNotFoundError: if no files are found in ``root``
        """

        super().__init__(root, crs, res, transforms, cache)
