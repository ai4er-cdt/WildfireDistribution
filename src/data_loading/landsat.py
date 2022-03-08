# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Landsat datasets."""

import abc
from typing import Any, Callable, Dict, List, Optional, Sequence

from rasterio.crs import CRS




class Landsat(RasterDataset, abc.ABC):
    """Abstract base class for all Landsat datasets.
    `Landsat <https://landsat.gsfc.nasa.gov/>`_ is a joint NASA/USGS program,
    providing the longest continuous space-based record of Earth's land in existence.
    If you use this dataset in your research, please cite it using the following format:
    * https://www.usgs.gov/centers/eros/data-citation
    
    For GTC, we will use the Landsat7 class with bands = ["B2", "B3", "B4", "B5"]
    """

    # https://www.usgs.gov/faqs/what-naming-convention-landsat-collections-level-1-scenes
    # https://www.usgs.gov/faqs/what-naming-convention-landsat-collection-2-level-1-and-level-2-scenes
    # filename_glob = "LE07*.TIF"
    filename_regex = r"""
        ^L
        (?P<sensor>[COTEM])
        (?P<satellite>\d{2})
        _(?P<processing_correction_level>[A-Z0-9]{4})
        _(?P<wrs_path>\d{3})
        (?P<wrs_row>\d{3})
        _(?P<date>\d{8})
        _(?P<processing_date>\d{8})
        _(?P<collection_number>\d{2})
        _(?P<collection_category>[A-Z0-9]{2})
        _(?P<band>B\d+)
        \..*$
    """

    # https://www.usgs.gov/faqs/what-are-band-designations-landsat-satellites
    all_bands: List[str] = []
    rgb_bands: List[str] = []

    separate_files = True
    stretch = True

    def __init__(
        self,
        root: str = "data",
        crs: Optional[CRS] = None,
        res: Optional[float] = None,
        bands: Sequence[str] = [],
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
            bands: bands to return (defaults to all bands)
            transforms: a function/transform that takes an input sample
                and returns a transformed version
            cache: if True, cache file handle to speed up repeated sampling
        Raises:
            FileNotFoundError: if no files are found in ``root``
        """
        self.bands = bands if bands else self.all_bands

        super().__init__(root, crs, res, transforms, cache)


class Landsat7(Landsat):
    """Landsat 7 Enhanced Thematic Mapper Plus (ETM+)."""

    filename_glob = "LE07_*B3.TIF"

    all_bands = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"]
    rgb_bands = ["B3", "B2", "B1"]