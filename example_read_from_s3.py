
from shapely.geometry import shape

coords = {
  "type": "Polygon",
  "coordinates": [
        [
            [
                100.053179477376972,
                15.201781400278016
            ],
            [
                100.05525938863012,
                15.204290299988905
            ],
            [
                100.057553408394639,
                15.202932546204847
            ],
            [
                100.056421691977476,
                15.199980877380222
            ],
            [
                100.053179477376972,
                15.201781400278016
            ]
        ]
    ]
}


geom = shape(coords)

min_lon, min_lat, max_lon, max_lat = geom.bounds


import time
import os
from dotenv import load_dotenv
load_dotenv()


os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID", "")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY", "")
os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-1"

os.environ["AWS_S3_ENDPOINT"] = os.getenv("AWS_S3_ENDPOINT", "")
os.environ["AWS_S3_SIGNATURE_VERSION"] = "s3v4"
os.environ["AWS_VIRTUAL_HOSTING"] = os.getenv("AWS_VIRTUAL_HOSTING", "FALSE")
os.environ["AWS_HTTPS"] = os.getenv("AWS_HTTPS", "NO")

# ===== now import GIS libs =====
import rioxarray
import rasterio
import glob
from osgeo import gdal

print("ENDPOINT:", gdal.GetConfigOption("AWS_S3_ENDPOINT"))
print("VHOST:", gdal.GetConfigOption("AWS_VIRTUAL_HOSTING"))
print("ACCESS:", gdal.GetConfigOption("AWS_ACCESS_KEY_ID"))

def clip_image(ds_r_org, params, download_path, collection_id):
    ds_r = ds_r_org.rio.clip_box(
        minx=float(params["param1"]),
        miny=float(params["param2"]),
        maxx=float(params["param3"]),
        maxy=float(params["param4"]),
    )

    tifpath = os.path.join(download_path, f"{collection_id}.tif")
    ds_r.rio.to_raster(tifpath)

    return tifpath

def read_raster_from_s3(usr_id, collection_id, filename):
    s3_url = f"s3://{usr_id}/coverage/{collection_id}/cog/{filename}"

    ds_r_org = rioxarray.open_rasterio(s3_url)[0]
    download_path = "temp/s3_download"
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    clip_data = ds_r_org.rio.clip_box(
        minx=min_lon,
        miny=min_lat,
        maxx=max_lon,
        maxy=max_lat
    )
    #Don't forget to save clipped data
    tifpath = os.path.join(download_path, f"{collection_id}_clip.tif")
    clip_data.rio.to_raster(tifpath)

user_id = "644b92f9fbf1689fb3497525"
filename = glob.glob("temp/out_compress_test/zstd/*")
collection_id = "69006a3bbe4e87ecda5c176e"
download_path = "temp"

for data in sorted(filename):
    start_time = time.time()
    files = data.split("/")[-1]
    data = read_raster_from_s3(user_id, collection_id, files)

    endtime = time.time()
    print("File:", files)
    print("Time:", endtime - start_time, "seconds")
    print("=========")