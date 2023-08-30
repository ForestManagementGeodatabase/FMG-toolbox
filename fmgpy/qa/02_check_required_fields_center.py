# -*- coding: UTF-8 -*-

import arcpy
import importlib
from os.path import split, join
import clean_inputs

importlib.reload(clean_inputs)

# get parameter arguments for script tool
fc_center = arcpy.GetParameterAsText(0)
plot_name = arcpy.GetParameterAsText(1)
flag_name = arcpy.GetParameterAsText(2)

# check if input is a file path or feature layer, if layer, get file path
if not split(fc_center)[0]:
    fc_center = join(arcpy.Describe(fc_center).path, arcpy.Describe(fc_center).name)

# check each field collected dataset for required fields
result = clean_inputs.check_required_fields_center(fc_center, plot_name, flag_name)

arcpy.SetParameterAsText(3, result)
