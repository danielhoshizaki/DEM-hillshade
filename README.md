# DEM Raster File Converter
#### Transforming Open Source GIS Data

[![](./docs/hillshade.PNG)](https://danielhoshizaki.github.io/hillshade/)

### Purpose
This projects provides a convenient way to convert open source GIS data provided by the <a href="https://fgd.gsi.go.jp/download/menu.php">Geospatial Information Authority of Japan</a>. The primary function of this project is to provide a method for automatically converting the raw data source (a zipped XML file) into GIS software and web compatible formats. The final output is a WTMS folder that contains tiled hill shade PNG files. A section of the gml_to_wtms.py script can easily be modified to only output GeoTiff files from the raw data files.
