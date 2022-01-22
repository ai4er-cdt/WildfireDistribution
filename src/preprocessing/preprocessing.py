import ModisFireCCI as MF
from datetime import datetime

# Start the timer
startTime = datetime.now()
 
#: Variable paths (TODO: to be read from another file eventually)
raw_data_path = "/home/users/hrac2/MODIS/"
shape_path = "/home/users/hrac2/WildfireDistribution/src/data/ShapeFiles/"
post_processed_path = "/home/users/hrac2/WildfireDistribution/src/data/PostProcessed/MODIS/"

# Create data stack
print("Populating...")
fire_data = MF.PP_ModisJD(raw_data_path) 
fire_data.populate()
print("Populated.")

# Crop data stack
print("Cropping...")
fire_data.crop(shape_path+'whole_map.shp', -2)
print("Cropped.")

#: Plot monthly hist 
# Create dict
fire_proportions = fire_data.get_non_zero_proportion()

# Plot the data 
print('Plotting data...')
fire_data.plot_hist_non_zero_proportion()

# Alert user of task completion
print('Finished (', datetime.now() - startTime, ')')
