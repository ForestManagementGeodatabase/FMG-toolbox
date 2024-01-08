# -*- coding: UTF-8 -*-

import arcpy
import importlib
from os.path import split, join
import clean_inputs

importlib.reload(clean_inputs)

# get parameter arguments for script tool

# fc center
fc_center = arcpy.GetParameterAsText(0)
center_plot_name = arcpy.GetParameterAsText(1)
center_flag_name = arcpy.GetParameterAsText(2)
in_gdb = arcpy.Describe(fc_center).path

# fc prism
fc_prism = arcpy.GetParameterAsText(3)
prism_plot_name = arcpy.GetParameterAsText(4)
prism_species_name = arcpy.GetParameterAsText(5)
prism_dia_name = arcpy.GetParameterAsText(6)
prism_class_name = arcpy.GetParameterAsText(7)
prism_health_name = arcpy.GetParameterAsText(8)
prism_misc_name = arcpy.GetParameterAsText(9)
prism_crew_name = arcpy.GetParameterAsText(10)
prism_date_name = arcpy.GetParameterAsText(11)

# fc fixed
fc_fixed = arcpy.GetParameterAsText(12)
fixed_plot_name = arcpy.GetParameterAsText(13)
fixed_closure_name = arcpy.GetParameterAsText(14)
fixed_height_name = arcpy.GetParameterAsText(15)
fixed_un_ht_name = arcpy.GetParameterAsText(16)
fixed_un_cover_name = arcpy.GetParameterAsText(17)
fixed_un_sp_name = arcpy.GetParameterAsText(18)
fixed_gr_sp_name = arcpy.GetParameterAsText(19)
fixed_misc_name = arcpy.GetParameterAsText(20)
fixed_crew_name = arcpy.GetParameterAsText(21)
fixed_date_name = arcpy.GetParameterAsText(22)

# fc age
fc_age = arcpy.GetParameterAsText(23)
age_plot_name = arcpy.GetParameterAsText(24)
age_species_name = arcpy.GetParameterAsText(25)
age_dia_name = arcpy.GetParameterAsText(26)
age_height_name = arcpy.GetParameterAsText(27)
age_orig_name = arcpy.GetParameterAsText(28)
age_grw_name = arcpy.GetParameterAsText(29)
age_misc_name = arcpy.GetParameterAsText(30)
age_crew_name = arcpy.GetParameterAsText(31)
age_date_name = arcpy.GetParameterAsText(32)

# fmg polygons
fc_polygons = arcpy.GetParameterAsText(33)
pool = arcpy.GetParameterAsText(34)
comp = arcpy.GetParameterAsText(35)
unit = arcpy.GetParameterAsText(36)
site = arcpy.GetParameterAsText(37)
stand = arcpy.GetParameterAsText(38)

# check if input is a file path or feature layer, if layer, get file path
if not split(fc_center)[0]:
    fc_center = join(arcpy.Describe(fc_center).path, arcpy.Describe(fc_center).name)

if not split(fc_prism)[0]:
    fc_prism = join(arcpy.Describe(fc_prism).path, arcpy.Describe(fc_prism).name)

if not split(fc_fixed)[0]:
    fc_fixed = join(arcpy.Describe(fc_fixed).path, arcpy.Describe(fc_fixed).name)

if not split(fc_age)[0]:
    fc_age = join(arcpy.Describe(fc_age).path, arcpy.Describe(fc_age).name)

# check each field collected dataset for required fields
clean_inputs.check_required_fields_center(fc_center, center_plot_name, center_flag_name)
clean_inputs.check_required_fields_prism(fc_prism, prism_plot_name, prism_species_name, prism_dia_name,
                                         prism_class_name, prism_health_name, prism_misc_name, prism_crew_name,
                                         prism_date_name)
clean_inputs.check_required_fields_fixed(fc_fixed, fixed_plot_name, fixed_closure_name, fixed_height_name,
                                         fixed_un_ht_name, fixed_un_cover_name, fixed_un_sp_name,
                                         fixed_gr_sp_name, fixed_misc_name, fixed_crew_name,
                                         fixed_date_name)
clean_inputs.check_required_fields_age(fc_age, age_plot_name, age_species_name, age_dia_name,
                                       age_height_name, age_orig_name, age_grw_name, age_misc_name,
                                       age_crew_name, age_date_name)

# check plot IDs
clean_inputs.check_plot_ids(fc_center, 'PLOT', fc_prism, 'PLOT')
clean_inputs.check_plot_ids(fc_center, 'PLOT', fc_fixed, 'PLOT')
clean_inputs.check_plot_ids(fc_center, 'PLOT', fc_age, 'PLOT')

# check fixed offsets
clean_inputs.check_fixed_center(fc_center, 'PLOT', fc_fixed, 'PLOT', in_gdb)

# verify age plots
clean_inputs.check_contractor_age_plots(fc_center, 'PLOT', 'TYPE', fc_age, 'PLOT')

# check prism/fixed match
clean_inputs.check_prism_fixed(fc_prism, 'PLOT', fc_fixed, 'PLOT', in_gdb)

# import hierarchies
hierarchy_result = clean_inputs.import_hierarchy(fc_polygons, fc_center, fc_prism, fc_fixed,
                                                 fc_age, pool, comp, unit, site, stand)

# remove duplicates
deduplication_result = clean_inputs.remove_duplicates(fc_prism, fc_fixed, fc_age, fc_center)
out_center = deduplication_result[3]
arcpy.SetParameterAsText(39, out_center)
out_prism = deduplication_result[0]
arcpy.SetParameterAsText(40, out_prism)
out_fixed = deduplication_result[1]
arcpy.SetParameterAsText(41, out_fixed)
out_age = deduplication_result[2]
arcpy.SetParameterAsText(42, out_age)