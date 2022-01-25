import torch
from torchgeo.datasets.geo import RasterDataset
from typing import Any, Callable, Dict, Optional

from rasterio.crs import CRS


# info on ERA5 projection here:
#
# https://gis.stackexchange.com/questions/379877/convert-era5-data-to-wgs84
#
# https://confluence.ecmwf.int/display/CKB/ERA5%3A+What+is+the+spatial+reference
#
# note: some ERA5 data has 0 to 360 longitude, this should be changed to
# -180 to 180 if that's the case


class ERA5Land(RasterDataset):
  """Abstract class for all ERA5 Land datasets.
  """

class ERA5SnowC(ERA5Land):
  filename_glob = "era5_snowc_*.tiff"
  filename_regex = "\S{11}(?P<date>\d{6})\S{7}"
  date_format = "%Y%m"

  def __init__(
        self,
        root: str = None,
        # crs: Optional[CRS] = None,
        crs: CRS = CRS.from_epsg(4326),
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


class ERA5SnowDepth(ERA5Land):
  filename_glob = "era5_sd_*.tiff"
  filename_regex = "\S{8}(?P<date>\d{6})\S{7}"
  date_format = "%Y%m"

  def __init__(
        self,
        root: str = None,
        # crs: Optional[CRS] = None,
        crs: CRS = CRS.from_epsg(4326),
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

class ERA5T2M(ERA5Land):
  filename_glob = "era5_t2m_*.tiff"
  filename_regex = "\S{9}(?P<date>\d{6})\S{7}"
  date_format = "%Y%m"

  def __init__(
        self,
        root: str = None,
        # crs: Optional[CRS] = None,
        crs: CRS = CRS.from_epsg(4326),
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

class ERA5SWVL1(ERA5Land):
  filename_glob = "era5_swvl1_*.tiff"
  filename_regex = "\S{11}(?P<date>\d{6})\S{7}"
  date_format = "%Y%m"

  def __init__(
        self,
        root: str = None,
        # crs: Optional[CRS] = None,
        crs: CRS = CRS.from_epsg(4326),
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
