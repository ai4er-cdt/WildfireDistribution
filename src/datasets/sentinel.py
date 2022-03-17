from typing import Any, Callable, Dict, Optional, Sequence
from rasterio.crs import CRS


from torchgeo.datasets import Sentinel2

class Sentinel2(Sentinel2):
    """
    Custom Sentinel 2 Class
     - works with new name and date format for monthly composite files. 
     - Inherits properties from Raster Dataset  
    
    Note: Sampling will assume that all bands are present if the B03 is present: See the RasterDataset docs for more info
    """
    filename_glob = '*B03.tif'
    filename_regex = '^(?P<date>\\d{6})\\S{4}(?P<band>B[018][\\dA]).tif$'
    date_format = '%Y%m'
    all_bands = ['B03', 'B08', 'B11']
