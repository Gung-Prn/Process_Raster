from rio_cogeo.cogeo import cog_validate
            
input_tif = "test_.tif"

is_cog = cog_validate(input_tif)

# True if the file is a valid COG, False otherwise
print("COG:", is_cog)