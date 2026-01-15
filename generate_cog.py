from osgeo import gdal

input_tif = "output/test_tif.tif"
output_cog = "temp/new_test_tif_cog.tif"

gdal.Translate(
    destName=output_cog,
    srcDS=input_tif,
    format="COG",
    creationOptions=[
        "COMPRESS=ZSTD",
        "LEVEL=22",
        "BLOCKSIZE=512",
        "OVERVIEW_RESAMPLING=AVERAGE"
    ],
)

print(f"Done: {output_cog}")