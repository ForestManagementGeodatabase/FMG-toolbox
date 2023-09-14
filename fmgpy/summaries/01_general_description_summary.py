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

# Define inputs
fixed_fc = r"C:\LocalProjects\FMG\FMG-toolbox\test\data\FMG_OracleSchema.gdb\FIXED_PLOTS"
age_fc = r"C:\LocalProjects\FMG\FMG-toolbox\test\data\FMG_OracleSchema.gdb\AGE_PLOTS"
prism_fc = r"C:\LocalProjects\FMG\FMG-toolbox\test\data\FMG_OracleSchema.gdb\PRISM_PLOTS"
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

# loop through levels, producing general description table for each
for level in levels:
    if level != 'PID':
        arcpy.AddMessage('Work on {0}'.format(level))

        # Create base table
        base_df = fcalc.create_level_df(level, plot_table)
        arcpy.AddMessage("    Base DF Created")

        # create total num age trees, total num plots, mean overstory closure, overstory closure std,
        # mean overstory height, overstory height std, mean understory cover, understory cover std,
        # mean understory height, understory height std, invasive species present, invasive species
        # list -- source: plot table
        gendesc = plot_table \
            .groupby([level]) \
            .agg(
                PLOT_CT=('PID', fcalc.agg_plot_count),
                TR_AGE_CT=('AGE_SP', 'count'),
                OV_CLSR_MEAN=('OV_CLSR', 'mean'),
                OV_CLSR_STD=('OV_CLSR', 'std'),
                OV_HT_MEAN=('OV_HT', 'mean'),
                OV_HT_STD=('OV_HT', 'std'),
                UND_COV_MEAN=('UND_COV', 'mean'),
                UND_COV_STD=('UND_COV', 'std'),
                UND_HT_MEAN=('UND_HT2', 'mean'),
                UND_HT_STD=('UND_HT2', 'std'),
                INV_PRESENT=('INV_PRESENT', 'first'),
                INV_SP=('INV_SP', fcalc.agg_inv_sp),
                NUM_FIX_NOTES=('FX_MISC', fcalc.agg_count_notes),
                NUM_AGE_NOTES=('AGE_MISC', fcalc.agg_count_notes)
            ) \
            .reset_index() \
            .set_index([level])

        # Add mean under story height category values -- source: plot table
        gendesc['UND_HT_RG'] = gendesc['UND_HT_MEAN'].map(fcalc.und_height_range_map)
        arcpy.AddMessage("    General DF Created")

        #  Calculate TPA & BA for live trees
        tpa_ba_live = fcalc.tpa_ba_qmdbh_level(tree_table=tree_table,
                                               filter_statement=~tree_table.TR_HLTH.isin(["D", "DEAD"]),
                                               level=level)

        # Clean up TPA & BA for live tree dataframe
        tpa_ba_live_df = tpa_ba_live\
            .drop(columns=['tree_count', 'stand_dens', 'plot_count']) \
            .rename(columns={'TPA': 'LIVE_TPA', 'BA': 'LIVE_BA', 'QM_DBH': 'LIVE_QMDBH'}) \
            .set_index(level)
        arcpy.AddMessage("    TPA & BA Live Tree DF Created")

        # Calculate total num trees (all, no filter) -- source: tree table
        tr_all = tree_table \
            .groupby([level]) \
            .apply(fcalc.tree_count)

        # Convert tot num trees series to dataframe
        tr_all_df = pd.DataFrame({level: tr_all.index, 'TR_CT': tr_all.values}).set_index([level])
        arcpy.AddMessage("    Total Tree Count DF Created")

        # Calculate total num live trees -- source: tree table
        tr_live = tree_table[~tree_table.TR_HLTH.isin(["D", "DEAD"])] \
            .groupby([level]) \
            .apply(fcalc.tree_count)

        # Convert tot num live trees series to dataframe
        tr_live_df = pd.DataFrame({level: tr_live.index, 'TR_LV_CT': tr_live.values}).set_index([level])
        arcpy.AddMessage("    Total Live Tree Count DF Created")

        # Calculate total num dead trees -- source: tree table
        tr_dead = tree_table[tree_table.TR_HLTH.isin(["D", "DEAD"])] \
            .groupby([level]) \
            .apply(fcalc.tree_count)

        # Convert total num dead trees series to dataframe
        tr_dead_df = pd.DataFrame({level: tr_dead.index, 'TR_D_CT': tr_dead.values}).set_index([level])
        arcpy.AddMessage("    Total Dead Tree Count DF Created")

        # Average Mean Diameter live trees - tree table
        # Calculate Max DBH and Mean Diameter live trees -- source: tree table
        diam_df = tree_table[~tree_table.TR_HLTH.isin(["D", "DEAD"])] \
            .groupby([level]) \
            .agg(
                LIVE_AMD=('TR_DIA', 'mean'),
                LIVE_MAX_DBH=('TR_DIA', 'max')
            ) \
            .reset_index() \
            .set_index([level])
        arcpy.AddMessage("    AMD and Max DBH for Live Trees DF Created")

        # Calculate collection date
        date_df = tree_table\
            .groupby([level], as_index=False) \
            .agg(
                min_date=('COL_DATE', 'min'),
                max_date=('COL_DATE', 'max')
                )
        date_df['min_year'] = date_df['min_date'].dt.year
        date_df['max_year'] = date_df['max_date'].dt.year
        date_df["INVT_YEAR"] = date_df.apply(lambda x: fcalc.date_range(x["min_year"], x["max_year"]), axis=1)

        # Clean up collection date dataframe
        date_df = date_df.drop(columns=['min_date', 'max_date', 'min_year', 'max_year']).set_index(level)
        arcpy.AddMessage("    Collection Date DF Created")

        # Merge component dataframes onto the base dataframe
        out_df = base_df \
            .join(other=[gendesc,
                         tpa_ba_live_df,
                         tr_all_df,
                         tr_live_df,
                         tr_dead_df,
                         diam_df,
                         date_df],
                  how='left')\
            .reset_index()
        arcpy.AddMessage("    All Component DFs Merged")

        # Reindex output dataframe
        general_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                             col_csv='fmgpy/summaries/resources/general_summary_cols.csv')
        out_df = out_df.reindex(labels=general_reindex_cols,
                                axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Handle NaN values appropriately
        nan_fill_dict_level = fcalc.fmg_nan_fill(col_csv='fmgpy/summaries/resources/general_summary_cols.csv')

        out_df = out_df\
            .fillna(value=nan_fill_dict_level)\
            .drop(columns=['index'], errors='ignore')\
            .replace({'INV_SP': {"": 'NONE', " ": 'NONE', None: 'NONE'}})
        arcpy.AddMessage("    Nan Values Filled")

        # Enforce ESRI compatible Dtypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='fmgpy/summaries/resources/general_summary_cols.csv')
        out_df = out_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Export to gdb table
        table_name = level + "_General_Summary"
        table_path = os.path.join(out_gdb, table_name)
        out_df.spatial.to_table(location=table_path, sanitize_columns=False)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    elif level == 'PID':
        arcpy.AddMessage('Work on {0}'.format(level))
        # Drop unecessary plot table columns
        plot_metrics = plot_table.drop(columns=
                                       ['UND_SP1', 'UND_SP2', 'UND_SP3',
                                        'GRD_SP1', 'GRD_SP2', 'GRD_SP3',
                                        'NOT_SP1', 'NOT_SP2', 'NOT_SP3',
                                        'NOT_SP4', 'NOT_SP5',
                                        'COL_CREW', 'AGENCY', 'DISTRICT',
                                        'ITERATION', 'SHAPE'])

        # Rename Columns
        plot_metrics = plot_metrics.rename(columns={'AGE_MISC': 'AGE_NOTE',
                                                    'FX_MISC': 'FIXED_NOTE',
                                                    'UND_HT': 'UND_HT_RG',
                                                    'UND_HT2': 'UND_HT_MEAN',
                                                    'MAST_TYPE': 'AGE_MAST_TYPE'})

        # Create and populate inventory year column
        plot_metrics['INVT_YEAR'] = plot_metrics['COL_DATE'].dt.year
        plot_metrics = plot_metrics.set_index('PID')

        # Create BA, TPA, QM DBH
        plot_ba_tpa = fcalc.tpa_ba_qmdbh_plot(tree_table=tree_table,
                                              filter_statement=~tree_table.TR_HLTH.isin(["D", "DEAD"]))

        # Clean up TPA & BA for live tree dataframe
        plot_tpa_ba_live_df = plot_ba_tpa\
            .drop(columns=['tree_count', 'stand_dens', 'plot_count'], errors='ignore') \
            .rename(columns={'TPA': 'LIVE_TPA', 'BA': 'LIVE_BA',
                             'QM_DBH': 'LIVE_QMDBH', 'plot_count': 'PLOT_CT'}) \
            .set_index('PID')
        arcpy.AddMessage("    TPA & BA Live Tree DF Created")

        # Calculate total num trees (all, no filter) -- source: tree table
        plot_tr_all = tree_table \
            .groupby('PID') \
            .apply(fcalc.tree_count)

        # Convert tot num trees series to dataframe
        plot_tr_all_df = pd.DataFrame({'PID': plot_tr_all.index, 'TR_CT': plot_tr_all.values}).set_index('PID')
        arcpy.AddMessage("    Total Tree Count DF Created")

        # Calculate total num live trees -- source: tree table
        plot_tr_live = tree_table[~tree_table.TR_HLTH.isin(["D", "DEAD"])] \
            .groupby('PID') \
            .apply(fcalc.tree_count)

        # Convert tot num live trees series to dataframe
        plot_tr_live_df = pd.DataFrame({'PID': plot_tr_live.index, 'TR_LV_CT': plot_tr_live.values}).set_index('PID')
        arcpy.AddMessage("    Total Live Tree Count DF Created")

        # Calculate total num dead trees -- source: tree table
        plot_tr_dead = tree_table[tree_table.TR_HLTH.isin(["D", "DEAD"])] \
            .groupby('PID') \
            .apply(fcalc.tree_count)

        # Convert total num dead trees series to dataframe
        plot_tr_dead_df = pd.DataFrame({'PID': plot_tr_dead.index, 'TR_D_CT': plot_tr_dead.values}).set_index('PID')
        arcpy.AddMessage("    Total Dead Tree Count DF Created")

        # Average Mean Diameter live trees - tree table
        # Calculate Max DBH and Mean Diameter live trees -- source: tree table
        plot_diam_df = tree_table[~tree_table.TR_HLTH.isin(["D", "DEAD"])] \
            .groupby('PID') \
            .agg(
            LIVE_AMD=('TR_DIA', 'mean'),
            LIVE_MAX_DBH=('TR_DIA', 'max')
            ) \
            .reset_index() \
            .set_index('PID')
        arcpy.AddMessage("    AMD and Max DBH for Live Trees DF Created")

        # Merge component dataframes onto the base dataframe
        out_df = plot_metrics \
            .join([plot_tpa_ba_live_df,
                   plot_tr_all_df,
                   plot_tr_live_df,
                   plot_tr_dead_df,
                   plot_diam_df],
                  how='left') \
            .reset_index()
        arcpy.AddMessage("    All Component DFs Merged")

        # reindex output dataframe
        general_reindex_cols = \
            fcalc.fmg_column_reindex_list(level=level,
                                          col_csv='fmgpy/summaries/resources/general_summary_cols_pid.csv')
        out_df = out_df.reindex(labels=general_reindex_cols,
                                axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Handle NaN values appropriately
        nan_fill_dict_pid = fcalc.fmg_nan_fill(col_csv='fmgpy/summaries/resources/general_summary_cols_pid.csv')

        out_df = out_df\
            .fillna(value=nan_fill_dict_pid) \
            .replace({'AGE_NOTE': {None: "", " ": ""}})\
            .drop(columns=['index'], errors='ignore')
        arcpy.AddMessage("    Nan Values Filled")

        # Enforce ESRI compatible DTypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='fmgpy/summaries/resources/general_summary_cols_pid.csv')
        out_df = out_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Export to gdb table
        table_name = "PID_General_Summary"
        table_path = os.path.join(out_gdb, table_name)
        out_df.spatial.to_table(location=table_path, sanitize_columns=False)
        arcpy.AddMessage('    DataFrame exported to {0}'.format(table_path))

arcpy.AddMessage('Complete')
