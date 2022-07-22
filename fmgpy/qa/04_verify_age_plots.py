# -*- coding: UTF-8 -*-

import arcpy
from clean_inputs import check_contractor_age_plots

# Get Parameter arguments for script tool
fc_center = arcpy.GetParameterAsText(0)
center_plot_id_field = arcpy.GetParameterAsText(1)
age_flag_field = arcpy.GetParameterAsText(2)
fc_age = arcpy.GetParameterAsText(3)
age_plot_id = arcpy.GetParameterAsText(4)

# Verify required age trees have been collected
check_contractor_age_plots(fc_center, center_plot_id_field, age_flag_field, fc_age, age_plot_id)

                                                  
                                                  
