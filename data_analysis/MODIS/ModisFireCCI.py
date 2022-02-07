import os
import re
import glob

import rioxarray as rxr
import xarray as xr
import numpy as np

import utils
import plotting



class PP_ModisFireCCI():
    """Abstract base class for the preprocessing of all MODIS Fire CCI Burned Area datasets. This class should
       not be called directly - instead use the subclass objects.

    `MODIS Fire_cci Burned Area Dataset: <https://geogra.uah.es/fire_cci/firecci51.php>`_
    This dataset was developed by ESA, utilising the MODIS satellite. The dataset contains
    information at both PIXEL (~250m) and GRID (0.25 degrees) resolutions. A variety of 
    useful information is contained within the datasets including Julian Day of burn, 
    confidence level of burn etc.
    For more information, see:
    * `User Guide
      <https://climate.esa.int/media/documents/Fire_cci_D4.2_PUG-MODIS_v1.0.pdf>`_
    """
    
    #: Root directory (in CEDA) where the MODIS files can be found.
    root = None
    
    #: Glob expression used to search for files.
    filename_glob = None
    
    #: Regular expression used to extract date from filename.
    filename_regex = "(?P<date>\d{6})\S{33}(?P<tile_number>\d).*"

    #: Date format string used to parse date from filename.
    date_format = "%Y%m"
    
    #: DataArray used to store the relevant MODIS data.
    data = None
    
    #: Binary flag signifying that data has been mapped to 0/1
    binary_flag = False
    
    
    def __init__(
        self,
        root: str,
    ) -> None:
        """Initialize a new Preprocessing instance.
        Args:
            root: root directory where dataset can be found
        Raises:
            FileNotFoundError: if no files are found in ``root``
        """
        
        # Set the root attribute to that passed into the constructor
        self.root = root
      

    def populate(self, shape_root, zero_remap=0):
        """Extracts the relevant data from the root directory, crops it to an area of interest and stores it 
           within the object using a DataArray stack with 'YYYYMM' as the index.
           
        Args:
            shape_root: shape file (.shp) path
            zero_remap: the new value that elements outside the spatial bounds (but not dropped from the output 
                        DataArray) are mapped to after the crop has occurred
           """
        
        # Populate a list of DataArrays using the seperate files
        dataArrays = []
        pathname = os.path.join(self.root, "**", self.filename_glob)
        
        # For each file found:
        for filepath in glob.iglob(pathname, recursive=True):

            # Read the data
            match = re.match(self.filename_regex, os.path.basename(filepath))
            data = rxr.open_rasterio(filepath)

            # Crop the data
            data = utils.crop_data_spatially(data, shape_root, zero_remap)

            # Write the cropped data to the object
            data = data.assign_coords(date=match.group("date"))
            dataArrays.append(data)
            
        # Finally concatenate the DataArrays and store the result in the object     
        self.data = xr.concat(dataArrays, dim='date')
         

    def export(self, target_dir):
        """Saves the data contained within the object to some target directory (raster .tif files).
        
        Args:
            target_dir: path of target directory for export
                        
        Raises:
            ValueError: if object has not been populated with data before this function is called
            CPLE_OpenFailedError: if target directory has not been created before calling this function
        """
        
        if self.data is None:
            raise ValueError("The data is = None. Try calling 'populate' to assign the object data before making this call.") 

            
        # For each DataArray, save the data as a raster .tif file  
        for dataArray in self.data:
            output_name = "PostProcessing_" + str(dataArray.date.values)+ "-" + self.filename_glob[1:]
            full_output_file = os.path.join(target_dir, output_name) 
            dataArray.rio.to_raster(full_output_file)
            

    def get_non_zero_proportion(self):
        """Returns the proportion of non-zero pixels contained within each DataArray as a dict.
        
        Returns:
            dict_proportions: date ('YYYYMM'): proportion of non_zero elements
                        
        Raises:
            ValueError: if object has not been populated with data before this function is called
        """
        
        if self.data is None:
            raise ValueError("The data is = None. Try calling 'populate' to assign the object data before making this call.") 

        
        # Setup the dict and get the total number of elements in each DataArray
        dict_proportions = {}
        total_count = int(self.data[0].count().values)
        
        # Write the proportion of non-zero elements to the output dict
        for dataArray in self.data:
            data_mask = xr.where(dataArray>0, 1, 0)
            non_zero_count = int(data_mask.sum().values)
            dict_proportions[str(dataArray.date.values)] = non_zero_count/total_count
            
        return dict_proportions


    def plot_hist_non_zero_proportion(self, dict_proportions):
        """Plots the means/standard deviations of the proportion of non-zero pixels for each month.

        Args:
            dict_proportions: a dict of 'YYYYMM': proportions
                        
        Raises:
            ValueError: if object has not been populated with data before this function is called
        """
        
        if self.data is None:
            raise ValueError("The data is = None. Try calling 'populate' to assign the object data before making this call.") 

        # Call the corresponding function written in the plotting script
        plotting.monthly_histogram(dict_proportions)



class PP_ModisJD(PP_ModisFireCCI):
    """
    Preprocessing class for the burn day (in Julian Days) that a burned area is first seen on.
    
    Possible values (mask not image): 
        -2 = pixel not of burnable type e.g. water, urban areas or permanent snow/ice.
        -1 = pixel not observed in the month (possible cloud cover etc)
         0  = pixel is not burned 
        [1,366] = Julian Day of first detection when the pixel is burned 
    """

    filename_glob = "*JD.tif" 
    
    
    def binarize(self):
        """Maps any data points which are greater than zero to 1.
        
        Raises:
            ValueError: if object has not been populated with data before this function is called
        """
        
        if self.data is None:
            raise ValueError("The data is = None. Try calling 'populate' to assign the object data before making this call.") 
        
        # If data is more than 0, replace it with 1, otherwise keep original value
        self.data = xr.where(self.data > 0, 1, self.data)
        
        # Set the flag used for plotting functions
        self.binary_flag = True
    
    
    def plot(self, date, shape_root = None):
        """Plots the data corresponding to the date chosen.

        Args: 
            date: date in the format "YYYYMM" that is selected for plotting
            shape_root: shape file (.shp) path of training area (optional)
        
        Raises:
            ValueError: if object has not been populated with data before this function is called
        """
        
        if self.data is None:
            raise ValueError("The data is = None. Try calling 'populate' to assign the object data before making this call.") 
        
        
        # Call the corresponding function written in the plotting script
        plotting.selected_months_JD(self, date, shape_root)
    



class PP_ModisCL(PP_ModisFireCCI):
    """
    Preprocessing class for the confidence level (%) that a burn has occurred in an area.
    
    Possible values (mask not image): 
        0 = pixel is not observed within month or is not burnable.
        1-100 = expression of certainty in burn classification.
        
    """

    filename_glob = "*CL.tif" 
    
    
    def plot(self, date, shape_root = None):   
        """Plots the data corresponding to the date chosen.

        Args: 
            date: date in the format "YYYYMM" that is selected for plotting
            shape_root: shape file (.shp) path of training area (optional)
        
        Raises:
            ValueError: if object has not been populated with data before this function is called
        """
        
        if self.data is None:
            raise ValueError("The data is = None. Try calling 'populate' to assign the object data before making this call.") 
        
        # Call the corresponding function written in the plotting script
        plotting.selected_months_CL(self, date, shape_root)

