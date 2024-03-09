import rasterio
import numpy as np
import os
import time
import os
import glob
# import fmask


def split_image_into_chunks(image_path, out_folder, scene_name, chunk_size=384):
    """
    Split an image into chunks of a specific size and save them in an output location

    Parameters:
    image_path (str): The path to the image.
    chunk_size (int): The size of each chunk in pixels.
    out_folder (str): The output folder where the chunks will be saved.
    scene_name (str): The name of the input scene (taken from its directory).

    Returns:
    None
    """


    # Get name of scene and assign it to subfolder name
    tif_file_name = os.path.basename(image_path).split('.')[0]
    high_level_out_path = os.path.join(out_folder, scene_name)
    low_level_out_path = os.path.join(high_level_out_path, tif_file_name)
    # print("high level out path: ", high_level_out_path)
    # print("low level out path: ", low_level_out_path)

    if not os.path.exists(high_level_out_path):
        os.makedirs(high_level_out_path)
    
    if not os.path.exists(low_level_out_path):
        os.makedirs(low_level_out_path)
    
    print("Processing ", scene_name, ", ", tif_file_name)

    # Open the image
    with rasterio.open(image_path) as src:
        # Get the image dimensions
        height = src.height
        width = src.width

        # Calculate the new dimensions with zero padding
        new_height = int(np.ceil(height / chunk_size) * chunk_size)
        new_width = int(np.ceil(width / chunk_size) * chunk_size)

        # Calculate the padding sizes
        height_padding = new_height - height
        width_padding = new_width - width

        # Resize/buffer the image with zeros
        padded_image = np.pad(src.read(), ((0, 0), (0, height_padding), (0, width_padding)), mode='constant')

        # Calculate the number of chunks in each dimension
        num_chunks_height = new_height // chunk_size
        num_chunks_width = new_width // chunk_size

        # Reshape the image into chunks
        reshaped_image = padded_image.reshape(num_chunks_height, chunk_size, num_chunks_width, chunk_size, -1)

        # Transpose the axes to get the chunks in the correct order
        chunks = reshaped_image.transpose(0, 2, 1, 3, 4)

        # Iterate over the chunks and save them as separate images
        for i in range(chunks.shape[0]):
            for j in range(chunks.shape[1]):
                # Get the current chunk
                data = chunks[i, j]

                # Create the filename for the current chunk
                chunk_filename = f"{tif_file_name}_{i * chunk_size}_{j * chunk_size}.tif"
                chunk_filepath = os.path.join(low_level_out_path, chunk_filename)

                # Save the current chunk as a separate image
                # Save the current chunk as a separate image
                if not os.path.exists(chunk_filepath):
                    with rasterio.open(chunk_filepath, 'w', **src.meta) as dst:
                        dst.write(np.moveaxis(data, -1, 0))


def process_images_in_dir(top_level_dir, in_folder, out_folder, chunk_size=384):
    """
    Process all images within a top level directory given a name of an input and output folder within said directory.
    """

    os.chdir(top_level_dir)

    # Traverse through all the directories and files in the input folder
    for dirpath, dirnames, filenames in os.walk(in_folder):

        if dirpath.endswith('_B8') or dirpath.endswith('_BQA'):
            continue

        # Process each TIFF image file
        for filename in filenames:
            if filename.endswith('.TIF'):
                # Get the full path of the image file
                image_file = os.path.join(dirpath, filename)
                # print("Processing image file - ", image_file)

                # Get the scene name from the directory name
                scene_name = os.path.basename(dirpath)
                # print("In scene - ", scene_name)

                # Split the image into chunks and save them in the output folder
                split_image_into_chunks(image_file, out_folder, scene_name, chunk_size)
                # print(image_file, "\n", scene_name)

def main():

    top_level_dir = '/home/wyatt.mccurdy/Documents/L8_BIOME_TEST/'
    original_imgs = 'Original_Extracted'
    output_imgs = 'Chunked'

    start_time = time.time()
    process_images_in_dir(top_level_dir, original_imgs, output_imgs)
    end_time = time.time()
    execution_time = (end_time - start_time) / 60
    print(f"Execution time: {execution_time} minutes")


    # # Specify the path to the image
    # image_path = '/home/wyatt.mccurdy/Documents/L8_BIOME_TEST/Original_Extracted/LC80160502014041LGN00/LC80160502014041LGN00_B1.TIF'
    # # Specify the output folder
    # out_folder = '/home/wyatt.mccurdy/Documents/L8_BIOME_TEST/Chunked/'
    # # Specify the scene name
    # scene_name = 'LC80160502014041LGN00'
    # # Specify the chunk size
    # chunk_size = 384

    # # Call the split_image_into_chunks function
    # start_time = time.time()
    # split_image_into_chunks(image_path, out_folder, scene_name, chunk_size)
    # end_time = time.time()

    # execution_time = end_time - start_time
    # print(f"Execution time: {execution_time} seconds")

if __name__ == "__main__":
    main()