import fiona
import numpy as np
import rioxarray as rxr
import math


def extract_vertices(shape_file_path):
    """Returns a numpy array of the lat/lons corresponding to the vertices of a polygon defined by a shape file.
    
    Keyword arguments:
    shape_file_path -- realtive path where the shp and shx files are located (both required)
    """
    
    # Extract the vertices using fiona
    with fiona.open(shape_file_path) as shape_data:
        vertices = shape_data[0]['geometry']['coordinates'][0]
        
    # Return them as a numpy array
    return np.array(vertices)
    

def crop_data_spatially(input_data, shape_file_path, zero_remap):
    """Crops input data to keep only the elements within the spatial bounds defined by the input shape file.
    
    Keyword arguments:
    input_data -- DataArray of input data and corresponding x/y (latitude/longitude) coordinates
    shape_file_path -- realtive path where the shp and shx files are located (both required)
    zero_remap -- the new value that elements outside the spatial bounds (but not dropped from the output DataArray)
                  are mapped to after the crop has occurred
    """
    
    # Check that zero_remap is the same type as the values in input_data
    first_element = input_data.item(tuple(np.zeros(len(input_data.shape), int)))
    try:
        if not ((isinstance(zero_remap, (int, np.integer)) and isinstance(first_element, (int, np.integer))) or
                 (isinstance(zero_remap, (float, np.float64)) and isinstance(first_element, (float, np.float64)))):
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


def calc_means(dated_quantities):
    """Calculates the means of the quantities stored in 'dated_quantities', for each month.

        Args:
            dated_quantities: date  ('YYYYMM'): quantity of interest

        Returns: 
            monthly_means:  month ('MM'): mean value
            year_counts:    month ('MM'): number of years considered 
    """

    # Create a dict, which for each month contains: sum of proportions, number of years considered 
    monthly_totals = {
        "01": {'sum': 0.0, 'count': 0},
        "02": {'sum': 0.0, 'count': 0},
        "03": {'sum': 0.0, 'count': 0},
        "04": {'sum': 0.0, 'count': 0},
        "05": {'sum': 0.0, 'count': 0},
        "06": {'sum': 0.0, 'count': 0},
        "07": {'sum': 0.0, 'count': 0},
        "08": {'sum': 0.0, 'count': 0},
        "09": {'sum': 0.0, 'count': 0},
        "10": {'sum': 0.0, 'count': 0},
        "11": {'sum': 0.0, 'count': 0},
        "12": {'sum': 0.0, 'count': 0},
    }

    # Update the monthly totals dict
    for date in dated_quantities:
        month_considered = date[4:]
        monthly_totals[month_considered]['sum'] += dated_quantities[date]
        monthly_totals[month_considered]['count'] += 1

    # Find the average non-zero proportion for months where we have at least one entry 
    monthly_means, year_counts = {}, {}
    for month in monthly_totals:
        if monthly_totals[month]['count'] != 0:
            monthly_means[month] = monthly_totals[month]['sum']/monthly_totals[month]['count']
            year_counts[month] = monthly_totals[month]['count']
        else:
            monthly_means[month] = 0.0
            year_counts[month] = 0

    return monthly_means, year_counts


def calc_std_devs(dated_quantities):
    """Calculates the standard deviation of the quantities stored in 'dated_quantities', for each month.

        Args:
            dated_quantities: date ('YYYYMM'): quantity of interest

        Returns: 
            monthly_std_devs: month ('MM'): standard deviation value
    """

    # Create a dict, which for each month contains: standard deviation 
    monthly_std_devs = {
        "01": 0.0,
        "02": 0.0,
        "03": 0.0,
        "04": 0.0,
        "05": 0.0,
        "06": 0.0,
        "07": 0.0,
        "08": 0.0,
        "09": 0.0,
        "10": 0.0,
        "11": 0.0,
        "12": 0.0,
    }

    # Get the mean and year count values 
    monthly_means, year_counts = calc_means(dated_quantities)

    # Sum the squared deviation of each proportion from the corresponding mean value
    for date in dated_quantities:
        month_considered = date[4:]
        monthly_std_devs[month_considered] += (dated_quantities[date]-monthly_means[month_considered])**2

    # Now divide each entry by the number of years considered, and take square root 
    for month in monthly_std_devs:
        if monthly_means[month_considered] != 0:
            monthly_std_devs[month] = math.sqrt(monthly_std_devs[month]/year_counts[month_considered])
        else:
            monthly_std_devs[month] = 0.0

    return monthly_std_devs