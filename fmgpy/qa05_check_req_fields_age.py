# -*- coding: UTF-8 -*-

import arcpy
from os.path import split, join
from fmglib import clean_inputs

# get parameter arguments for script tool
fc_age = arcpy.GetParameterAsText(0)
plot_name = arcpy.GetParameterAsText(1)
species_name = arcpy.GetParameterAsText(2)
dia_name = arcpy.GetParameterAsText(3)
height_name = arcpy.GetParameterAsText(4)
orig_name = arcpy.GetParameterAsText(5)
grw_name = arcpy.GetParameterAsText(6)
misc_name = arcpy.GetParameterAsText(7)
crew_name = arcpy.GetParameterAsText(8)
date_name = arcpy.GetParameterAsText(9)

# check if input is a file path or feature layer, if layer, get file path
if not split(fc_age)[0]:
    fc_age = join(arcpy.Describe(fc_age).path, arcpy.Describe(fc_age).name)

# check each field collected dataset for required fields
result = clean_inputs.check_required_fields_age(fc_age, plot_name, species_name, dia_name, height_name,
                                                orig_name, grw_name, misc_name, crew_name, date_name)

arcpy.SetParameterAsText(10, result)
