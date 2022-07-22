import os
import sys
import arcpy
import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor

arcpy.env.overwriteOutput = True