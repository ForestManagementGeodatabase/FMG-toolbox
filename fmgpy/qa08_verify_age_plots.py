# -*- coding: UTF-8 -*-

import arcpy
from os.path import split, join
from fmglib import clean_inputs

# get parameter arguments for script tool
fc_center = arcpy.GetParameterAsText(0)
center_plot_id_field = arcpy.GetParameterAsText(1)
age_flag_field = arcpy.GetParameterAsText(2)
fc_age = arcpy.GetParameterAsText(3)
age_plot_id = arcpy.GetParameterAsText(4)

# check if input is a file path or feature layer, if layer, get file path
if not split(fc_center)[0]:
    fc_center = join(arcpy.Describe(fc_center).path, arcpy.Describe(fc_center).name)
if not split(fc_age)[0]:
    fc_age = join(arcpy.Describe(fc_age).path, arcpy.Describe(fc_age).name)

# verify required age trees have been collected
result = clean_inputs.check_contractor_age_plots(fc_center, center_plot_id_field, age_flag_field, fc_age, age_plot_id)

arcpy.SetParameterAsText(5, result)

                                                  
                                                  
