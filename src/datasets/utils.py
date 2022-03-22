#!/usr/bin/env python
# coding: utf-8

#Utils file for sentinel and modis download 
import ee
import geemap
import datetime
import os
import numpy as np
import tarfile
import dateutil


import glob
import re
import shutil




def query_landsat(key_json, project_id, start, end, row, path, cloud=100.0):
    """
    Query Google BigQuery Landsat 7 data, returning the list of urls of scenes defined by the input parameters
    
    Inputs:
    key_json: Credentials file downloaded from Console
    project_id: id of projecgt set up within Console 
    start: start date of interest
    end: end dat of interest 
    row: defines bounding box of interest
    path: defines bounding box of interest 
    cloud: level of cloud cover acceptable 
    """
    credentials = service_account.Credentials.from_service_account_file(key_json)
    client = bigquery.Client(credentials=credentials, project=project_id)
    BASE_URL = "http://storage.googleapis.com/"
    query = client.query(
        """
                    SELECT * 
                    FROM `bigquery-public-data.cloud_storage_geo_index.landsat_index` 
                    where wrs_row = {r}
                    and spacecraft_id = 'LANDSAT_7'
                    and wrs_path = {p}
                    and DATE(sensing_time) >  CAST('{s}' AS DATE)
                    and DATE(sensing_time) < CAST('{e}' AS DATE)
        """.format(
            r=row, p=path, s=start, e=end
        )
    )
    results = query.result()
    df = results.to_dataframe()
    good_scenes = []
    for i, row in df.iterrows():
        # print (row['product_id'], '; cloud cover:', row['cloud_cover'])
        if float(row["cloud_cover"]) <= cloud:
            if float(row["cloud_cover"]) <= cloud:
                good_scenes.append(row["base_url"].replace("gs://", BASE_URL))
    return good_scenes


def download_landsat(outdir, bands, row_list, path_list, start, end, key_json, project_id, cloud):
    """
    Download the Landsat data into outdir, using Google Bigquery, for the bounding box, time period and bands defined.
    
    Inputs:
    outdir: directory for data to go 
    bands: bands to be downloaded from Landsat 
    row_list: list of rows, defines bounding box of interest
    path_list: list of paths, defines bounding box of interest
    key_json: Credentials file downloaded from Console
    project_id: id of projecgt set up within Console 
    start: start date of interest
    end: end dat of interest 
    cloud: level of cloud cover acceptable 
    
    """
    download_links = []
    scene_names = []

    for x in row_list:
        row = x
        for y in path_list:
            path = y
            scene_list = query_landsat(
                key_json, project_id, start, end, row, path, cloud
            )
            for scene in scene_list:
                scene_name = scene.split("/")[-1]

                band_paths = [scene_name + str(band) for band in bands]
                urls = [scene + "/" + str(band) for band in band_paths]
                download_links = [*download_links, *urls]
                scene_names = [*scene_names, *band_paths]

    for down_url, name in zip(download_links, scene_names):
        print("Starting file {}".format(name))
        file_name = str(outdir) + str(name)

        if os.path.exists(file_name) is False:
            r = requests.get(down_url, allow_redirects=True)
            try:
                open(file_name, "wb").write(r.content)
                print("File downloaded!")
            except:
                print("Download of {} failed".format(file_name))
        else:
            print("File already exists")
            
            
def get_s2_sr_cld_col(aoi, start_date, end_date, CLOUD_FILTER):
    """Function taken from https://developers.google.com/earth-engine/tutorials/community/sentinel-2-s2cloudless
    """
    # Import and filter S2 SR.
    s2_sr_col = (ee.ImageCollection('COPERNICUS/S2_SR')
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', CLOUD_FILTER)))

    # Import and filter s2cloudless.
    s2_cloudless_col = (ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
        .filterBounds(aoi)
        .filterDate(start_date, end_date))

    # Join the filtered s2cloudless collection to the SR collection by the 'system:index' property.
    return ee.ImageCollection(ee.Join.saveFirst('s2cloudless').apply(**{
        'primary': s2_sr_col,
        'secondary': s2_cloudless_col,
        'condition': ee.Filter.equals(**{
            'leftField': 'system:index',
            'rightField': 'system:index'
        })
    }))

def add_cloud_bands(img, CLD_PRB_THRESH):
    """
    Function taken from https://developers.google.com/earth-engine/tutorials/community/sentinel-2-s2cloudless
    """
    # Get s2cloudless image, subset the probability band.
    cld_prb = ee.Image(img.get('s2cloudless')).select('probability')

    # Condition s2cloudless by the probability threshold value.
    is_cloud = cld_prb.gt(CLD_PRB_THRESH).rename('clouds')

    # Add the cloud probability layer and cloud mask as image bands.
    return img.addBands(ee.Image([cld_prb, is_cloud]))


def add_shadow_bands(img, NIR_DRK_THRESH, CLD_PRJ_DIST):
        """Function taken from https://developers.google.com/earth-engine/tutorials/community/sentinel-2-s2cloudless
    """
    # Identify water pixels from the SCL band.
    not_water = img.select('SCL').neq(6)

    # Identify dark NIR pixels that are not water (potential cloud shadow pixels).
    SR_BAND_SCALE = 1e4
    dark_pixels = img.select('B8').lt(NIR_DRK_THRESH*SR_BAND_SCALE).multiply(not_water).rename('dark_pixels')

    # Determine the direction to project cloud shadow from clouds (assumes UTM projection).
    shadow_azimuth = ee.Number(90).subtract(ee.Number(img.get('MEAN_SOLAR_AZIMUTH_ANGLE')));

    # Project shadows from clouds for the distance specified by the CLD_PRJ_DIST input.
    cld_proj = (img.select('clouds').directionalDistanceTransform(shadow_azimuth, CLD_PRJ_DIST*10)
        .reproject(**{'crs': img.select(0).projection(), 'scale': 100})
        .select('distance')
        .mask()
        .rename('cloud_transform'))

    # Identify the intersection of dark pixels with cloud shadow projection.
    shadows = cld_proj.multiply(dark_pixels).rename('shadows')

    # Add dark pixels, cloud projection, and identified shadows as image bands.
    return img.addBands(ee.Image([dark_pixels, cld_proj, shadows]))


def add_cld_shdw_mask(img):
        """Function taken from https://developers.google.com/earth-engine/tutorials/community/sentinel-2-s2cloudless
    """
    CLD_PRB_THRESH = 40
    NIR_DRK_THRESH =0.15
    CLD_PRJ_DIST = 2
    BUFFER = 100
    # Add cloud component bands.
    img_cloud = add_cloud_bands(img, CLD_PRB_THRESH  )

    # Add cloud shadow component bands.
    img_cloud_shadow = add_shadow_bands(img_cloud, NIR_DRK_THRESH, CLD_PRJ_DIST)

    # Combine cloud and shadow mask, set cloud and shadow as value 1, else 0.
    is_cld_shdw = img_cloud_shadow.select('clouds').add(img_cloud_shadow.select('shadows')).gt(0)

    # Remove small cloud-shadow patches and dilate remaining pixels by BUFFER input.
    # 20 m scale is for speed, and assumes clouds don't require 10 m precision.
    is_cld_shdw = (is_cld_shdw.focalMin(2).focalMax(BUFFER*2/20)
        .reproject(**{'crs': img.select([0]).projection(), 'scale': 20})
        .rename('cloudmask'))

    # Add the final cloud-shadow mask to the image.
    return img_cloud_shadow.addBands(is_cld_shdw)

def apply_cld_shdw_mask(img):
        """Function taken from https://developers.google.com/earth-engine/tutorials/community/sentinel-2-s2cloudless
    """
    # Subset the cloudmask band and invert it so clouds/shadow are 0, else 1.
    not_cld_shdw = img.select('cloudmask').Not()

    # Subset reflectance bands and update their masks, return the result.
    return img.select('B.*').updateMask(not_cld_shdw)


def pull_composite_image(START_DATE, END_DATE, AOI):
    """
    Pulls composite image from google earth enginge, based on these standard levels given by google cloud development script,   
    https://developers.google.com/earth-engine/tutorials/community/sentinel-2-s2cloudless
    
    Inputs:
    Start_date: start of time period in format YYYY-MM-DD
    End date: end of time period in format YYY-MM-DD
    AOI: ee geometry object (e.g. polygon) than defines area of interest to pull data for 
    """
    CLOUD_FILTER = 60
    
    NIR_DRK_THRESH = 0.15
    CLD_PRJ_DIST = 2
    BUFFER = 100
    
    s2_sr_cld_col = get_s2_sr_cld_col(AOI, START_DATE, END_DATE, CLOUD_FILTER)
    
    s2_sr_median = (s2_sr_cld_col.map(add_cld_shdw_mask)
                             .map(apply_cld_shdw_mask)
                             .median())
    return s2_sr_median

def create_monthly_start_end_dates(years, months):
    """
    Generate three lists: start_date, end_date and date_list to pull sentinel data in a monthly manner with start and end date, 
    using date_list to label the monthly composite files. uses 30th as EOM
    
    TO DO update to include 31st
    
    Inputs:
    
    years: list of years you want to iterate over 
    months: months in the year to iterate over 
    """
    
    start_list = [] 
    end_list = [] 
    date_list = []
    
    for y in years:
        for m in months: 
            start = datetime.date( y, m, 1) 
            
            if m == 2:
                end = datetime.date( y, m, 28)
            if m!= 2:
                end = datetime.date( y, m, 30)

            start_date = start.strftime('%Y-%m-%d')
            end_date = end.strftime('%Y-%m-%d')
            date = start.strftime('%Y%m')

            start_list.append(start_date)
            end_list.append(end_date) 
            date_list.append(date)
        
        return start_list, end_list, date_list 
    

def pairwise(iterable):
    """Returns set of pairs from list- iterated over in order 
    """
    it = iter(iterable)
    a = next(it, None)

    for b in it:
        yield (a, b)
        a = b
        

def create_latlon_grid(minlat  = 50.77946266, maxlat=  53.04445373, minlon= 22.9446959 , maxlon= 32.08155782):
    """
    Create list of polygon geometry objects to iterate over with in earth engine in order to not overload memory. 
    Set up to deal with Polesia region 
    
    TODO update the increments in the linspace range to deal with inputs of any shape - current workaround, try different levels until able to download 
    """
    lon_range =  np.linspace(minlon, maxlon, 30) 

    lat_range = np.linspace(minlat, maxlat, 4)

    geom_list= []
    geom_labels=[]
    
    i=1
    
    for lower, upper in pairwise(lon_range):
        for x_low, x_up in pairwise(lat_range):

            geom = ee.Geometry.Polygon(( 
              [lower, x_low]
            , [lower, x_up] 
            , [upper, x_up]
            , [upper, x_low])  )

            geom_list.append(geom)
            geom_labels.append(i)
            i+= 1 
    return geom_list , geom_labels


def pull_monthly_cloudless_sentinel(years,outdir, coords =( 50.77946266, 53.04445373,22.9446959, 32.08155782) ):
    """
    Download normalized monthly medians of composite cloudless sentinel 2 data for bands 3 and 8 to use in CNN. For all months in years provided.
    Currently normalised using the min = 0 max = 65535 of bands 3 and 8 from Sentinel2 data. using scale 50m for outputs - this is to speed up downloads. 
    Defaults to Polesia Region
    
    TODO: update to enable other bands to be pulled, automatic set of max / min for normalisation. Allow flexible month pulling.
    Update to allow input of geometry shape and automatic breakdown. Check max min date of Sentinel2 data and add checks on valid dates
    
    Inputs:
    years: list of years
    coords: of format minlat, maxlat, minlon, maxlon defining the rectangle of interest
    outdir: output directory 
    """
    months = [i for i in range(1,13) ]
    
    max_val = 65535
    scale = 50 
    minlat, maxlat, minlon, maxlon = coords 
    
    start_list, end_list, date_list  = create_monthly_start_end_dates(years, months)
    
    geom_list, geom_labels = create_latlon_grid( minlat, maxlat, minlon, maxlon)

    for geom, label  in zip(geom_list[:], geom_labels[:]):
        for s, e, d  in zip(start_list, end_list , date_list):
            print('Starting geom/tile {}'.format(label))
            AOI = geom
 
            tile = label

            b3_file_name = os.path.join(outdir, str(d) + '_' + str(tile) +'_B03.tif' )
            b11_file_name = os.path.join(outdir, str(d) + '_'  + str(tile) +'_B11.tif' )
            b8_file_name = os.path.join(outdir, str(d) + '_'  + str(tile) +'_B08.tif' )


            if (os.path.exists(b3_file_name) is False and os.path.exists(b8_file_name) is False and os.path.exists(b11_file_name) is False):
                
                print('Starting {}'.format(d) )
                print('Creating median image')
                
                comp_image = pull_composite_image(s, e, AOI)
               
                if comp_image is not None:
                    print('Normalizing bands')
                    b8 = comp_image.select('B8').divide(max_val)
                    b3 = comp_image.select('B3').divide(max_val)
                    b11 = comp_image.select('B11').divide(max_val)

                    if os.path.exists(b3_file_name) is False:
                        print('Exporting B3 data!')
                        geemap.ee_export_image( b3, filename= b3_file_name, scale = scale, region=AOI)

                    if os.path.exists(b11_file_name) is False:
                        print('Exporting B11 data!')
                        geemap.ee_export_image( b11, filename= b11_file_name ,scale = scale, region=AOI)

                    if os.path.exists(b8_file_name) is False:
                        print('Exporting B8 data!')
                        geemap.ee_export_image( b8, filename= b8_file_name , scale = scale, region=AOI)

                    print('Data exported!')
    return

def clean_sentinel_folder(path, bad_path):
    """
    This function cleans up a folder to remove any date/tile combos that do not have all three bands- some are missing from GEE. 
    Needed to sample successfully in Torch Lightning. 
    Note this only works on folders containing only the bands noted below - run manual clean up on any other bands e.b. rm *B04.tif 
    TODO: update to deal with multiple bands 
    
    Inputs: 
    
    path: path of folder to clean 
    
    bad_path: where to move files that dont have all three files 
    
    """
    filename_regex = '^(?P<date>\\d{6})_(?P<tile>\\d{1,2})_(?P<band>B[018][\\dA]).tif$'
    filename_glob = '*B0*.tif'

    list_bands = ['B03', 'B08', 'B11']
    list_files= os.listdir(path)
    
    good = [] 
    date_tile_list = [] 
    
    for filename in list_files:
        dt = filename[0:9]
        date_tile_list.append(dt)

    for dt in date_tile_list:
        check = [s for s in list_files if dt in s]
        check = list(dict.fromkeys(check))
        if len(check) >= 3:
            good.append(dt)

    if os.path.isdir(bad_path) is False:
        os.mkdir(bad_path)

    for filename in list_files:
        dt = filename[0:9]
        if dt not in good:
            print('bad files ' + filename)
            shutil.move(os.path.join(path, filename) , os.path.join( bad_path, filename ) )


def unzip_all_modis_fire_files(output_path):
    """
    Function pulls all modis fire data from CEDA archive within Jasmin from 2001 - 2020 and unzips it into output folder. 
    Deals with different file structure for 2019 and 2007 folders.
    
    Inputs:
    output_path = path for unzipped files to be stored e.g. '/home/users/graceebc/MODIS/'
    """
    print("Pulling and unzipping the MODIS files, start()... ")
    print("Check output directory..")

    # Check path exists
    if os.path.isdir(output_path) is False:
        os.makedirs(output_path)

    # Check that annual folders exist also
    for year in range(2001, 2021):
        if os.path.isdir(output_path + str(year) + "/") is False:
            os.makedirs(output_path + str(year) + "/")

    print("Output directory ready.")
    print("Creating list of files to pulll..")

    # Access all files and unzip - need to treat 2007 and 2019 differently as there was restated data
    year_list = [x for x in range(2001, 2021) if (x != 2007 and x != 2019)]
    months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

    # Create list of files - 2007 has different folder structure + 2019
    file_part1 = [
        "/neodc/esacci/fire/data/burned_area/MODIS/pixel/v5.1/compressed/{0}/{0}{1}01-ESACCI-L3S_FIRE-BA-MODIS-AREA_3-fv5.1.tar.gz".format(
            year, month
        )
        for year in year_list
        for month in months
    ]
    file_part2 = [
        "/neodc/esacci/fire/data/burned_area/MODIS/pixel/v5.1/compressed/2007/new-corrected/2007{0}01-ESACCI-L3S_FIRE-BA-MODIS-AREA_3-fv5.1.tar.gz".format(
            month
        )
        for month in months
    ]
    file_part3 = [
        "/neodc/esacci/fire/data/burned_area/MODIS/pixel/v5.1/compressed/2019/2019{0}01-ESACCI-L3S_FIRE-BA-MODIS-AREA_3-fv5.1.tar.gz".format(
            month
        )
        for month in months[:9]
    ]
    file_part4 = [
        "/neodc/esacci/fire/data/burned_area/MODIS/pixel/v5.1/compressed/2019/new-corrected/2019{0}01-ESACCI-L3S_FIRE-BA-MODIS-AREA_3-fv5.1.tar.gz".format(
            month
        )
        for month in months[-3:]
    ]
    files = file_part1 + file_part2 + file_part3 + file_part4
    print("List of files created.")

    print("Start unzipping files..")
    for file_name in files:

        try:
            dat = dateutil.parser.parse(
                str(file_name[68:80].replace("/", " ")), fuzzy="yes"
            )
            name = dat.strftime("%Y%m%d")

        except:
            dat = dateutil.parser.parse(
                str(file_name[80:95].replace("/", " ")), fuzzy="yes"
            )
            name = dat.strftime("%Y%m%d")
        file_id = "{0}-ESACCI-L3S_FIRE-BA-MODIS-AREA_3-fv5.1-LC.tif".format(name)
        year = name[:4]

        # check if file already unzipped
        if file_id not in os.listdir(output_path + year + "/"):

            # Open file
            file = tarfile.open(file_name)

            # Extracting file
            file.extractall(output_path + year + "/")

            file.close()

    print("Unzipped all MODIS files, bye!")
