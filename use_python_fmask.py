import fmask
from fmask import landsatTOA

input_dir = "/home/wyatt.mccurdy/Documents/FMASK_test/LC08_L1TP_098014_20240308_20240308_02_RT/"

# Run fmask processing on the input directory
input_dir = "/home/wyatt.mccurdy/Documents/FMASK_test/LC08_L1TP_098014_20240308_20240308_02_RT/"

# Preprocess the Landsat image to convert to TOA
# landsatTOA.riosTOA

# Run fmask processing on the input directory
fmask.run_fmask(input_dir)