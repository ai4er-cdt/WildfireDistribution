# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Landsat datasets."""

import abc
from torchgeo.datasets.geo import Landsat
from typing import Any, Callable, Dict, List, Optional, Sequence

from rasterio.crs import CRS

class Landsat7(Landsat):
    """Landsat 7 Enhanced Thematic Mapper Plus (ETM+)."""

    filename_glob = "LE07_*B3.TIF"

    all_bands = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"]
    rgb_bands = ["B3", "B2", "B1"]
