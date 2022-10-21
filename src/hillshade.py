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
""" XML DEM data converter for generating hillshade GeoTIFF """

import os
import subprocess
from pathlib import Path
from multiprocessing import Pool
from bs4 import BeautifulSoup as bs
import numpy as np
from osgeo import gdal, osr
from zipfile import ZipFile
from loguru import logger


def format_lat_lon(string):
    # Accepts a string lat long seperated by a single space
    split_string = string.split(' ')
    lat = split_string[0]
    lon = split_string[1]

    return float(lat), float(lon)


def get_dimensions(xml):
    height_width_string = xml.find('gml:high').text.split(' ')
    height = int(height_width_string[0]) + 1 # number of rows, y
    width = int(height_width_string[1]) + 1 # number of columns, x
    return height, width


def get_data(xml, required_length):
    # get the data as an array
    data = xml.find('gml:tupleList')
    # get the elevation data and turn into into a numpy matrix
    elevation_array = np.array([float(row.split(',')[1]) for row in data.text.split('\n') if len(row) > 0])

    # Run a dimension check
    if len(elevation_array) != required_length:
        missing_n_elements = required_length - len(elevation_array)
        missing_elements = np.array(missing_n_elements * [-9999.0])

        elevation_array = np.concatenate((elevation_array, missing_elements), axis=0)

    return elevation_array


def get_geotransform(xml, width, height):
    # get the coordinates of the data
    lower_corner = xml.find('gml:lowerCorner').text # in string format, lat long seperated by space
    upper_corner = xml.find('gml:upperCorner').text # in string format, lat long seperated by space

    lower_lat, lower_long = format_lat_lon(lower_corner)
    upper_lat, upper_long = format_lat_lon(upper_corner)

    x_resolution = (upper_long - lower_long) / float(height)
    y_resolution = (upper_lat - lower_lat) / float(width)

    geo_transform = (lower_long, x_resolution, 0, upper_lat, 0, -y_resolution)

    return geo_transform


def convert(source_directory: Path, to_dir: Path) -> None:
    """Convert all XML files from source directory to GeoTiffs 
    in the output directory"""

    # Unzip the data folder
    zipfile = ZipFile(source_directory)

    for f in zipfile.namelist():
        if f.endswith(".xml"):

            # Create an output path
            split_name = f.split('-')
            new_file_name = f"{split_name[2]}_{split_name[3]}.tif"
            new_file_destination = to_dir / new_file_name

            # Extract target metadata from the source XML file
            zipped_xml = zipfile.open(f)
            xml = bs(zipped_xml, 'lxml-xml')

            # Use metadata to create a GeoTiff output
            height, width = get_dimensions(xml)
            required_length = height * width
            data_array = get_data(xml, required_length)
            elevation_matrix = data_array.reshape((width, height)) # use the obtained dimensions
            geo_transform = get_geotransform(xml, width, height)

            # Create the raster file
            driver = gdal.GetDriverByName('GTiff') # specify the file type
            outRaster = driver.Create(new_file_destination.as_posix(), height, width, 1, gdal.GDT_Float32)

            # Set the projection of the output raster
            outRaster.SetGeoTransform(geo_transform)
            outRasterSRS = osr.SpatialReference()
            outRasterSRS.ImportFromEPSG(6668)
            outRaster.SetProjection(outRasterSRS.ExportToWkt())

            # Burn the data
            outband = outRaster.GetRasterBand(1)
            outband.WriteArray(elevation_matrix, 0, 0)
            outband.FlushCache()
            outband.SetNoDataValue(-9999)

            # Close the file
            del outRaster, outband
            logger.info(f, "processing complete")


def hillshade(f: Path, to_dir: Path) -> None:
    output_path = to_dir / f.name
    command = f'gdaldem hillshade -s 50000 {f.as_posix()} {output_path.as_posix()} -compute_edges'
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

    # Set up the directory paths to where the zipped XML files are and where the converted
    # GeoTiffs will be placed
    from_dir = base / "raw"
    to_dir = base / "processed"

    # Make the required output folder if it is not present
    os.makedirs(to_dir, exist_ok=True)

    # Convert all zipped XMLs to GeoTiffs
    targets = []
    for folder in from_dir.iterdir():
        if folder.name.endswith(".zip"):
            targets.append((folder, to_dir))
    
    with Pool(POOL) as pool:
        results = pool.starmap(convert, targets)

    # Set up the paths for rendering the new GeoTiff files
    hillshade_dir = base / "hillshade"

    # Create the hillshade folder if it does not exist
    os.makedirs(hillshade_dir, exist_ok=True)

    # Use Python to rigger GDAL commands in the command line
    # Convert the DEM to a hillshade raster
    targets = [(f, hillshade_dir) for f in to_dir.iterdir()]

    with Pool(POOL) as pool:
        pool.starmap(hillshade, targets)

    # Done with hillshade logic
    logger.info("Done creating hillshade files")