# -*- coding: UTF-8 -*-

import arcpy
from os.path import split, join
from clean_inputs import check_required_fields_fixed

# get parameter arguments for script tool
fc_fixed = arcpy.GetParameterAsText(0)
plot_name = arcpy.GetParameterAsText(1)
closure_name = arcpy.GetParameterAsText(2)
height_name = arcpy.GetParameterAsText(3)
un_ht_name = arcpy.GetParameterAsText(4)
un_cover_name = arcpy.GetParameterAsText(5)
un_sp_name = arcpy.GetParameterAsText(6)
gr_sp_name = arcpy.GetParameterAsText(7)
crew_name = arcpy.GetParameterAsText(8)
date_name = arcpy.GetParameterAsText(9)

# check if input is a file path or feature layer, if layer, get file path
if not split(fc_fixed)[0]:
    fc_fixed = join(arcpy.Describe(fc_fixed).path, arcpy.Describe(fc_fixed).name)

# check each field collected dataset for required fields
result = check_required_fields_fixed(fc_fixed, plot_name, closure_name, height_name, un_ht_name, un_cover_name,
                                     un_sp_name, gr_sp_name, crew_name, date_name)

arcpy.SetParameterAsText(10, result)
