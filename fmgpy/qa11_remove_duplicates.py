# -*- coding: UTF-8 -*-

import arcpy
from os.path import split, join
from fmglib import clean_inputs

# get parameter arguments for script tool
fc_prism = arcpy.GetParameterAsText(0)
fc_fixed = arcpy.GetParameterAsText(1)
fc_age = arcpy.GetParameterAsText(2)
fc_center = arcpy.GetParameterAsText(3)

# check if input is a file path or feature layer, if layer, get file path
if not split(fc_prism)[0]:
    fc_prism = join(arcpy.Describe(fc_prism).path, arcpy.Describe(fc_prism).name)

if not split(fc_fixed)[0]:
    fc_fixed = join(arcpy.Describe(fc_fixed).path, arcpy.Describe(fc_fixed).name)

if not split(fc_age)[0]:
    fc_age = join(arcpy.Describe(fc_age).path, arcpy.Describe(fc_age).name)

if not split(fc_center)[0]:
    fc_center = join(arcpy.Describe(fc_center).path, arcpy.Describe(fc_center).name)

result = clean_inputs.remove_duplicates(fc_prism, fc_fixed, fc_age, fc_center)

out_prism = result[0]
arcpy.SetParameterAsText(4, out_prism)
out_fixed = result[1]
arcpy.SetParameterAsText(5, out_fixed)
out_age = result[2]
arcpy.SetParameterAsText(6, out_age)
out_center = result[3]
arcpy.SetParameterAsText(7, out_center)
