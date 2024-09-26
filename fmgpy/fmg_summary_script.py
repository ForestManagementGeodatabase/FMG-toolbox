# Do some imports
import arcpy
import pandas as pd
from fmgpy.fmglib import forest_calcs as fcalc, forest_summaries as fsum
import importlib

importlib.reload(fcalc)
importlib.reload(fsum)

# Define Required Input Parameters
prism_fc = arcpy.GetParameterAsText(0)
fixed_fc = arcpy.GetParameterAsText(1)
age_fc = arcpy.GetParameterAsText(2)
out_gdb = arcpy.GetParameterAsText(3)

# Define Optional Inupt Parameters
pid_sum = arcpy.GetParameterAsText(4)
sid_sum = arcpy.GetParameterAsText(5)
site_sum = arcpy.GetParameterAsText(6)
unit_sum = arcpy.GetParameterAsText(7)
comp_sum = arcpy.GetParameterAsText(8)
pool_sum = arcpy.GetParameterAsText(9)

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

# Define output lists
gen_sum = []
age_sum = []
health_sum = []
mast_sum = []
size_sum = []
species_sum = []
vert_sum = []
manage_sum = []

# Execute FMG Summaries
for level in levels:
    out_gen_sum = fsum.general_summary(plot_table, tree_table, out_gdb, level)
    gen_sum.append(out_gen_sum)

    out_age_sum = fsum.age_summary(plot_table, out_gdb, level)
    age_sum.append(out_age_sum)

    out_health_sum = fsum.health_summary(plot_table, tree_table, out_gdb, level)
    health_sum.append(out_health_sum)

    out_mast_sum = fsum.mast_summary(plot_table, tree_table, out_gdb, level)
    mast_sum.append(out_mast_sum)

    out_size_sum = fsum.size_summary(plot_table, tree_table, out_gdb, level)
    size_sum.append(out_size_sum)

    out_species_sum = fsum.species_summary(plot_table, tree_table, fixed_df, out_gdb, level)
    species_sum.append(out_species_sum)

    out_vert_sum = fsum.vert_comp_summary(plot_table, tree_table, out_gdb, level)
    vert_sum.append(out_vert_sum)

    out_manage_sum = fsum.management_summary(plot_table, tree_table, out_gdb, level)
    manage_sum.append(out_manage_sum)

# Set ouput parameters for ESRI-land
arcpy.SetParameter(10, gen_sum)
arcpy.SetParameter(11, age_sum)
arcpy.SetParameter(12, health_sum)
arcpy.SetParameter(13, mast_sum)
arcpy.SetParameter(14, size_sum)
arcpy.SetParameter(15, species_sum)
arcpy.SetParameter(16, vert_sum)
arcpy.SetParameter(17, manage_sum)

arcpy.AddMessage('FMG Summaries Complete - check output GDB for results')
