from rio_cogeo.cogeo import cog_validate
            
input_tif = "test_.tif"

is_cog = cog_validate(input_tif)

# True if the file is a valid COG, False otherwise
print("COG:", is_cog)



# Comparing The COGs

import os
import time
import rasterio
import pandas as pd

# =========================
# CONFIG
# =========================
baseline = "output/69006a3bbe4e87ecda5c176e.tif"
test_root = "temp/out_compress_test"

compressions = ["zstd", "lzw", "deflate"]
blocksizes = [128, 256, 512, 1024]
n_reads = 100

report = []

# =========================
# BASELINE SIZE
# =========================
baseline_size = os.path.getsize(baseline)

# =========================
# BENCHMARK FUNCTION
# =========================
def benchmark_read(path, blocksize):
    with rasterio.open(path) as ds:
        w = h = blocksize
        max_x = ds.width - w
        max_y = ds.height - h

        start = time.time()
        for i in range(n_reads):
            x = (i * w) % max_x
            y = (i * h) % max_y
            window = rasterio.windows.Window(x, y, w, h)
            ds.read(1, window=window)
        end = time.time()

    return (end - start) / n_reads * 1000  # ms/read

# =========================
# PROCESS
# =========================
for comp in compressions:
    for bs in blocksizes:
        path = f"{test_root}/{comp}/out_{comp}_block{bs}.tif"

        if not os.path.exists(path):
            continue

        size = os.path.getsize(path)
        reduction = (1 - size / baseline_size) * 100

        io_ms = benchmark_read(path, bs)

        report.append({
            "compression": comp.upper(),
            "blocksize": bs,
            "filesize_mb": round(size / 1024 / 1024, 2),
            "reduction_%": round(reduction, 2),
            "avg_read_ms": round(io_ms, 2),
        })

# =========================
# REPORT
# =========================
df = pd.DataFrame(report)
df = df.sort_values(["compression", "blocksize"])

print(df)
df.to_csv("temp/cog_benchmark_report.csv", index=False)
