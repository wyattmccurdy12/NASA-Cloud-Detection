# Imports
# Download the files
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import os
import shutil
import os
import tarfile
import glob

# Provide a folder for unprocessed images
unproc_folder = 'D:/BIOME-dataset-images/unzipped'
unproc_imgs = []

# Provide a folder for processed images
proc_folder = 'C:/Users/12078/OneDrive/Documents/TESTFOLDER/etc/l8biomedownloads/unzipped'
proc_imgs = []

# Provide names of all images from the download links from USGS
# Get the HTML content of the page
url = 'https://landsat.usgs.gov/landsat-8-cloud-cover-assessment-validation-data'  # replace with your URL
response = requests.get(url)
html_content = response.text
soup = BeautifulSoup(html_content, 'html.parser')
download_links = [a['href'] for a in soup.find_all('a', href=True) if a.text]
download_links = [link for link in download_links if link.endswith('.tar.gz')]

# For all the images in the processed folder, check if the fmask algorithm has been run
for file in os.listdir(proc_folder):
    if file.endswith('.tif') and file.endswith('_Fmask4.tif'):
        # Fmask algorithm has been run for this image
        # Add the file to the list of processed images
        proc_imgs.append(file)
    else:
        # Fmask algorithm has not been run for this image
        # Add the file to the list of unprocessed images
        unproc_imgs.append(file)

# Check if the images in the unprocessed folder have been processed
for file in os.listdir(unproc_folder):
    if file.endswith('.tif') and file.endswith('_Fmask4.tif'):
        # Fmask algorithm has been run for this image
        # Add the file to the list of processed images
        proc_imgs.append(file)
    else:
        # Fmask algorithm has not been run for this image
        # Add the file to the list of unprocessed images
        unproc_imgs.append(file)

# Give a report
print("Number of processed images:", len(proc_imgs))
print("Number of unprocessed images:", len(unproc_imgs))

print("Unprocessed image names:")
for image in unproc_imgs:
    print(image)

# Combine processed and unprocessed list
all_imgs = proc_imgs + unproc_imgs

# Compare to the list of download links - download if not in all_imgs list
for link in download_links:
    # Get the name of the file
    filename = link.split('/')[-1]
    if filename not in all_imgs:
        # Download the file
        print("Downloading", filename)
        response = requests.get(link, stream=True)
        with open(os.path.join(unproc_folder, filename), 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
