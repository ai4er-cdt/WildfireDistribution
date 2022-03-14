#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import requests
from google.cloud import bigquery
from google.oauth2 import service_account

import pandas as pd
import pandas
import pyarrow

import datetime


# In[3]:


# list of relevant tiles
tile_dict = [
    {"mgrs_tile": "35UMS"},
    {"mgrs_tile": "35UNV"},
    {"mgrs_tile": "35UNT"},
    {"mgrs_tile": "35UPS"},
    {"mgrs_tile": "35UQV"},
    {"mgrs_tile": "35UMU"},
    {"mgrs_tile": "35UMR"},
    {"mgrs_tile": "34UGB"},
    {"mgrs_tile": "35UQU"},
    {"mgrs_tile": "35UMT"},
    {"mgrs_tile": "35UPU"},
    {"mgrs_tile": "35UNS"},
    {"mgrs_tile": "35UPR"},
    {"mgrs_tile": "34UGC"},
    {"mgrs_tile": "35UPT"},
    {"mgrs_tile": "35ULU"},
    {"mgrs_tile": "35ULT"},
    {"mgrs_tile": "35ULS"},
    {"mgrs_tile": "36UUD"},
    {"mgrs_tile": "35UNU"},
    {"mgrs_tile": "34UGD"},
]


# In[5]:


tile_list = [x for dict in tile_dict for x in dict.values()]
BASE_URL = "http://storage.googleapis.com/"


# In[4]:


# In[ ]:


def query_sentinel(key_json, project_id, start, end, tile, cloud=100.0):
    credentials = service_account.Credentials.from_service_account_file(key_json)
    client = bigquery.Client(credentials=credentials, project=project_id)
    query = client.query(
        """
            SELECT * FROM `bigquery-public-data.cloud_storage_geo_index.sentinel_2_index` 
                WHERE (mgrs_tile = '{t}' 
                and CAST(SUBSTR(CAST(sensing_time as STRING ) , 1, 10) as DATE) >= CAST('{s}' AS DATE)
                AND CAST(SUBSTR(CAST(sensing_time as STRING ) , 1, 10) as DATE) < CAST('{e}' AS DATE) ) 
            """.format(
            t=tile, s=start, e=end
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


# In[ ]:


def download_file(url, dst_name):
    try:
        data = requests.get(url, stream=True)
        with open(dst_name, "wb") as out_file:
            for chunk in data.iter_content(chunk_size=100 * 100):
                out_file.write(chunk)
    except:
        print("\t ... {f} FAILED!".format(f=url.split("/")[-1]))
    return


def make_safe_dirs(scene, outpath):
    scene_name = os.path.basename(scene)
    scene_path = os.path.join(outpath, scene_name)
    manifest = os.path.join(scene_path, "manifest.safe")
    manifest_url = scene + "/manifest.safe"
    if os.path.exists(manifest):
        os.remove(manifest)
    download_file(manifest_url, manifest)
    with open(manifest, "r") as f:
        manifest_lines = f.read().split()
    download_links = []
    load_this = False
    for line in manifest_lines:
        if "href" in line:
            #             online_path = line[7:line.find('><')]
            online_path = line[7 : line.find("><") - 2]
            tile = scene_name.split("_")[-2]
            if online_path.startswith("/GRANULE/"):
                if "_" + tile + "_" in online_path:
                    load_this = True
            else:
                load_this = True
            if load_this:
                local_path = os.path.join(scene_path, *online_path.split("/")[1:])
                online_path = scene + online_path
                download_links.append((online_path, local_path))
        load_this = False
    for extra_dir in ("AUX_DATA", "HTML"):
        if not os.path.exists(os.path.join(scene_path, extra_dir)):
            os.makedirs(os.path.join(scene_path, extra_dir))
    return download_links


def download_sentinel(scene, dst):
    scene_name = scene.split("/")[-1]
    scene_path = os.path.join(dst, scene_name)
    print(scene_path)
    if not os.path.exists(scene_path):
        os.mkdir(scene_path)
    print("Downloading scene {s} ...".format(s=scene_name))
    download_links = sorted(make_safe_dirs(scene, dst))
    for l in download_links:
        if not os.path.exists(os.path.dirname(l[1])):
            os.makedirs(os.path.dirname(l[1]))
        if os.path.exists(l[1]):
            os.remove(l[1])

        if "B04.j" in l[1] or "B03.j" in l[1] or "B08.j" in l[1]:
            print("\t ... *{b}".format(b=l[1].split("_")[-1]))
            if download_file(l[0], l[1]) is False:
                print(
                    "\t ... {f} failed to download! Download for this scene is cancelled here!".format(
                        f=l[0]
                    )
                )
                return


### finally do it ###
if __name__ == "__main__":
    key_json = r"/home/users/graceebc/sentinel-342714-c434e5e45305.json"
    project_id = "sentinel-342714"
    outdir = (
        r"/gws/nopw/j04/bas_climate/projects/WildfireDistribution/sentinel/2016_test"
    )
    #     tile = '35UPU'
    cloud = 10
    start = "2016-12-10"
    end = "2016-12-31"
    if os.path.isdir(outdir) is False:
        os.mkdir(outdir)
    for tile in tile_list:
        scene_list = query_sentinel(key_json, project_id, start, end, tile, cloud)
        print("Start {}. Length of scenes: {}".format(tile, len(scene_list)))
        for s in scene_list:
            download_sentinel(s, outdir)


# In[ ]:
