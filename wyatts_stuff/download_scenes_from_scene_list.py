# Go through existing zips and find scenes inside
# Create folder with scene name and unzip the scene
# Define dataset

import os
from download_scenes_from_scene_list_utils import *


# payload = {'datasetName': datasetName, 'maxResults': 10}
# datasets = sendRequest(serviceUrl + "dataset-search", payload, apiKey)
# dataset = datasets[0]

########## TEST - TEST A SCENE FROM THE SPARCS FOLDER ##########
# sparcs_dir = os.path.join(top_dir, 'sparcsdownloads')
# usgs_dir = os.path.join(top_dir, 'usgsdownloads')
# sceneIds = os.listdir(sparcs_dir)
# sceneIds = sceneIds[:1]

# Get information from the scene




# Add main function
def main():
    # Initial variable setting
    # top_dir = input("Please provide top level dir (containing properly named folders): ")
    top_dir = r'C:\Users\12078\OneDrive\Desktop\sample_scenes'
    datasetName = 'landsat_ot_c2_l1'
    serviceUrl = "https://m2m.cr.usgs.gov/api/api/json/stable/"

    # Get the api key
    apiKey = get_api_key('m2m_credentials.json')   

    # Get scene ids from directory
    sceneIds = os.listdir(top_dir)

    for sceneId in sceneIds:
        # Run the helper function that 
        retrieve_l8c2l1_scene_from_usgs(top_dir, serviceUrl, apiKey, datasetName, sceneId)

# Call main function
if __name__ == "__main__":
    main()