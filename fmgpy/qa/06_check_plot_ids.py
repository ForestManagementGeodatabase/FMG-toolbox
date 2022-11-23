# -*- coding: UTF-8 -*-

import arcpy
from os.path import split, join
from clean_inputs import check_plot_ids

# get parameter arguments for script tool
fc_center = arcpy.GetParameterAsText(0)
center_plot_id_field = arcpy.GetParameterAsText(1)
fc_prism = arcpy.GetParameterAsText(2)
prism_plot_id_field = arcpy.GetParameterAsText(3)
fc_fixed = arcpy.GetParameterAsText(4)
fixed_plot_id_field = arcpy.GetParameterAsText(5)
fc_age = arcpy.GetParameterAsText(6)
age_plot_id_field = arcpy.GetParameterAsText(7)

# check if input is a file path or feature layer, if layer, get file path
if not split(fc_center)[0]:
    fc_center = join(arcpy.Describe(fc_center).path, arcpy.Describe(fc_center).name)

if not split(fc_prism)[0]:
    fc_prism = join(arcpy.Describe(fc_prism).path, arcpy.Describe(fc_prism).name)

if not split(fc_fixed)[0]:
    fc_fixed = join(arcpy.Describe(fc_fixed).path, arcpy.Describe(fc_fixed).name)

if not split(fc_age)[0]:
    fc_age = join(arcpy.Describe(fc_age).path, arcpy.Describe(fc_age).name)

# check plot IDs - PRISM
result_prism = check_plot_ids(fc_center,
                              center_plot_id_field,
                              fc_prism,
                              prism_plot_id_field)

arcpy.SetParameterAsText(8, result_prism)

# check plot IDs - FIXED
result_fixed = check_plot_ids(fc_center,
                              center_plot_id_field,
                              fc_fixed,
                              fixed_plot_id_field)

arcpy.SetParameterAsText(9, result_fixed)

# check plot IDs - AGE
result_age = check_plot_ids(fc_center,
                            center_plot_id_field,
                            fc_age,
                            age_plot_id_field)

arcpy.SetParameterAsText(10, result_age)

arcpy.SetParameterAsText(11, fc_center)
