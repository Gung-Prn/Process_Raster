from osgeo import gdal
import os
import subprocess

# ==============================
# CONFIG
# ==============================
input_tif = "output/data.tif"
base_output_dir = "temp/out_compress_test"

compressions = {
    "ZSTD": {"level_opt": "ZSTD_LEVEL", "level": 7},
    "LZW": {"level_opt": None, "level": None},
    "DEFLATE": {"level_opt": "ZLEVEL", "level": 6},
}

blocksizes = [128, 256, 512, 1024]

overview_levels = [2, 4, 8, 16, 32]

os.makedirs(base_output_dir, exist_ok=True)

# ==============================
# PROCESS
# ==============================
for comp, cfg in compressions.items():
    comp_dir = os.path.join(base_output_dir, comp.lower())
    os.makedirs(comp_dir, exist_ok=True)

    for bs in blocksizes:
        out_tif = os.path.join(
            comp_dir,
            f"out_{comp.lower()}_block{bs}.tif"
        )

        if os.path.exists(out_tif):
            os.remove(out_tif)

        # ---------- gdal_translate ----------
        translate_cmd = [
            "gdal_translate",
            input_tif,
            out_tif,
            "-co", f"COMPRESS={comp}",
            "-co", "TILED=YES",
            "-co", f"BLOCKXSIZE={bs}",
            "-co", f"BLOCKYSIZE={bs}",
            "-co", "COPY_SRC_OVERVIEWS=NO"
        ]

        if cfg["level_opt"]:
            translate_cmd.extend([
                "-co", f"{cfg['level_opt']}={cfg['level']}"
            ])

        print("Running:", " ".join(translate_cmd))
        subprocess.run(translate_cmd, check=True)

        # ---------- gdaladdo ----------
        addo_cmd = [
            "gdaladdo",
            "-r", "average",
            "--config", "COMPRESS_OVERVIEW", comp,
            "--config", "BIGTIFF_OVERVIEW", "IF_SAFER",
        ]

        if cfg["level_opt"]:
            addo_cmd.extend([
                "--config", cfg["level_opt"], str(cfg["level"])
            ])

        addo_cmd.append(out_tif)
        addo_cmd.extend(map(str, overview_levels))

        print("Running:", " ".join(addo_cmd))
        subprocess.run(addo_cmd, check=True)

        print(f"Created: {out_tif}")

print("All combinations finished")
