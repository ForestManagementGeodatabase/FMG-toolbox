# -*- coding: UTF-8 -*-

import arcpy
from os.path import split, join
from fmglib import clean_inputs
import importlib

importlib.reload(clean_inputs)

# run this tool AFTER running check_plot_ids

# get parameter arguments for script tool
fc_center = arcpy.GetParameterAsText(0)
center_plot_id_field = arcpy.GetParameterAsText(1)
fc_fixed = arcpy.GetParameterAsText(2)
fixed_plot_id_field = arcpy.GetParameterAsText(3)
in_gdb = arcpy.Describe(fc_center).path

# check if input is a file path or feature layer, if layer, get file path
if not split(fc_center)[0]:
    fc_center = join(arcpy.Describe(fc_center).path, arcpy.Describe(fc_center).name)

if not split(fc_fixed)[0]:
    fc_fixed = join(arcpy.Describe(fc_fixed).path, arcpy.Describe(fc_fixed).name)

# check fixed plot offset from plot centers
result = clean_inputs.check_fixed_center(fc_center, center_plot_id_field, fc_fixed, fixed_plot_id_field, in_gdb)

arcpy.SetParameterAsText(4, result)
