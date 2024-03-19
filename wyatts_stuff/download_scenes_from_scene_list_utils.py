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