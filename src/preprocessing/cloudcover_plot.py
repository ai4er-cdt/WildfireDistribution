import ModisFireCCI as MF
import os
import glob
from datetime import datetime

# Start the timer
startTime = datetime.now()
 
#: Variable paths (TODO: to be read from another file eventually)
raw_data_path = '/home/users/graceebc/MODIS_annual_half/'
glob_path = '/home/users/graceebc/MODIS/*JD.tif'
shape_path = "/home/users/graceebc/WildfireDistribution/src/data/ShapeFiles/"
post_processed_path = "/home/users/graceebc/WildfireDistribution/src/data/PostProcessed/MODIS/"

# Due to memory limitations, need to consider years one by one
#fire_proportions = {}
cloud_dict= {} 

for year in range(2001,2021):
    
    print('Starting ',year ,'...')

    # Create data stack
    print("Populating and cropping...")
    folders = ['/1sthalf/', '/2ndhalf/']
    
    for f in folders:
        print('Starting ' + str(f) )
        
        fire_data = MF.PP_ModisJD(raw_data_path + str(year) + f) 
        fire_data.populate(shape_path +'whole_map.shp', -2)
        print("Populated and cropped.")

        # Create dict
        print('Creating Dictionary..')
        clouds = fire_data.get_proportion_of_cloudcover()

        # Add annual dict to overall dict
        print('Updating Dictionary..')
        cloud_dict.update(clouds)
    
    
    print('Finished',year)

# Plot the overall histogram  
print('Plotting data...')

#fire_data.plot_hist_non_zero_proportion(fire_proportions)
fire_data.plot_hist_for_given_proportion(dict_proportions = cloud_dict, proportion_name = 'Cloud Cover Proportion', plot_output_path = post_processed_path)

# Alert user of task completion
print('Finished (', datetime.now() - startTime, ')')
