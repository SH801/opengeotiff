# OpenGeoTIFF - library for processing GeoTIFF files

## Overview
The `OpenGeoTIFF` library provides a simple command line interface for automatically retrieving GeoTIFF images from a remote data repository and then processing the image to produce vectorized GKPG files. 

A `yml` configuration file is used to provide key parameters to the library.

## Key features

- Run simple binary processing through `min` and `max` settings.
- Clip to a user-supplied outline.

## Installation

```
pip install git+https://github.com/SH801/opengeotiff.git
```

To use the library, enter:

```
opengeotiff /path/to/conf.yml
```

## Configuration file

The `.yml` configuration file should have the following format:

```
# ----------------------------------------------------
# sample.yml
# Sample yml configuration file
# ----------------------------------------------------

# Link to this GitHub code repository 
# This can be used to host yml files on an open data server and automatically install required library just-in-time
codebase:
  https://github.com/SH801/opengeotiff.git

# Link to GeoTIFF image which may be zipped
source:
  https://s3.amazonaws.com/elevation-tiles-prod/terrarium/${z}/${x}/${y}.png

# Directory where downloaded tiles and temporary data are stored
cache_dir:
  ./tile_cache

# Bounding box in WGS84 coordinates: [min_lon, min_lat, max_lon, max_lat]
bounds:
  [-9.0, 49.0, 2.0, 61.0]

# External URL or path to a geometry file used to crop the output to a specific shape
clipping:
  https://github.com/open-wind/openwindenergy/raw/refs/heads/main/overall-clipping.gpkg

# The exact name and extension of the final file generated
output:
  insufficient-solar-irradiation--uk.gpkg

# Filters the final result values, e.g. degrees for slope
mask:
  # Minimum excessive slope is 5 degrees
  min: 
    5.001
  
  # Maxium excessive slope is 90 degrees
  max: 
    100
```

## Possible uses

- Generating areas with insufficient solar irradiation for solar farm siting.

