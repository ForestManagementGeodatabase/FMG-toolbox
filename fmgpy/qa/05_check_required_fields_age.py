# -*- coding: UTF-8 -*-

import arcpy
from os.path import split, join
from clean_inputs import check_required_fields_age

# get parameter arguments for script tool
fc_age = arcpy.GetParameterAsText(0)
plot_name = arcpy.GetParameterAsText(1)
species_name = arcpy.GetParameterAsText(2)
dia_name = arcpy.GetParameterAsText(3)
height_name = arcpy.GetParameterAsText(4)
orig_name = arcpy.GetParameterAsText(5)
grw_name = arcpy.GetParameterAsText(6)
crew_name = arcpy.GetParameterAsText(7)
date_name = arcpy.GetParameterAsText(8)

# check if input is a file path or feature layer, if layer, get file path
if not split(fc_age)[0]:
    fc_age = join(arcpy.Describe(fc_age).path, arcpy.Describe(fc_age).name)

# check each field collected dataset for required fields
result = check_required_fields_age(fc_age, plot_name, species_name, dia_name, height_name,
                                   orig_name, grw_name, crew_name, date_name)

arcpy.SetParameterAsText(9, result)
