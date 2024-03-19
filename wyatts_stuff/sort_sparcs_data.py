'''
The purpose of this py file is to take all images in a newly downloaded sparcs directory and sort them into folders based on scene name. 
It just takes *_mtl.txt files and grabs the first part

It takes a user-given argument for the location that it's supposed to be run on.
'''
# Imports
import os
import shutil


# Helper functions
def sort_files_into_folders(files, location):
    """
    Sort files into folders based on the first part of their names.

    Parameters:
    files (list): The list of file names.
    location (str): The directory where the files are located and where the folders will be created.

    Returns:
    None
    """

    # Iterate over the files
    for file in files:
        # Get the first part of the file name
        name_part = file.split("_")[0]

        # Create the folder if it doesn't exist
        folder_path = os.path.join(location, name_part)
        if not os.path.exists(folder_path):
            print("making dir: ", folder_path)
            os.makedirs(folder_path)

        # Move the file to the folder
        file_path = os.path.join(location, file)
        print("new file path: ", file_path)
        shutil.move(file_path, folder_path)

def main():
    # Get the user-given argument for the location
    location = input("Enter the location to run the script on: ")

    # Check if the location exists
    if not os.path.exists(location):
        print("Invalid location.")
        return

    # Get all the files in the location
    files = os.listdir(location)

    sort_files_into_folders(files, location)

    print("Sorting complete.")

if __name__ == "__main__":
    main()