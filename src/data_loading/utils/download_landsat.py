#!/usr/bin/env python
# coding: utf-8

# In[1]:


# use google_cloud on jasmin
import os
import requests
from google.cloud import bigquery
from google.oauth2 import service_account

import pandas as pd
import pandas
import pyarrow

import datetime

import requests


BASE_URL = "http://storage.googleapis.com/"


def query_sentinel(key_json, project_id, start, end, row, path, cloud=100.0):
    credentials = service_account.Credentials.from_service_account_file(key_json)
    client = bigquery.Client(credentials=credentials, project=project_id)
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


def download_landsat(row_list, path_list, bands, outdir, cloud):
    download_links = []
    scene_names = []

    for x in row_list:
        row = x
        for y in path_list:
            path = y
            scene_list = query_sentinel(
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


### finally do it ###
if __name__ == "__main__":
    key_json = r"/home/users/graceebc/sentinel-342714-c434e5e45305.json"
    project_id = "sentinel-342714"
    outdir = r"/gws/nopw/j04/bas_climate/projects/WildfireDistribution/landsat/"
    #     outdir = '/home/users/graceebc/landsat/'
    start = "2000-01-01"
    end = "2020-12-31"
    cloud = 100
    row_list = [23, 24]
    path_list = [x for x in range(182, 187)]
    bands = ["_B3.TIF", "_B4.TIF", "_B5.TIF"]

    download_landsat(row_list, path_list, bands, outdir, cloud)
