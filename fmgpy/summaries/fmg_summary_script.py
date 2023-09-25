# Do some imports
import os
import sys
import arcpy
import arcgis
import math
import pandas as pd
import numpy as np
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import fmgpy.summaries.forest_calcs as fcalc
import fmgpy.summaries.forest_summaries as fsum

# Define Required Input Parameters
prism_fc = r"C:\LocalProjects\FMG\FMG-toolbox\test\data\FMG_OracleSchema.gdb\PRISM_PLOTS" #arcpy.GetParameterAsText(0)
fixed_fc = r"C:\LocalProjects\FMG\FMG-toolbox\test\data\FMG_OracleSchema.gdb\FIXED_PLOTS" #arcpy.GetParameterAsText(1)
age_fc = r"C:\LocalProjects\FMG\FMG-toolbox\test\data\FMG_OracleSchema.gdb\AGE_PLOTS" #arcpy.GetParameterAsText(2)
out_gdb = r"C:\LocalProjects\FMG\FMG_CODE_TESTING.gdb" #arcpy.GetParameterAsText(3)

# Define Optional Inupt Parameters
pid_sum = 'True' #arcpy.GetParameterAsText(4)
sid_sum = 'True' #arcpy.GetParameterAsText(5)
site_sum = 'True' #arcpy.GetParameterAsText(6)
unit_sum = 'True' #arcpy.GetParameterAsText(7)
comp_sum = 'True' #arcpy.GetParameterAsText(8)
pool_sum = 'True' #arcpy.GetParameterAsText(9)

# Evaluate Optional Input Parameters to build level list
levels = []
if pid_sum.lower() == 'true':
    levels.append('PID')
if sid_sum.lower() == 'true':
    levels.append('SID')
if site_sum.lower() == 'true':
    levels.append('SITE')
if unit_sum.lower() == 'true':
    levels.append('UNIT')
if comp_sum.lower() == 'true':
    levels.append('COMP')
if pool_sum.lower() == 'true':
    levels.append('POOL')
arcpy.AddMessage('Begin FMG Summaries on ' + str(levels))

# Import ESRI feature classes as pandas dataframes
fixed_df = pd.DataFrame.spatial.from_featureclass(fixed_fc)
age_df = pd.DataFrame.spatial.from_featureclass(age_fc)
prism_df = pd.DataFrame.spatial.from_featureclass(prism_fc)

# Check dfs for FMG level fields
arcpy.AddMessage('Running checks on input data')
for required_level in levels:
    if required_level not in fixed_df.columns:
        raise Exception('{0} column not present in fixed plots, correct to run FMG Summaries'.format(required_level))
    if required_level not in age_df.columns:
        raise Exception('{0} column not present in age plots, correct to run FMG Summaries'.format(required_level))
    if required_level not in prism_df.columns:
        raise Exception('{0} column not present in prism plots, correct to run FMG Summaries'.format(required_level))
arcpy.AddMessage('Checks passed, continuing with summaries')

# Create base datasets
plot_table = fcalc.create_plot_table(fixed_df=fixed_df, age_df=age_df)
tree_table = fcalc.create_tree_table(prism_df=prism_df)

# Execute FMG Summaries
for level in levels:
    out_gen_sum = fsum.general_summary(plot_table, tree_table, out_gdb, level)
    #arcpy.SetParameterAsText(10, out_gen_sum)

    out_age_sum = fsum.age_summary(plot_table, out_gdb, level)
    #arcpy.SetParameterAsText(11, out_age_sum)

    out_health_sum = fsum.health_summary(plot_table, tree_table, out_gdb, level)
    #arcpy.SetParameterAsText(12, out_health_sum)

    out_mast_sum = fsum.mast_summary(plot_table, tree_table, out_gdb, level)
    #arcpy.SetParameterAsText(13, out_mast_sum)

    out_size_sum = fsum.size_summary(plot_table, tree_table, out_gdb, level)
    #arcpy.SetParameterAsText(14, out_size_sum)

    out_species_sum = fsum.species_summary(plot_table, tree_table, fixed_df, out_gdb, level)
    #arcpy.SetParameterAsText(15, out_species_sum)

    out_vert_sum = fsum.vert_comp_summary(plot_table, tree_table, out_gdb, level)
    #arcpy.SetParameterAsText(16, out_vert_sum)

    out_manage_sum = fsum.management_summary(plot_table, tree_table, out_gdb, level)
    #arcpy.SetParameterAsText(17, out_manage_sum)