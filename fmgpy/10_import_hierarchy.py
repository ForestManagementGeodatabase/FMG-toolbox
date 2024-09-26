# -*- coding: UTF-8 -*-

import arcpy
import importlib
from os.path import split, join
from fmglib import clean_inputs

importlib.reload(clean_inputs)

# get parameter arguments for script tool
fc_polygons = arcpy.GetParameterAsText(0)
fc_center = arcpy.GetParameterAsText(1)
fc_prism = arcpy.GetParameterAsText(2)
fc_fixed = arcpy.GetParameterAsText(3)
fc_age = arcpy.GetParameterAsText(4)
pool = arcpy.GetParameterAsText(5)
comp = arcpy.GetParameterAsText(6)
unit = arcpy.GetParameterAsText(7)
site = arcpy.GetParameterAsText(8)
stand = arcpy.GetParameterAsText(9)

# check if input is a file path or feature layer, if layer, get file path
if not split(fc_polygons)[0]:
    fc_polygons = join(arcpy.Describe(fc_polygons).path, arcpy.Describe(fc_polygons).name)

if not split(fc_center)[0]:
    fc_center = join(arcpy.Describe(fc_center).path, arcpy.Describe(fc_center).name)

if not split(fc_prism)[0]:
    fc_prism = join(arcpy.Describe(fc_prism).path, arcpy.Describe(fc_prism).name)

if not split(fc_fixed)[0]:
    fc_fixed = join(arcpy.Describe(fc_fixed).path, arcpy.Describe(fc_fixed).name)

if not split(fc_age)[0]:
    fc_age = join(arcpy.Describe(fc_age).path, arcpy.Describe(fc_age).name)

result = clean_inputs.import_hierarchy(fc_polygons, fc_center, fc_prism, fc_fixed, fc_age, pool, comp, unit, site, stand)

out_polygons = result[0]
arcpy.SetParameterAsText(10, out_polygons)
out_center = result[1]
arcpy.SetParameterAsText(11, out_center)
out_prism = result[2]
arcpy.SetParameterAsText(12, out_prism)
out_fixed = result[3]
arcpy.SetParameterAsText(13, out_fixed)
out_age = result[4]
arcpy.SetParameterAsText(14, out_age)
