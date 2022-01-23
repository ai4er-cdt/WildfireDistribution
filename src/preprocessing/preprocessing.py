import ModisFireCCI as MF
from datetime import datetime

# Start the timer
startTime = datetime.now()
 
#: Variable paths (TODO: to be read from another file eventually)
raw_data_path = "/home/users/hrac2/MODIS/"
shape_path = "/home/users/hrac2/WildfireDistribution/src/data/ShapeFiles/"
post_processed_path = "/home/users/hrac2/WildfireDistribution/src/data/PostProcessed/MODIS/"

# Due to memory limitations, need to consider years one by one
fire_proportions = {}
for year in range(2001,2021):
    print('Starting',year,'...')

    # Create data stack
    print("Populating and cropping...")
    fire_data = MF.PP_ModisJD(raw_data_path+str(year)+'/') 
    fire_data.populate(shape_path+'whole_map.shp', -2)
    print("Populated and cropped.")

    # Create dict
    fire_proportions_annual = fire_data.get_non_zero_proportion()

    # Add annual dict to overall dict
    fire_proportions.update(fire_proportions_annual)
    print('Finished',year)

# Plot the overall histogram  
print('Plotting data...')
fire_data.plot_hist_non_zero_proportion(fire_proportions)

# Alert user of task completion
print('Finished (', datetime.now() - startTime, ')')
