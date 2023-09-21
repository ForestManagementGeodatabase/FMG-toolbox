import os
import sys
import arcpy
import arcgis
import math
import pandas as pd
import numpy as np
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import fmgpy.summaries.forest_calcs as fcalc

# Define inputs
prism_fc = r"C:\LocalProjects\FMG\FMG-toolbox\test\data\FMG_OracleSchema.gdb\PRISM_PLOTS"
fixed_fc = r"C:\LocalProjects\FMG\FMG-toolbox\test\data\FMG_OracleSchema.gdb\FIXED_PLOTS"
age_fc = r"C:\LocalProjects\FMG\FMG-toolbox\test\data\FMG_OracleSchema.gdb\AGE_PLOTS"
out_gdb = r"C:\LocalProjects\FMG\FMG_CODE_TESTING.gdb"

# Import ESRI feature classes as pandas dataframes
fixed_df = pd.DataFrame.spatial.from_featureclass(fixed_fc)
age_df = pd.DataFrame.spatial.from_featureclass(age_fc)
prism_df = pd.DataFrame.spatial.from_featureclass(prism_fc)

# Create base datasets
plot_table = fcalc.create_plot_table(fixed_df=fixed_df, age_df=age_df)
tree_table = fcalc.create_tree_table(prism_df=prism_df)

# Allow output overwrite during testing
arcpy.env.overwriteOutput = True

# Define list of levels
levels = ['PID', 'SID', 'SITE', 'UNIT', 'COMP', 'POOL']

for level in levels:
    if level != 'PID':
        arcpy.AddMessage('Work on {0}'.format(level))

        # Create base table
        base_df = fcalc.create_level_df(level, plot_table)
        arcpy.AddMessage("    Base DF Created")

        # Run TPA Case with live tree filter to get CNP_TPA, CNP_BA, CNP_QMDBH, MID_TPA, MID_BA, MID_QMDBH
        vc_live_tpa = fcalc.tpa_ba_qmdbh_level_by_case(tree_table=tree_table,
                                                       filter_statement=~tree_table.TR_HLTH.isin(["D", "DEAD"]),
                                                       case_column='VERT_COMP',
                                                       level=level)
        vc_live_tpa = vc_live_tpa \
            .rename(columns={'BA_VERT_COMP_Canopy': 'CNP_BA',
                             'QM_DBH_VERT_COMP_Canopy': 'CNP_QMDBH',
                             'TPA_VERT_COMP_Canopy': 'CNP_TPA',
                             'BA_VERT_COMP_Midstory': 'MID_BA',
                             'QM_DBH_VERT_COMP_Midstory': 'MID_QMDBH',
                             'TPA_VERT_COMP_Midstory': 'MID_TPA'}) \
            .set_index(level)
        arcpy.AddMessage("    Live TPA, BA, QM DBH for vert comp created")

        # Run TPA Case with dead tree filter to get CNP_D_TPA, CNP_D_BA, CNP_D_QMDBH, MID_D_TPA, MID_D_BA, MID_D_QMDBH
        vc_dead_tpa = fcalc.tpa_ba_qmdbh_level_by_case(tree_table=tree_table,
                                                       filter_statement=tree_table.TR_HLTH.isin(["D", "DEAD"]),
                                                       case_column='VERT_COMP',
                                                       level=level)
        vc_dead_tpa = vc_dead_tpa \
            .rename(columns={'BA_VERT_COMP_Canopy': 'CNP_D_BA',
                             'QM_DBH_VERT_COMP_Canopy': 'CNP_D_QMDBH',
                             'TPA_VERT_COMP_Canopy': 'CNP_D_TPA',
                             'BA_VERT_COMP_Midstory': 'MID_D_BA',
                             'QM_DBH_VERT_COMP_Midstory': 'MID_D_QMDBH',
                             'TPA_VERT_COMP_Midstory': 'MID_D_TPA'}) \
            .set_index(level)
        arcpy.AddMessage("    Dead TPA, BA, QM DBH for vert comp created")

        # Run SP Prev Pct with Canopy (VERT_COMP) filter to get CNP_DOM_SP, CNP_DOM_SP_PCMP
        # Create Typical Species dominant species
        cnp_dom_sp_df = fcalc.species_dom_level(tree_table=tree_table,
                                                filter_statement=tree_table['VERT_COMP'] == 'Canopy',
                                                level=level)
        cnp_dom_sp_df = cnp_dom_sp_df\
            .rename(columns={'SP_DOM': 'CNP_DOM_SP', 'SP_DOM_PCMP': 'CNP_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Canopy Dom species created")

        # Run SP Prev Pct with Midstory (VERT_COMP) filter to get MID_DOM_SP, MID_DOM_SP_PCMP
        mid_dom_sp_df = fcalc.species_dom_level(tree_table=tree_table,
                                                filter_statement=tree_table['VERT_COMP'] == 'Midstory',
                                                level=level)
        mid_dom_sp_df = mid_dom_sp_df\
            .rename(columns={'SP_DOM': 'MID_DOM_SP', 'SP_DOM_PCMP': 'MID_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Midstory Dom species created")

        # Run SP Prev Pct with Intermediate (TR_CL==I) filter to get INT_DOM_SP, INT_DOM_SP_PCMP
        int_dom_sp_df = fcalc.species_dom_level(tree_table=tree_table,
                                                filter_statement=tree_table['TR_CL'] == 'I',
                                                level=level)
        int_dom_sp_df = int_dom_sp_df\
            .rename(columns={'SP_DOM': 'INT_DOM_SP', 'SP_DOM_PCMP': 'INT_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Intermediate Dom species created")

        # Run HLTH Prev Pct with Canopy (VERT_COMP) filter to get CNP_DOM_HLTH, CNP_DOM_HLTH_PCMP
        cnp_dom_hlth_df = fcalc.health_dom_level(tree_table=tree_table,
                                                 filter_statement=tree_table['VERT_COMP'] == 'Canopy',
                                                 level=level)
        cnp_dom_hlth_df = cnp_dom_hlth_df\
            .rename(columns={'HLTH_DOM': 'CNP_DOM_HLTH', 'HLTH_DOM_PCMP': 'CNP_DOM_HLTH_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Canopy Dom health created")

        # Run HLTH Prev Pct with Midstory (VERT_COMP) filter to get MID_DOM_HLTH, MID_DOM_HLTH_PCMP
        mid_dom_hlth_df = fcalc.health_dom_level(tree_table=tree_table,
                                                 filter_statement=tree_table['VERT_COMP'] == 'Midstory',
                                                 level=level)
        mid_dom_hlth_df = mid_dom_hlth_df\
            .rename(columns={'HLTH_DOM': 'MID_DOM_HLTH', 'HLTH_DOM_PCMP': 'MID_DOM_HLTH_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Midstory Dom health created")

        # Run HLTH Prev Pct with Intermediate (TR_CL==I) filter to get INT_DOM_HLTH, INT_DOM_HLTH_PCMP
        int_dom_hlth_df = fcalc.health_dom_level(tree_table=tree_table,
                                                 filter_statement=tree_table['TR_CL'] == 'I',
                                                 level=level)
        int_dom_hlth_df = int_dom_hlth_df\
            .rename(columns={'HLTH_DOM': 'INT_DOM_HLTH', 'HLTH_DOM_PCMP': 'INT_DOM_HLTH_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Intermediate Dom health created")

        # Merge component dataframes onto the base dataframe
        out_df = base_df \
            .join(other=[vc_live_tpa,
                         vc_dead_tpa,
                         cnp_dom_sp_df,
                         mid_dom_sp_df,
                         int_dom_sp_df,
                         cnp_dom_hlth_df,
                         mid_dom_hlth_df,
                         int_dom_hlth_df],
                  how='left')\
            .reset_index()
        arcpy.AddMessage("    All Component DFs Merged")

        # Reindex output dataframe
        general_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                             col_csv='resources/vertcomp_summary_cols.csv')
        out_df = out_df.reindex(labels=general_reindex_cols,
                                axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Handle NaN values appropriately
        nan_fill_dict_level = fcalc.fmg_nan_fill(col_csv='resources/vertcomp_summary_cols.csv')
        out_df = out_df.fillna(value=nan_fill_dict_level)
        arcpy.AddMessage("    Nan Values Filled")

        # Enforce ESRI compatible Dtypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/vertcomp_summary_cols.csv')
        out_df = out_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Export to gdb table
        table_name = level + "_Vert_Comp_Summary"
        table_path = os.path.join(out_gdb, table_name)
        out_df.spatial.to_table(location=table_path, sanitize_columns=False)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    if level == 'PID':
        arcpy.AddMessage('Work on {0}'.format(level))

        # Create base table
        base_df = fcalc.create_level_df(level, plot_table)
        arcpy.AddMessage("    Base DF Created")

        # Run TPA Case with live tree filter to get CNP_TPA, CNP_BA, CNP_QMDBH, MID_TPA, MID_BA, MID_QMDBH
        vc_live_tpa = fcalc.tpa_ba_qmdbh_plot_by_case(tree_table=tree_table,
                                                      filter_statement=~tree_table.TR_HLTH.isin(["D", "DEAD"]),
                                                      case_column='VERT_COMP')

        vc_live_tpa = vc_live_tpa \
            .rename(columns={'BA_VERT_COMP_Canopy': 'CNP_BA',
                             'QM_DBH_VERT_COMP_Canopy': 'CNP_QMDBH',
                             'TPA_VERT_COMP_Canopy': 'CNP_TPA',
                             'BA_VERT_COMP_Midstory': 'MID_BA',
                             'QM_DBH_VERT_COMP_Midstory': 'MID_QMDBH',
                             'TPA_VERT_COMP_Midstory': 'MID_TPA'}) \
            .set_index(level)
        arcpy.AddMessage("    Live TPA, BA, QM DBH for vert comp created")

        # Run TPA Case with dead tree filter to get CNP_D_TPA, CNP_D_BA, CNP_D_QMDBH, MID_D_TPA, MID_D_BA, MID_D_QMDBH
        vc_dead_tpa = fcalc.tpa_ba_qmdbh_plot_by_case(tree_table=tree_table,
                                                      filter_statement=tree_table.TR_HLTH.isin(["D", "DEAD"]),
                                                      case_column='VERT_COMP')

        vc_dead_tpa = vc_dead_tpa \
            .rename(columns={'BA_VERT_COMP_Canopy': 'CNP_D_BA',
                             'QM_DBH_VERT_COMP_Canopy': 'CNP_D_QMDBH',
                             'TPA_VERT_COMP_Canopy': 'CNP_D_TPA',
                             'BA_VERT_COMP_Midstory': 'MID_D_BA',
                             'QM_DBH_VERT_COMP_Midstory': 'MID_D_QMDBH',
                             'TPA_VERT_COMP_Midstory': 'MID_D_TPA'}) \
            .set_index(level)
        arcpy.AddMessage("    Dead TPA, BA, QM DBH for vert comp created")

        # Run SP Prev Pct with Canopy (VERT_COMP) filter to get CNP_DOM_SP, CNP_DOM_SP_PCMP
        # Create Typical Species dominant species
        cnp_dom_sp_df = fcalc.species_dom_plot(tree_table=tree_table,
                                               filter_statement=tree_table['VERT_COMP'] == 'Canopy')

        cnp_dom_sp_df = cnp_dom_sp_df \
            .rename(columns={'SP_DOM': 'CNP_DOM_SP', 'SP_DOM_PCMP': 'CNP_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Canopy Dom species created")

        # Run SP Prev Pct with Midstory (VERT_COMP) filter to get MID_DOM_SP, MID_DOM_SP_PCMP
        mid_dom_sp_df = fcalc.species_dom_plot(tree_table=tree_table,
                                               filter_statement=tree_table['VERT_COMP'] == 'Midstory')

        mid_dom_sp_df = mid_dom_sp_df \
            .rename(columns={'SP_DOM': 'MID_DOM_SP', 'SP_DOM_PCMP': 'MID_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Midstory Dom species created")

        # Run SP Prev Pct with Intermediate (TR_CL==I) filter to get INT_DOM_SP, INT_DOM_SP_PCMP
        int_dom_sp_df = fcalc.species_dom_plot(tree_table=tree_table,
                                               filter_statement=tree_table['TR_CL'] == 'I')

        int_dom_sp_df = int_dom_sp_df \
            .rename(columns={'SP_DOM': 'INT_DOM_SP', 'SP_DOM_PCMP': 'INT_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Intermediate Dom species created")

        # Run HLTH Prev Pct with Canopy (VERT_COMP) filter to get CNP_DOM_HLTH, CNP_DOM_HLTH_PCMP
        cnp_dom_hlth_df = fcalc.health_dom_plot(tree_table=tree_table,
                                                filter_statement=tree_table['VERT_COMP'] == 'Canopy')

        cnp_dom_hlth_df = cnp_dom_hlth_df \
            .rename(columns={'HLTH_DOM': 'CNP_DOM_HLTH', 'HLTH_DOM_PCMP': 'CNP_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Canopy Dom health created")

        # Run HLTH Prev Pct with Midstory (VERT_COMP) filter to get MID_DOM_HLTH, MID_DOM_HLTH_PCMP
        mid_dom_hlth_df = fcalc.health_dom_plot(tree_table=tree_table,
                                                filter_statement=tree_table['VERT_COMP'] == 'Midstory')

        mid_dom_hlth_df = mid_dom_hlth_df \
            .rename(columns={'HLTH_DOM': 'MID_DOM_HLTH', 'HLTH_DOM_PCMP': 'MID_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Midstory Dom health created")

        # Run HLTH Prev Pct with Intermediate (TR_CL==I) filter to get INT_DOM_HLTH, INT_DOM_HLTH_PCMP
        int_dom_hlth_df = fcalc.health_dom_plot(tree_table=tree_table,
                                                filter_statement=tree_table['TR_CL'] == 'I')

        int_dom_hlth_df = int_dom_hlth_df \
            .rename(columns={'HLTH_DOM': 'INT_DOM_HLTH', 'HLTH_DOM_PCMP': 'INT_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Intermediate Dom health created")

        # Merge component dataframes onto the base dataframe
        out_df = base_df \
            .join(other=[vc_live_tpa,
                         vc_dead_tpa,
                         cnp_dom_sp_df,
                         mid_dom_sp_df,
                         int_dom_sp_df,
                         cnp_dom_hlth_df,
                         mid_dom_hlth_df,
                         int_dom_hlth_df],
                  how='left') \
            .reset_index()
        arcpy.AddMessage("    All Component DFs Merged")

        # Reindex output dataframe
        general_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                             col_csv='resources/vertcomp_summary_cols.csv')
        out_df = out_df.reindex(labels=general_reindex_cols,
                                axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Handle NaN values appropriately
        nan_fill_dict_level = fcalc.fmg_nan_fill(col_csv='resources/vertcomp_summary_cols.csv')
        out_df = out_df.fillna(value=nan_fill_dict_level)
        arcpy.AddMessage("    Nan Values Filled")

        # Enforce ESRI compatible Dtypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/vertcomp_summary_cols.csv')
        out_df = out_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Export to gdb table
        table_name = "PID_Vert_Comp_Summary"
        table_path = os.path.join(out_gdb, table_name)
        out_df.spatial.to_table(location=table_path, sanitize_columns=False)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))


