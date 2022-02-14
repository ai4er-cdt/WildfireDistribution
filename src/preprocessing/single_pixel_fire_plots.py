import ModisFireCCI as MF
import os
import glob
from datetime import datetime

# Start the timer
startTime = datetime.now()

#: Variable paths (TODO: to be read from another file eventually)
raw_data_path = "/home/users/graceebc/MODIS_annual_half/"
glob_path = "/home/users/graceebc/MODIS/*JD.tif"
shape_path = "/home/users/graceebc/WildfireDistribution/src/data/ShapeFiles/"
post_processed_path = (
    "/home/users/graceebc/WildfireDistribution/src/data/PostProcessed/MODIS/"
)

# Due to memory limitations, need to consider years one by one
# fire_proportions = {}
fire_prop_excl_single = {}

for year in range(2001, 2021):

    print("Starting ", year, "...")

    # Create data stack
    print("Populating and cropping...")
    folders = ["/1sthalf/", "/2ndhalf/"]

    for f in folders:
        print("Starting " + str(f))

        fire_data = MF.PP_ModisJD(raw_data_path + str(year) + f)
        fire_data.populate(shape_path + "whole_map.shp", -2)
        print("Populated and cropped.")

        # Create dict
        print("Creating Dictionary..")
        fire_prop_excl_single_annual = (
            fire_data.get_burn_area_excluding_single_pixel_fire()
        )

        # Add annual dict to overall dict
        print("Updating Dictionary..")
        fire_prop_excl_single.update(fire_prop_excl_single_annual)

    print("Finished", year)

# Plot the overall histogram
print("Plotting data...")

# fire_data.plot_hist_non_zero_proportion(fire_proportions)
fire_data.plot_hist_for_given_proportion(
    dict_proportions=fire_prop_excl_single,
    proportion_name="Burned Proportion Excluding Single Pixel Fires",
    plot_output_path=post_processed_path,
)

# Alert user of task completion
print("Finished (", datetime.now() - startTime, ")")
