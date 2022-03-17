#!/usr/bin/env python
# coding: utf-8
import ee
import geemap
import datetime
import os
import numpy as np

#This script download Sentinel2 data in the form of monthly median composite images, for bands 3 and 8,  which are normalized to within 0-1. Data download from EE can be slow - to imrpove run time you can lower the scale (resolution of output) or run different years concurrently.
#Requirements: have an Earth Enginge account and authenticate the environment after installing our dataloading_evn.yml file. 

# Initialize the library.
ee.Initialize()

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
        """Function taken from https://developers.google.com/earth-engine/tutorials/community/sentinel-2-s2cloudless
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
    Set up to deal with polesia region 
    
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
            b4_file_name = os.path.join(outdir, str(d) + '_'  + str(tile) +'_B04.tif' )
            b8_file_name = os.path.join(outdir, str(d) + '_'  + str(tile) +'_B08.tif' )


            if (os.path.exists(b3_file_name) is False  and os.path.exists(b8_file_name) is False):
                print('Starting {}'.format(d) )
                print('Creating median image')
                comp_image = pull_composite_image(s, e, AOI)
               
                if comp_image is not None:
                    print('Normalizing bands')
                    b8 = comp_image.select('B8').divide(max_val)
                    b3 = comp_image.select('B3').divide(max_val)
#                     b4 = comp_image.select('B4').divide(max_val)

                    if os.path.exists(b3_file_name) is False:
                        print('Exporting B3 data!')
                        geemap.ee_export_image( b3, filename= b3_file_name, scale = scale, region=AOI)

#                     if os.path.exists(b4_file_name) is False:
#                         print('Exporting B4 data!')
#                         geemap.ee_export_image( b4, filename= b4_file_name ,scale = scale, region=AOI)

                    if os.path.exists(b8_file_name) is False:
                        print('Exporting B8 data!')
                        geemap.ee_export_image( b8, filename= b8_file_name , scale = scale, region=AOI)

                    print('Data exported!')
    return
      
if __name__ == '__main__':
    years = [2017, 2018,2019, 2020]
    outdir = r'/gws/nopw/j04/bas_climate/projects/WildfireDistribution/cloudless'
    
    if os.path.isdir(outdir) is False:
        os.mkdir(outdir)
        
    for y in years:
        pull_monthly_cloudless_sentinel(y, outdir)
