# Do some imports
import os
import sys
import arcpy
import arcgis
import math
import pandas as pd
import numpy as np
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import forest_calcs as fcalc
import forest_summaries as fsum

# Define Required Input Parameters
prism_fc = arcpy.GetParameterAsText(0)
fixed_fc = arcpy.GetParameterAsText(1)
age_fc = arcpy.GetParameterAsText(2)
out_gdb = arcpy.GetParameterAsText(3)

# Define Optional Input Parameters - Summary Type
sum_sp = arcpy.GetParameterAsText(4)
sum_sp_by_mast = arcpy.GetParameterAsText(6)
sum_sp_by_size = arcpy.GetParameterAsText(7)
sum_hlth = arcpy.GetParameterAsText(8)
sum_hlth_by_sp = arcpy.GetParameterAsText(9)
sum_hlth_by_mast = arcpy.GetParameterAsText(10)
sum_hlth_by_size = arcpy.GetParameterAsText(11)
exp_enhanced_fixed = arcpy.GetParameterAsText(12)
exp_enhanced_prism = arcpy.GetParameterAsText(13)

# Define Optional Inupt Parameters - Summary Level
pid_sum = arcpy.GetParameterAsText(14)
sid_sum = arcpy.GetParameterAsText(15)
site_sum = arcpy.GetParameterAsText(16)
unit_sum = arcpy.GetParameterAsText(17)
comp_sum = arcpy.GetParameterAsText(18)
pool_sum = arcpy.GetParameterAsText(19)

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

# Generate Summaries
for level in levels:
    if level == 'PID':
        if sum_sp.lower() == 'true':
            fcalc.tpa_ba_qmdbh_plot_by_case_long(tree_table, None, 'TR_SP')
            table_name = "PID_Advanced_Species_Summary"
            table_path = os.path.join(out_gdb, table_name)
            out_df.spatial.to_table(location=table_path, sanitize_columns=False)
