# -*- coding: UTF-8 -*-

import arcpy
from clean_inputs import check_required_fields_prism

# Get Parameter arguments for script tool
fc_prism = arcpy.GetParameterAsText(0)
species_name = arcpy.GetParameterAsText(1)
dia_name = arcpy.GetParameterAsText(2)
class_name = arcpy.GetParameterAsText(3)
health_name = arcpy.GetParameterAsText(4)
crew_name = arcpy.GetParameterAsText(5)
date_name = arcpy.GetParameterAsText(6)

# Check each field collected dataset for required fields
check_required_fields_prism(fc_prism, species_name, dia_name, class_name, health_name, crew_name, date_name)
