import os
import sys
import arcpy
import arcgis
import math
import pandas as pd
import numpy as np
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import fmgpy.summaries.forest_calcs as fcalc


def management_summary(plot_table, tree_table, out_gdb, level):
    arcpy.AddMessage('--Execute Management Summary--')
    if level != 'PID':
        arcpy.AddMessage('Work on {0}'.format(level))

        # Create base table
        base_df = fcalc.create_level_df(level, plot_table)
        arcpy.AddMessage("    Base DF Created")

        # Create Stocking Percent df
        stocking_df = fcalc.tpa_ba_qmdbh_level(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]), level)
        stocking_df['STOCK_PCT'] = fcalc.stocking_pct(stocking_df['TPA'], stocking_df['QM_DBH'])
        stocking_df = stocking_df[[level, 'STOCK_PCT']].set_index(level)

        # Create hard mast stocking percent df
        hm_stocking_df = fcalc.tpa_ba_qmdbh_level(tree_table=tree_table,
                                                  filter_statement=(tree_table['TR_HLTH'] != 'D') &
                                                                   (tree_table['MAST_TYPE'] == 'Hard'),
                                                  level=level)
        hm_stocking_df['STOCK_PCT_HM'] = fcalc.stocking_pct(hm_stocking_df['TPA'], hm_stocking_df['QM_DBH'])
        hm_stocking_df = hm_stocking_df[[level, 'STOCK_PCT_HM']].set_index(level)

        # Create species richness df
        species_richness_df = fcalc.create_sp_richness(tree_table=tree_table,
                                                       plot_table=plot_table,
                                                       level=level)\
                                   .set_index(level)

        # Merge component dfs
        manage_summary_df = base_df \
            .join(other=[stocking_df,
                         hm_stocking_df,
                         species_richness_df],
                  how='left') \
            .reset_index()

        # Reindex output dataframe
        manage_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                            col_csv='resources/management_summary_cols.csv')
        manage_summary_df = manage_summary_df.reindex(labels=manage_reindex_cols,
                                                      axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Enforce ESRI compatible DTypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/management_summary_cols.csv')
        manage_summary_df = manage_summary_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Handle NAN values for output
        nan_fill_dict = fcalc.fmg_nan_fill(col_csv='resources/management_summary_cols.csv')
        manage_summary_df = manage_summary_df.fillna(value=nan_fill_dict)
        arcpy.AddMessage("    No data/nan values set")

        # Export to GDB Table
        table_name = level + '_Management_Summary'
        table_path = os.path.join(out_gdb, table_name)
        manage_summary_df.spatial.to_table(table_path)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    if level == 'PID':
        arcpy.AddMessage('Work on {0}'.format(level))

        # Create base table
        base_df = fcalc.create_level_df(level, plot_table)
        arcpy.AddMessage("    Base DF Created")

        # Create Stocking Percent df
        stocking_df = fcalc.tpa_ba_qmdbh_plot(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]))
        stocking_df['STOCK_PCT'] = fcalc.stocking_pct(stocking_df['TPA'], stocking_df['QM_DBH'])
        stocking_df = stocking_df[[level, 'STOCK_PCT']].set_index(level)

        # Create hard mast stocking percent df
        hm_stocking_df = fcalc.tpa_ba_qmdbh_plot(tree_table=tree_table,
                                                 filter_statement=(tree_table['TR_HLTH'] != 'D') &
                                                                  (tree_table['MAST_TYPE'] == 'Hard'))
        hm_stocking_df['STOCK_PCT_HM'] = fcalc.stocking_pct(hm_stocking_df['TPA'], hm_stocking_df['QM_DBH'])
        hm_stocking_df = hm_stocking_df[[level, 'STOCK_PCT_HM']].set_index(level)

        # Create species richness df
        species_richness_df = fcalc.create_sp_richness(tree_table=tree_table,
                                                       plot_table=plot_table,
                                                       level=level)\
                                   .set_index(level)

        # Merge component dfs
        manage_summary_df = base_df \
            .join(other=[stocking_df,
                         hm_stocking_df,
                         species_richness_df],
                  how='left') \
            .reset_index()

        # Reindex output dataframe
        manage_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                            col_csv='resources/management_summary_cols.csv')
        manage_summary_df = manage_summary_df.reindex(labels=manage_reindex_cols,
                                                      axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Enforce ESRI compatible DTypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/management_summary_cols.csv')
        manage_summary_df = manage_summary_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Handle NAN values for output
        nan_fill_dict = fcalc.fmg_nan_fill(col_csv='resources/management_summary_cols.csv')
        manage_summary_df = manage_summary_df.fillna(value=nan_fill_dict)
        arcpy.AddMessage("    No data/nan values set")

        # Export to GDB Table
        table_name = 'PID_Management_Summary'
        table_path = os.path.join(out_gdb, table_name)
        manage_summary_df.spatial.to_table(table_path)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    arcpy.AddMessage('Complete')
    return table_path

