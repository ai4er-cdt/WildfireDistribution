#!/usr/bin/env python
# coding: utf-8

# # Download the datasets needed for Wildfire Classification
# 
# ## MODIS Burned Area and Sentinel 2 for the Polesia Region 
# 
# ### Data to be downloaded:
# - MODIS Burned area product for years 2000-2020. This method will pull from Jasmin storage, and unzip files to location specified in modis output dir 
# - 3 bands of Sentinel 2 data: B3, B8 and B11, rolled up to monthly level and normalised to within 0-1. This method will download years 2017-2020. Each band downloads to seperate file. The Polesia region is split into 87 tiles to enable download. 
# 
# 
# ### Requirements:
# - Create environment using the data_envs.yml file 
# - Authenticate Earth enginge account in this environemnt - https://developers.google.com/earth-engine/guides/python_install
# - This script is designed to be run on JASMIN HPC - the Sentinel portion will work locally but the MODIS unzip will not. Modis data can also be accessed freely via the CEDA archive. 
# 
# 

# In[ ]:


from .utils import unzip_all_modis_fire_files, pull_monthly_cloudless_sentinel, clean_sentinel_folder


# In[ ]:


#Define the directory 

modis_output_dir = '/home/users/graceebc/Test/MODIS/'
sentinel_output_dir = '/home/users/graceebc/Test/Sentinel_cloudless/'
bad_sentinel_dir = '/home/users/graceebc/Test/missing_bands'


# In[ ]:


#Download all the files 
if __name__ == '__main__':
    print('Creating the directories')
    if os.path.isdir(modis_output_dir) is False:
        os.mkdir(outdir)
    if os.path.isdir(sentinel_output_dir) is False:
        os.mkdir(outdir)
        
    print('Starting Modis unzip')    
    unzip_all_modis_fire_files(modis_output_dir)
    print('Modis data all unzipped')
    
    years_sentinel = [2017, 2018, 2019, 2020]
    
    print('Starting to download Sentinel data')
    for y in years_sentinel:
        pull_monthly_cloudless_sentinel(y, sentinel_output_dir)
        print('Sentinel data downloaded!')
    
    print('Clean up Sentinel folder')
    clean_sentinel_folder(sentinel_output_dir, bad_sentinel_dir)
    
    print('Clean data downloaded!')

