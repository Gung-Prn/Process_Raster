import numpy as np
import rasterio
from rasterio.windows import Window
import glob
import logging
import time
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

def calculate_mean_rasters_large(raster_files: list, output_file: str, block_size: int = 1000) -> None:
    start_time = time.time()
    # Initialize variables to store maximum width and height
    max_width = 0
    max_height = 0
    
    # Loop through raster files to find the maximum width and height
    logger.info('Determining maximum width and height from raster files.')
    for raster_file in raster_files:
        with rasterio.open(raster_file) as src:
            # Update maximum width and height if necessary
            max_width = max(max_width, src.width)
            max_height = max(max_height, src.height)
            logger.debug(f'Checked raster: {raster_file}, width: {src.width}, height: {src.height}')

    logger.info(f'Maximum width: {max_width}, Maximum height: {max_height}')
    # Use one of the raster files as a template for metadata
    with rasterio.open(raster_files[0]) as template_src:
        meta = template_src.meta
        meta.update(dtype=rasterio.float32, count=1, width=max_width, height=max_height)

    # Create an output raster file
    with rasterio.open(output_file, 'w', **meta) as dst:
        logger.info(f'Created output raster file: {output_file}')
        # Process the raster in chunks
        process_start_time = time.time()
        for j in range(0, max_height, block_size):
            for k in range(0, max_width, block_size):
                win = Window(k, j, min(block_size, max_width - k), min(block_size, max_height - j))
                # Stack the data for all rasters in the current window
                stack = []
                for raster_file in raster_files:
                    with rasterio.open(raster_file) as src:
                        # Adjust window to match raster size
                        win_adjusted = win.intersection(Window(0, 0, src.width, src.height))
                        # print(win_adjusted)
                        if win_adjusted.width == 0 or win_adjusted.height == 0:
                            raster_data = np.full((win.height, win.width), src.nodata, dtype=np.float32)
                            logger.info(f'Window adjusted has no data for raster')
                        else:
                            raster_data = src.read(1, window=win_adjusted).astype(np.float32)
                            logger.info(f'raster = window frame ')
                            # Pad with nodata if the window exceeds raster dimensions
                            if win_adjusted.width < win.width or win_adjusted.height < win.height:
                                padded_data = np.full((win.height, win.width), src.nodata, dtype=np.float32)
                                padded_data[:win_adjusted.height, :win_adjusted.width] = raster_data
                                raster_data = padded_data
                                logger.info(f'Padded raster data for window')
                        stack.append(raster_data)
                # Convert the stack list to a 3D numpy array
                stack_values = np.stack(stack, axis=0)
                # Calculate the median along the first dimension
                median_raster = np.median(stack_values, axis=0)
                # Write the median values to the output raster
                dst.write(median_raster, 1, window=win)
        process_end_time = time.time()
        logger.info(f'Processing time: {process_end_time - process_start_time:.2f} seconds')
    end_time = time.time()
    logger.info(f'Total time for calculation: {end_time - start_time:.2f} seconds')
logger.info('Finished calculation of median rasters.')
# List of raster files
raster_files = glob.glob('/mnt/New_processData_month/NDVI/data_test_01/*.tif')
# Output file
output_file = '/mnt/New_processData_month/NDVI/Midian_NDVI_N0510_R104_T47PNS_202401.tif'

calculate_mean_rasters_large(raster_files, output_file , 1000)
