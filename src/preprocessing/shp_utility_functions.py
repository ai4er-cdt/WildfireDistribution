import geopandas as gpd
import numpy as np
import rioxarray as rxr

def extract_vertices(shape_file_path):
    """Returns a numpy array of the lat/lons corresponding to the vertices of a polygon defined by a shape file.
    
    Keyword arguments:
    shape_file_path -- realtive path where the shp and shx files are located (both required)
    """
    
    polygons_df = gpd.read_file(shape_file_path)
    vertices = list([list(coords) for coords in polygons_df.iloc[0]['geometry'].exterior.coords])
    return np.array(vertices)
    

def crop_data_spatially(input_data, shape_file_path, zero_remap = 0):
    """Crops input data to keep only the elements within the spatial bounds defined by the input shape file.
    
    Keyword arguments:
    input_data -- DataArray of input data and corresponding x/y (latitude/longitude) coordinates
    shape_file_path -- realtive path where the shp and shx files are located (both required)
    zero_remap -- the new value that elements outside the spatial bounds (but not dropped from the output DataArray)
                  are mapped to after the crop has occurred
    """
    
    # Check that zero_remap is the same type as the values in input_data
    try:
        if not ((isinstance(zero_remap, (int, np.integer)) and isinstance(input_data.values[0,0,0], (int, np.integer))) or
                 (isinstance(zero_remap, (float, np.float64)) and isinstance(input_data.values[0,0,0], (float, np.float64)))):
            raise TypeError('The zero_remap value provided must match the type of the input data:', type(zero_remap), type(input_data.values.dtype)) 
    
    except TypeError as error:
        print(error.args)
    
    
    # Extract the vertice's latitude/longitudes from the shape file
    vertices = extract_vertices(shape_file_path) 
    
    # Define a geometry object to define the polygon
    shape_geometry = [{'type': 'Polygon',
                       'coordinates': [vertices]}]
    
    # Crop the data using the latitude/longitudes and remap the new zero values 
    data_cropped = (input_data-zero_remap).rio.clip(shape_geometry, "epsg:4326") + zero_remap
    return data_cropped
    