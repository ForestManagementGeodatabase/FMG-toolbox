# Do some imports
import os
import arcpy
import pandas as pd
from fmglib import forest_calcs as fcalc

# Define Required Input Parameters
prism_fc = arcpy.GetParameterAsText(0)
fixed_fc = arcpy.GetParameterAsText(1)
age_fc = arcpy.GetParameterAsText(2)
out_gdb = arcpy.GetParameterAsText(3)

# Define Optional Input Parameters - Summary Type
sum_sp = arcpy.GetParameterAsText(4)
sum_sp_by_mast = arcpy.GetParameterAsText(5)
sum_sp_by_size = arcpy.GetParameterAsText(6)
sum_sp_by_vertcomp = arcpy.GetParameterAsText(7)
sum_hlth = arcpy.GetParameterAsText(8)
sum_hlth_by_sp = arcpy.GetParameterAsText(9)
sum_hlth_by_mast = arcpy.GetParameterAsText(10)
sum_hlth_by_size = arcpy.GetParameterAsText(11)
sum_hlth_by_vertcomp = arcpy.GetParameterAsText(12)
exp_enhanced_fixed = arcpy.GetParameterAsText(13)
exp_enhanced_prism = arcpy.GetParameterAsText(14)

# Define Optional Inupt Parameters - Summary Level
pid_sum = arcpy.GetParameterAsText(15)
sid_sum = arcpy.GetParameterAsText(16)
site_sum = arcpy.GetParameterAsText(17)
unit_sum = arcpy.GetParameterAsText(18)
comp_sum = arcpy.GetParameterAsText(19)
pool_sum = arcpy.GetParameterAsText(20)

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
sum_sp_out_list = []

sum_hlth_out_list = []


# Generate Summaries
for level in levels:
    if level == 'PID':
        arcpy.AddMessage('Work on level {0}'.format(level))

        if sum_sp.lower() == 'true':
            arcpy.AddMessage('    Create Advanced Species Summary')
            sum_sp_df = fcalc.tpa_ba_qmdbh_plot_by_multi_case_long(tree_table, None, ['TR_SP'])
            sum_sp_name = "PID_ZAdv_Species_Summary"
            sum_sp_path = os.path.join(out_gdb, sum_sp_name)
            sum_sp_df.spatial.to_table(location=sum_sp_path, sanitize_columns=False)
            sum_sp_out_list.append(sum_sp_path)

        if sum_sp_by_mast.lower() == 'true':
            arcpy.AddMessage('    Create Advanced Species by Mast Types Summary')
            sum_sp_by_mast_df = fcalc.tpa_ba_qmdbh_plot_by_multi_case_long(tree_table, None, ['TR_SP', 'MAST_TYPE'])
            sum_sp_by_mast_name = "PID_ZAdv_SpeciesByMastType_Summary"
            sum_sp_by_mast_path = os.path.join(out_gdb, sum_sp_by_mast_name)
            sum_sp_by_mast_df.spatial.to_table(location=sum_sp_by_mast_path, sanitize_columns=False)
            sum_sp_out_list.append(sum_sp_by_mast_path)

        if sum_sp_by_size.lower() == 'true':
            arcpy.AddMessage('    Create Advanced Species By Size Summary')
            sum_sp_by_size_df = fcalc.tpa_ba_qmdbh_plot_by_multi_case_long(tree_table, None, ['TR_SP', 'TR_SIZE'])
            sum_sp_by_size_name = "PID_ZAdv_SpeciesBySize_Summary"
            sum_sp_by_size_path = os.path.join(out_gdb, sum_sp_by_size_name)
            sum_sp_by_size_df.spatial.to_table(location=sum_sp_by_size_path, sanitize_columns=False)
            sum_sp_out_list.append(sum_sp_by_size_path)

        if sum_sp_by_vertcomp.lower() == 'true':
            arcpy.AddMessage('    Create Advanced Species By Vertical Composition Summary')
            sum_sp_by_vertcomp_df = fcalc.tpa_ba_qmdbh_plot_by_multi_case_long(tree_table, None, ['TR_SP', 'VERT_COMP'])
            sum_sp_by_vertcomp_name = "PID_ZAdv_SpeciesByVertComp_Summary"
            sum_sp_by_vertcomp_path = os.path.join(out_gdb, sum_sp_by_vertcomp_name)
            sum_sp_by_vertcomp_df.spatial.to_table(location=sum_sp_by_vertcomp_path, sanitize_columns=False)
            sum_sp_out_list.append(sum_sp_by_vertcomp_path)

        if sum_hlth.lower() == 'true':
            arcpy.AddMessage('    Create Advanced Health Summary')
            sum_hlth_df = fcalc.tpa_ba_qmdbh_plot_by_multi_case_long(tree_table, None, ['TR_HLTH'])
            sum_hlth_df_name = "PID_ZAdv_Health_Summary"
            sum_hlth_df_path = os.path.join(out_gdb, sum_hlth_df_name)
            sum_hlth_df.spatial.to_table(location=sum_hlth_df_path, sanitize_columns=False)
            sum_hlth_out_list.append(sum_hlth_df_path)

        if sum_hlth_by_sp.lower() == 'true':
            arcpy.AddMessage('    Create Advanced Health by Species Summary')
            sum_hlth_by_sp_df = fcalc.tpa_ba_qmdbh_plot_by_multi_case_long(tree_table, None, ['TR_HLTH', 'TR_SP'])
            sum_hlth_by_sp_df_name = "PID_ZAdv_HealthBySpecies_Summary"
            sum_hlth_by_sp_df_path = os.path.join(out_gdb, sum_hlth_by_sp_df_name)
            sum_hlth_by_sp_df.spatial.to_table(location=sum_hlth_by_sp_df_path, sanitize_columns=False)
            sum_hlth_out_list.append(sum_hlth_by_sp_df_path)

        if sum_hlth_by_mast.lower() == 'true':
            arcpy.AddMessage('    Create Advanced Health by Mast Types Summary')
            sum_hlth_by_mast_df = fcalc.tpa_ba_qmdbh_plot_by_multi_case_long(tree_table, None, ['TR_HLTH', 'MAST_TYPE'])
            sum_hlth_by_mast_df_name = "PID_ZAdv_HealthByMastType_Summary"
            sum_hlth_by_mast_df_path = os.path.join(out_gdb, sum_hlth_by_mast_df_name)
            sum_hlth_by_mast_df.spatial.to_table(location=sum_hlth_by_mast_df_path, sanitize_columns=False)
            sum_hlth_out_list.append(sum_hlth_by_mast_df_path)

        if sum_hlth_by_size.lower() == 'true':
            arcpy.AddMessage('    Create Advanced Health by Size Summary')
            sum_hlth_by_size_df = fcalc.tpa_ba_qmdbh_plot_by_multi_case_long(tree_table, None, ['TR_HLTH', 'TR_SIZE'])
            sum_hlth_by_size_df_name = "PID_ZAdv_HealthBySize_Summary"
            sum_hlth_by_size_df_path = os.path.join(out_gdb, sum_hlth_by_size_df_name)
            sum_hlth_by_size_df.spatial.to_table(location=sum_hlth_by_size_df_path, sanitize_columns=False)
            sum_hlth_out_list.append(sum_hlth_by_size_df_path)

        if sum_hlth_by_vertcomp.lower() == 'true':
            arcpy.AddMessage('    Create Advanced Health by Vertical Composition Summary')
            sum_hlth_by_vertcomp_df = fcalc.tpa_ba_qmdbh_plot_by_multi_case_long(tree_table, None, ['TR_HLTH', 'VERT_COMP'])
            sum_hlth_by_vertcomp_df_name = "PID_ZAdv_HealthByVertComp_Summary"
            sum_hlth_by_vertcomp_df_path = os.path.join(out_gdb, sum_hlth_by_vertcomp_df_name)
            sum_hlth_by_vertcomp_df.spatial.to_table(location=sum_hlth_by_vertcomp_df_path, sanitize_columns=False)
            sum_hlth_out_list.append(sum_hlth_by_vertcomp_df_path)

    elif level != 'PID':
        arcpy.AddMessage('Work on level {0}'.format(level))

        if sum_sp.lower() == 'true':
            arcpy.AddMessage('    Create Advanced Species Summary')
            sum_sp_df = fcalc.tpa_ba_qmdbh_level_by_multi_case_long(tree_table, None, ['TR_SP'], level)
            sum_sp_name = level + "_ZAdv_Species_Summary"
            sum_sp_path = os.path.join(out_gdb, sum_sp_name)
            sum_sp_df.spatial.to_table(location=sum_sp_path, sanitize_columns=False)
            sum_sp_out_list.append(sum_sp_path)

        if sum_sp_by_mast.lower() == 'true':
            arcpy.AddMessage('    Create Advanced Species by Mast Types Summary')
            sum_sp_by_mast_df = fcalc.tpa_ba_qmdbh_level_by_multi_case_long(tree_table, None, ['TR_SP', 'MAST_TYPE'], level)
            sum_sp_by_mast_name = level + "_ZAdv_SpeciesByMastType_Summary"
            sum_sp_by_mast_path = os.path.join(out_gdb, sum_sp_by_mast_name)
            sum_sp_by_mast_df.spatial.to_table(location=sum_sp_by_mast_path, sanitize_columns=False)
            sum_sp_out_list.append(sum_sp_by_mast_path)

        if sum_sp_by_size.lower() == 'true':
            arcpy.AddMessage('    Create Advanced Species By Size Summary')
            sum_sp_by_size_df = fcalc.tpa_ba_qmdbh_level_by_multi_case_long(tree_table, None, ['TR_SP', 'TR_SIZE'], level)
            sum_sp_by_size_name = level + "_ZAdv_SpeciesBySize_Summary"
            sum_sp_by_size_path = os.path.join(out_gdb, sum_sp_by_size_name)
            sum_sp_by_size_df.spatial.to_table(location=sum_sp_by_size_path, sanitize_columns=False)
            sum_sp_out_list.append(sum_sp_by_size_path)

        if sum_sp_by_vertcomp.lower() == 'true':
            arcpy.AddMessage('    Create Advanced Species By Vertical Composition Summary')
            sum_sp_by_vertcomp_df = fcalc.tpa_ba_qmdbh_level_by_multi_case_long(tree_table, None, ['TR_SP', 'VERT_COMP'], level)
            sum_sp_by_vertcomp_name = level + "_ZAdv_SpeciesByVertComp_Summary"
            sum_sp_by_vertcomp_path = os.path.join(out_gdb, sum_sp_by_vertcomp_name)
            sum_sp_by_vertcomp_df.spatial.to_table(location=sum_sp_by_vertcomp_path, sanitize_columns=False)
            sum_sp_out_list.append(sum_sp_by_vertcomp_path)

        if sum_hlth.lower() == 'true':
            arcpy.AddMessage('    Create Advanced Health Summary')
            sum_hlth_df = fcalc.tpa_ba_qmdbh_level_by_multi_case_long(tree_table, None, ['TR_HLTH'], level)
            sum_hlth_df_name = level + "_ZAdv_Health_Summary"
            sum_hlth_df_path = os.path.join(out_gdb, sum_hlth_df_name)
            sum_hlth_df.spatial.to_table(location=sum_hlth_df_path, sanitize_columns=False)
            sum_hlth_out_list.append(sum_hlth_df_path)

        if sum_hlth_by_sp.lower() == 'true':
            arcpy.AddMessage('    Create Advanced Health by Species Summary')
            sum_hlth_by_sp_df = fcalc.tpa_ba_qmdbh_level_by_multi_case_long(tree_table, None, ['TR_HLTH', 'TR_SP'], level)
            sum_hlth_by_sp_df_name = level + "_ZAdv_HealthBySpecies_Summary"
            sum_hlth_by_sp_df_path = os.path.join(out_gdb, sum_hlth_by_sp_df_name)
            sum_hlth_by_sp_df.spatial.to_table(location=sum_hlth_by_sp_df_path, sanitize_columns=False)
            sum_hlth_out_list.append(sum_hlth_by_sp_df_path)

        if sum_hlth_by_mast.lower() == 'true':
            arcpy.AddMessage('    Create Advanced Health by Mast Types Summary')
            sum_hlth_by_mast_df = fcalc.tpa_ba_qmdbh_level_by_multi_case_long(tree_table, None, ['TR_HLTH', 'MAST_TYPE'], level)
            sum_hlth_by_mast_df_name = level + "_ZAdv_HealthByMastType_Summary"
            sum_hlth_by_mast_df_path = os.path.join(out_gdb, sum_hlth_by_mast_df_name)
            sum_hlth_by_mast_df.spatial.to_table(location=sum_hlth_by_mast_df_path, sanitize_columns=False)
            sum_hlth_out_list.append(sum_hlth_by_mast_df_path)

        if sum_hlth_by_size.lower() == 'true':
            arcpy.AddMessage('    Create Advanced Health by Size Summary')
            sum_hlth_by_size_df = fcalc.tpa_ba_qmdbh_level_by_multi_case_long(tree_table, None, ['TR_HLTH', 'TR_SIZE'], level)
            sum_hlth_by_size_df_name = level+ "_ZAdv_HealthBySize_Summary"
            sum_hlth_by_size_df_path = os.path.join(out_gdb, sum_hlth_by_size_df_name)
            sum_hlth_by_size_df.spatial.to_table(location=sum_hlth_by_size_df_path, sanitize_columns=False)
            sum_hlth_out_list.append(sum_hlth_by_size_df_path)

        if sum_hlth_by_vertcomp.lower() == 'true':
            arcpy.AddMessage('    Create Advanced Health by Vertical Composition Summary')
            sum_hlth_by_vertcomp_df = fcalc.tpa_ba_qmdbh_level_by_multi_case_long(tree_table, None, ['TR_HLTH', 'VERT_COMP'], level)
            sum_hlth_by_vertcomp_df_name = level + "_ZAdv_HealthByVertComp_Summary"
            sum_hlth_by_vertcomp_df_path = os.path.join(out_gdb, sum_hlth_by_vertcomp_df_name)
            sum_hlth_by_vertcomp_df.spatial.to_table(location=sum_hlth_by_vertcomp_df_path, sanitize_columns=False)
            sum_hlth_out_list.append(sum_hlth_by_vertcomp_df_path)

if exp_enhanced_fixed.lower() == 'true':
    arcpy.AddMessage('Exporting Enhanced Fixed Plots')
    plot_table_name = "Enhanced_Fixed_Plots"
    plot_table_path = os.path.join(out_gdb, plot_table_name)
    plot_table.spatial.to_featureclass(location=plot_table_path, sanitize_columns=False)
    arcpy.SetParameter(21, plot_table_path)

if exp_enhanced_prism.lower() == 'true':
    arcpy.AddMessage('Exporting Enhanced Prism Plots')
    tree_table_name = "Enhanced_Prism_Plots"
    tree_table_path = os.path.join(out_gdb, tree_table_name)
    tree_table.spatial.to_featureclass(location=tree_table_path, sanitize_columns=False)
    arcpy.SetParameter(22, tree_table_path)

arcpy.SetParameter(23, sum_sp_out_list)
arcpy.SetParameter(24, sum_hlth_out_list)


arcpy.AddMessage('FMG Advanced Summaries Complete - check output GDB for results')
