import os
import numpy as np
import json
import requests
import sys
import time
import datetime
import json
from download_scenes_from_scene_list_utils import *

top_dir = r'C:\Users\12078\Downloads\l8cloudmasks'

with open('m2m_credentials.json') as f:
    credentials = json.load(f)

# Login to the M2M API
serviceUrl = "https://m2m.cr.usgs.gov/api/api/json/stable/"
payload = {"username": credentials['username'], "password": credentials['password']}
apiKey = sendRequest(serviceUrl + "login", payload)

# Go through existing zips and find scenes inside
# Create folder with scene name and unzip the scene
# Define dataset
datasetName = 'landsat_ot_c2_l1'
# payload = {'datasetName': datasetName, 'maxResults': 10}
# datasets = sendRequest(serviceUrl + "dataset-search", payload, apiKey)
# dataset = datasets[0]

########## TEST - TEST A SCENE FROM THE SPARCS FOLDER ##########
sparcs_dir = os.path.join(top_dir, 'sparcsdownloads')
usgs_dir = os.path.join(top_dir, 'usgsdownloads')
sceneIds = os.listdir(sparcs_dir)
sceneIds = sceneIds[:1]

# Get information from the scene

# Specify the folder you want to open
folder_path = os.path.join(sparcs_dir, sceneIds[0])

# Get a list of all files in the folder
files = os.listdir(folder_path)

# # Get the first MTL file in the folder
# # This assumes that the MTL file has a '.txt' extension
mtl_files = [file for file in files if file.endswith('.txt') and ('MTL' in file or 'mtl' in file)]
# mtl_file = mtl_files[0]

# If there is at least one MTL file, get the first one
if mtl_files:
    mtl_file = mtl_files[0]
    mtl_file_path = os.path.join(folder_path, mtl_file)

    # Example of how the mtl data will look
    # WRS_PATH = 128
    # WRS_ROW = 42
    # NADIR_OFFNADIR = "NADIR"
    # TARGET_WRS_PATH = 128
    # TARGET_WRS_ROW = 42
    # DATE_ACQUIRED = 2014-03-15

    # Extract the path, row, and date

    # Initialize variables
    path = None
    row = None
    date_acquired = None

    # Open the text file and read the lines
    with open(mtl_file_path, 'r') as file:
        lines = file.readlines()

        for line in lines:
            if 'WRS_PATH' in line or 'WRS_ROW' in line or 'DATE_ACQUIRED' in line:
                # Split the line into name and value
                name, value = line.split(' = ')

                # Remove any trailing newline characters from the value
                name = name.strip()
                value = value.rstrip('\n')

                # Check if the name matches what we're looking for
                if name == 'WRS_PATH':
                    path = value
                elif name == 'WRS_ROW':
                    row = value
                elif name == 'DATE_ACQUIRED':
                    date_acquired = value

    print(f"Path: {path}, Row: {row}, Date: {date_acquired}")

    # print(f"Path: {path}, Row: {row}, Date: {date}")
else:
    print("No MTL files found in the folder.")

# Get response from the API
print("Dataset Info: ")
# print(dataset)
print("\n")
print('\n')

temporalFilter = {'start' : '2013-03-08', 'end' : '2014-01-01'}

payload = {'datasetName' : datasetName,
                            'temporalFilter' : temporalFilter}                     

print("Searching datasets...\n")
datasets = sendRequest(serviceUrl + "dataset-search", payload, apiKey)
print("Datasets found: ")
print(datasets)
dataset = datasets[0]

acquisition_filter = {
    "start": date_acquired,
    "end": date_acquired
}

payload = {'datasetName' : dataset['datasetAlias'], 
                            'maxResults' : 2,
                            'startingNumber' : 1, 
                            'sceneFilter' : {'path' : path, 'row' : row, 'acquisitionFilter' : acquisition_filter}}

print("Searching scenes...\n")
scenes = sendRequest(serviceUrl + "scene-search", payload, apiKey)
print("Scenes found: " , scenes)
