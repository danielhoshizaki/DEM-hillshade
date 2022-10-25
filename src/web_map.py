# coding=utf-8
# Copyright 2022 Daniel Hoshizaki. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" Hillshade GeoTIFF to WMTS converter"""

import os
import subprocess
from pathlib import Path
from multiprocessing import Pool
from loguru import logger


def reproject(f: Path, to_dir: Path) -> None:
    output_path = to_dir / f.name
    command = f'gdalwarp -t_srs EPSG:3857 {f.as_posix()} {output_path.as_posix()}'
    subprocess.run(
        command,
        shell=True,
        check=True,
        stdout=open(os.devnull, "w"),
        stderr=subprocess.STDOUT,
    )
    logger.info(f.name, "done")


if __name__ == "__main__":

    # Thread count for all tasks
    POOL = 8

    # File system paths for processing temporary files as well as the final output folder
    cwd = Path(__file__).resolve().parent.parent
    base = cwd / "data"
    
    # Set up the paths for rendering the new GeoTiff files
    hillshade_dir = base / "hillshade"
    reproject_dir = base / "reproject"
    vrt_path = reproject_dir / "merge.vrt"

    os.makedirs(reproject_dir, exist_ok=True)

    # Reproject all files to web mercator
    # Convert all zipped XMLs to GeoTiffs
    targets = []
    for f in hillshade_dir.iterdir():
        if not (reproject_dir / f.name).exists():
            targets.append((f, reproject_dir))
    
    with Pool(POOL) as pool:
        results = pool.starmap(reproject, targets)

    # Merge all raster files into a VRT
    command = f'gdalbuildvrt {vrt_path.as_posix()} {reproject_dir.as_posix()}/*.tif'
    subprocess.run(
        command,
        shell=True,
        check=True,
        stdout=open(os.devnull, "w"),
        stderr=subprocess.STDOUT,
    )
    logger.info("Merged all hillshade files into a VRT")

    # Convert the VRT file into a WTMS data folder
    WTMS_path = base / "WTMS"

    command = f'python3 /usr/bin/gdal2tiles.py -z 0-12  --processes {POOL} {vrt_path.as_posix()} {WTMS_path.as_posix()}'
    subprocess.run(
        command,
        shell=True,
        check=True,
        stdout=open(os.devnull, "w"),
        stderr=subprocess.STDOUT,
    )
    logger.info("Converted VRT to WTMS folder")
    logger.info("Processing complete")
