# -*- coding: UTF-8 -*-

import arcpy
from os.path import split, join
from fmglib import clean_inputs
import importlib

importlib.reload(clean_inputs)

# get parameter arguments for script tool
fc_prism = arcpy.GetParameterAsText(0)
plot_name = arcpy.GetParameterAsText(1)
species_name = arcpy.GetParameterAsText(2)
dia_name = arcpy.GetParameterAsText(3)
class_name = arcpy.GetParameterAsText(4)
health_name = arcpy.GetParameterAsText(5)
misc_name = arcpy.GetParameterAsText(6)
crew_name = arcpy.GetParameterAsText(7)
date_name = arcpy.GetParameterAsText(8)

# check if input is a file path or feature layer, if layer, get file path
if not split(fc_prism)[0]:
    fc_prism = join(arcpy.Describe(fc_prism).path, arcpy.Describe(fc_prism).name)

# check each field collected dataset for required fields
result = clean_inputs.check_required_fields_prism(fc_prism, plot_name, species_name, dia_name,
                                                  class_name, health_name, misc_name, crew_name, date_name)

arcpy.SetParameterAsText(9, result)
