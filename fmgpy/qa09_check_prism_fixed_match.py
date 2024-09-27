# -*- coding: UTF-8 -*-

import arcpy
from os.path import split, join
from fmglib import clean_inputs

# get parameter arguments for script tool
fc_prism = arcpy.GetParameterAsText(0)
prism_plot_id = arcpy.GetParameterAsText(1)
fc_fixed = arcpy.GetParameterAsText(2)
fixed_plot_id = arcpy.GetParameterAsText(3)
in_gdb = arcpy.Describe(fc_prism).path

# check if input is a file path or feature layer, if layer, get file path
if not split(fc_prism)[0]:
    fc_prism = join(arcpy.Describe(fc_prism).path, arcpy.Describe(fc_prism).name)

if not split(fc_fixed)[0]:
    fc_fixed = join(arcpy.Describe(fc_fixed).path, arcpy.Describe(fc_fixed).name)

# check each fixed plot has a prism plot and each prism plot has a fixed plot
result = clean_inputs.check_prism_fixed(fc_prism, prism_plot_id, fc_fixed, fixed_plot_id, in_gdb)

out_prism = result[0]
arcpy.SetParameterAsText(4, out_prism)

out_fixed = result[1]
arcpy.SetParameterAsText(5, out_fixed)


                                         
