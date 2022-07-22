# -*- coding: UTF-8 -*-

import arcpy
from clean_inputs import check_fixed_center

# run this tool AFTER running check_plot_ids

# Get Parameter arguments for script tool
fc_center = arcpy.GetParameterAsText(0)
center_plot_id_field = arcpy.GetParameterAsText(1)
fc_fixed = arcpy.GetParameterAsText(2)
fixed_plot_id_field = arcpy.GetParameterAsText(3)
in_gdb = arcpy.GetParameterAsText(4)

# Check fixed plot offset from plot centers
check_fixed_center(fc_center, center_plot_id_field, fc_fixed, fixed_plot_id_field, in_gdb)
