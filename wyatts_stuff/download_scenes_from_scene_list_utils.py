# FIXME get methods sorted out for the scene search and download steps

import os
import numpy as np
import json
import requests
import sys
import time
import datetime
import json

with open('m2m_credentials.json') as f:
    credentials = json.load(f)


def search_datasets_and_scenes(serviceUrl, apiKey, datasetName, date_acquired, path, row):
    """
    Search for datasets and scenes using the M2M API.

    Parameters:
    serviceUrl (str): The base URL of the M2M API.
    apiKey (str): The API key.
    datasetName (str): The name of the dataset to search for.
    date_acquired (str): The acquisition date to filter scenes by.
    path (int): The path to filter scenes by.
    row (int): The row to filter scenes by.

    Returns:
    list: The scenes found.
    """

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

    return scenes

def retrieve_l8c2l1_scene_from_usgs(directory, serviceUrl, apiKey, datasetName, sceneId):
    # Specify the folder you want to open
    folder_path = os.path.join(directory, sceneId)

    # Get a list of all files in the folder
    files = os.listdir(folder_path)

    # # Get the first MTL file in the folder
    # # This assumes that the MTL file has a '.txt' extension
    mtl_files = [file for file in files if file.endswith('.txt') and ('MTL' in file or 'mtl' in file)]

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

    scenes = search_datasets_and_scenes(serviceUrl, apiKey, datasetName, date_acquired, path, row)

# send http request
def sendRequest(url, data, apiKey = None):  
    json_data = json.dumps(data)
    
    if apiKey == None:
        response = requests.post(url, json_data)
    else:
        headers = {'X-Auth-Token': apiKey}              
        response = requests.post(url, json_data, headers = headers)    
    
    try:
      httpStatusCode = response.status_code 
      if response == None:
          print("No output from service")
          sys.exit()
      output = json.loads(response.text)	
      if output['errorCode'] != None:
          print(output['errorCode'], "- ", output['errorMessage'])
          sys.exit()
      if  httpStatusCode == 404:
          print("404 Not Found")
          sys.exit()
      elif httpStatusCode == 401: 
          print("401 Unauthorized")
          sys.exit()
      elif httpStatusCode == 400:
          print("Error Code", httpStatusCode)
          sys.exit()
    except Exception as e: 
          response.close()
          print(e)
          sys.exit()
    response.close()
    
    return output['data']

def download_scenes(dataset, serviceUrl, apiKey, sceneIds, downloadDir):
    # Find the download options for these scenes
    # NOTE :: Remember the scene list cannot exceed 50,000 items!
    payload = {'datasetName': dataset['datasetAlias'], 'entityIds': sceneIds}
    downloadOptions = sendRequest(serviceUrl + "download-options", payload, apiKey)

    # Aggregate a list of available products
    downloads = []
    for product in downloadOptions:
        # Make sure the product is available for this scene
        if product['available'] == True:
            downloads.append({'entityId': product['entityId'], 'productId': product['id']})

    # Did we find products?
    if downloads:
        requestedDownloadsCount = len(downloads)
        # set a label for the download request
        label = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") # Customized label using date time
        payload = {'downloads': downloads, 'label': label}
        # Call the download to get the direct download urls
        requestResults = sendRequest(serviceUrl + "download-request", payload, apiKey)

        # PreparingDownloads has a valid link that can be used but data may not be immediately available
        # Call the download-retrieve method to get download that is available for immediate download
        if requestResults['preparingDownloads'] != None and len(requestResults['preparingDownloads']) > 0:
            payload = {'label': label}
            moreDownloadUrls = sendRequest(serviceUrl + "download-retrieve", payload, apiKey)

            downloadIds = []
            for download in moreDownloadUrls['available']:
                if str(download['downloadId']) in requestResults['newRecords'] or str(download['downloadId']) in requestResults['duplicateProducts']:
                    downloadIds.append(download['downloadId'])
                    print("DOWNLOAD: " + download['url'])

            for download in moreDownloadUrls['requested']:
                if str(download['downloadId']) in requestResults['newRecords'] or str(download['downloadId']) in requestResults['duplicateProducts']:
                    downloadIds.append(download['downloadId'])
                    print("DOWNLOAD: " + download['url'])

            # Didn't get all of the requested downloads, call the download-retrieve method again probably after 30 seconds
            while len(downloadIds) < (requestedDownloadsCount - len(requestResults['failed'])):
                preparingDownloads = requestedDownloadsCount - len(downloadIds) - len(requestResults['failed'])
                print("\n", preparingDownloads, "downloads are not available. Waiting for 30 seconds.\n")
                time.sleep(30)
                print("Trying to retrieve data\n")
                moreDownloadUrls = sendRequest(serviceUrl + "download-retrieve", payload, apiKey)
                for download in moreDownloadUrls['available']:
                    if download['downloadId'] not in downloadIds and (str(download['downloadId']) in requestResults['newRecords'] or str(download['downloadId']) in requestResults['duplicateProducts']):
                        downloadIds.append(download['downloadId'])
                        print("DOWNLOAD: " + download['url'])

        else:
            # Get all available downloads
            for i, download in enumerate(requestResults['availableDownloads']):
                # TODO :: Implement a downloading routine
                print("DOWNLOAD: " + download['url'])
                download_url = download['url']

                # Specify the download directory and filename

                filename = f'download_{i}' + '.tar.gz'

                # Create the full file path
                file_path = os.path.join(downloadDir, filename)

                # Download the file
                response = requests.get(download_url)

                # Write the file
                with open(file_path, 'wb') as f:
                    f.write(response.content)

        print("\nAll downloads are available to download.\n")
    else:
        print("Search found no results.\n")

def get_api_key(credentials_file):
    """
    Login to the M2M API and return the API key.

    Parameters:
    credentials_file (str): The path to the JSON file containing the username and password.

    Returns:
    str: The API key.
    """

    # Load the credentials from the JSON file
    with open(credentials_file) as f:
        credentials = json.load(f)

    # Login to the M2M API
    serviceUrl = "https://m2m.cr.usgs.gov/api/api/json/stable/"
    payload = {"username": credentials['username'], "password": credentials['password']}
    apiKey = sendRequest(serviceUrl + "login", payload)

    return apiKey