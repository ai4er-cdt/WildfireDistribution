import torch
from torchgeo.datasets.geo import RasterDataset
from typing import Any, Callable, Dict, Optional

from rasterio.crs import CRS


class LandcoverSimple(RasterDataset):
    filename_glob = "*Simple.tif"

    # this is not true strictly speaking, but keeping like this for now
    # until we figure out how to handle this/how it fails
    is_image = True

    # Possible landcover classifications and corresponding values
    classifications = {
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


class LandcoverComplex(RasterDataset):
    filename_glob = "*Complex.tif"
    is_image = False

    # Possible landcover classifications and corresponding values
    classifications = {
        "pine, birch, wide leafed coniferous forests": 1,
        "spruce forests": 2,
        "oak, deciduous forests, small leaved deciduous forests": 3,
        "alder forests": 4,
        "birch forests": 5,
        "deciduous indigenous swamp forests": 6,
        "meadows": 7,
        "agriculture (fields and hay pasture)": 8,
        "raised bog": 9,
        "fen and transitional mire": 10,
        "forest cuttings and clearings, cleared ground outside of urban areas": 11,
        "water": 12,
        "urban, cleared ground in urban areas, buildings, and tarmac": 13,
    }

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
