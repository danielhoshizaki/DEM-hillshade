# -*- coding: UTF-8 -*-
# Author: Daniel Hoshizaki

# Operating System Commands
from os.path import join, basename, normpath, isfile, isdir, splitext, dirname, exists, abspath, realpath
from os import listdir, rename, remove, mkdir, walk, rmdir, environ, getcwd
import sys, shutil, subprocess
from pathlib import Path

# XML processing and converting into GeoTiff
from bs4 import BeautifulSoup as bs
import numpy as np
from osgeo import gdal, gdal_array, osr, ogr
from zipfile import ZipFile

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

def get_cwd():
    try:
        cwd = dirname(realpath(__file__))
    except:
        cwd = getcwd()
    return cwd

if __name__ == "__main__":

    cwd = get_cwd()
    base = Path(join(cwd, "data"))
    from_dir = Path(join(cwd, "data/raw"))
    to_dir = Path(join(cwd, "data/processed"))
    hillshade_dir = Path(join(cwd, "data/hillshade"))

    qgis_bin_path = "C:/Program Files/QGIS 3.10/bin"
    gdaldem_path = Path(join(qgis_bin_path, "gdaldem.exe"))
    vrt_path = Path(join(qgis_bin_path, "gdalbuildvrt.exe"))
    tiles_path = Path("C:/Program Files/QGIS 3.10/apps/Python37/Scripts/gdal2tiles.py")

    hillshade_vrt_path = Path(join(hillshade_dir, "hillshade.vrt"))
    WTMS_path = Path(join(base, "WTMS"))

    if not isdir(to_dir):
        mkdir(to_dir)

    if not isdir(hillshade_dir):
        mkdir(hillshade_dir)


    for folder in listdir(from_dir):
        if folder.endswith(".zip"):

            source_directory = join(from_dir, folder)
            zipfile = ZipFile(source_directory)

            for file in zipfile.namelist():
                if file.endswith(".xml"):

                    #new name uses DEM description followed by a grid number#
                    split_name = file.split('-')
                    new_file_name = f"{split_name[2]}_{split_name[3]}.tiff"
                    new_file_destination = join(to_dir, new_file_name)

                    zipped_xml = zipfile.open(file)
                    xml = bs(zipped_xml, 'lxml-xml')

                    # Extract target metadata from the XML file
                    # Use metadata to create a GeoTiff output
                    height, width = get_dimensions(xml)
                    required_length = height * width
                    data_array = get_data(xml, required_length)
                    elevation_matrix = data_array.reshape((width, height)) # use the obtained dimensions
                    geo_transform = get_geotransform(xml, width, height)

                    # Create the raster file
                    driver = gdal.GetDriverByName('GTiff') # specify the file type
                    outRaster = driver.Create(new_file_destination, height, width, 1, gdal.GDT_Float32)

                    # Lock the raster to the bounding box coordinates
                    outRaster.SetGeoTransform(geo_transform)

                    # Set the projection of the output raster
                    outRasterSRS = osr.SpatialReference()
                    outRasterSRS.ImportFromEPSG(6668)
                    outRaster.SetProjection(outRasterSRS.ExportToWkt())

                    # Burn the data
                    outband = outRaster.GetRasterBand(1)
                    outband.WriteArray(elevation_matrix, 0, 0)
                    outband.FlushCache()
                    outband.SetNodataValue(-9999)

                    del outRaster, outband

                    print(file, "processing complete")


    command = f'for %f in ("{to_dir}\*.tif") do ("{gdaldem_path}" hillshade -s 50000 %f "{hillshade_dir}/%~nf_hillshade.tif" -compute_edges)'
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    process.communicate()
    print("\nFinished converting DEM to hillshade")

    command = f'"{vrt_path}" "{hillshade_vrt_path}" "{hillshade_dir}\*_hillshade.tif"'
    process = subprocess.Popen(command,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            shell=True)
    process.communicate()
    print("Merged all hillshade files into a VRT")

    command = f'python "{tiles_path}" -z 0-12 --processes 4 "{hillshade_vrt_path}" "{WTMS_path}"'
    process = subprocess.Popen(command,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            shell=True)
    process.communicate()
    print("Converted VRT to WTMS folder")
