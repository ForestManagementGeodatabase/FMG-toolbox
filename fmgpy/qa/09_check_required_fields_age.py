# -*- coding: UTF-8 -*-

import arcpy
from clean_inputs import check_required_fields_age

# Get Parameter arguments for script tool
fc_age = arcpy.GetParameterAsText(0)
species_name = arcpy.GetParameterAsText(1)
dia_name = arcpy.GetParameterAsText(2)
height_name = arcpy.GetParameterAsText(3)
orig_name = arcpy.GetParameterAsText(4)
grw_name = arcpy.GetParameterAsText(5)
crew_name = arcpy.GetParameterAsText(6)
date_name = arcpy.GetParameterAsText(7)

# Check each field collected dataset for required fields
check_required_fields_age(fc_age, species_name, dia_name, height_name, orig_name, grw_name, crew_name, date_name)
