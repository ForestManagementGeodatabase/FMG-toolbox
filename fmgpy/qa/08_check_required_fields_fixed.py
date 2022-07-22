# -*- coding: UTF-8 -*-

import arcpy
from clean_inputs import check_required_fields_fixed

# Get Parameter arguments for script tool
fc_fixed = arcpy.GetParameterAsText(0)
closure_name = arcpy.GetParameterAsText(1)
height_name = arcpy.GetParameterAsText(2)
un_ht_name = arcpy.GetParameterAsText(3)
un_cover_name = arcpy.GetParameterAsText(4)
un_sp_name = arcpy.GetParameterAsText(5)
gr_sp_name = arcpy.GetParameterAsText(6)
crew_name = arcpy.GetParameterAsText(7)
date_name = arcpy.GetParameterAsText(8)

# Check each field collected dataset for required fields
check_required_fields_fixed(fc_fixed, closure_name, height_name, un_ht_name, un_cover_name, un_sp_name, gr_sp_name,
                            crew_name, date_name)
