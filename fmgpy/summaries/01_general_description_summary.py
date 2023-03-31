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

# Define list of levels
levels = ['SID', 'SITE', 'UNIT']

# Allow output overwrite during testing
arcpy.env.overwriteOutput = True

# loop through levels, producing general description table for each
for level in levels:
    arcpy.AddMessage('Work on {0}'.format(level))

    # Create base table
    base_df = fcalc.create_level_df(level, plot_table)
    arcpy.AddMessage("    Base DF Created")

    # create total num age trees, total num plots, mean overstory closure, overstory closure std, mean overstory height,
    # overstory height std, mean understory cover, understory cover std, mean understory height, understory height std,
    # invasive species present, invasive species list -- source: plot table
    gendesc = plot_table \
        .groupby([level]) \
        .agg(
            NUM_PLOTS=('PID', fcalc.agg_plot_count),
            NUM_AGE_TR=('AGE_SP', 'count'),
            MEAN_OV_CLSR=('OV_CLSR', 'mean'),
            STD_OV_CLSR=('OV_CLSR', 'std'),
            MEAN_OV_HT=('OV_HT', 'mean'),
            STD_OV_HT=('OV_HT', 'std'),
            MEAN_UND_COV=('UND_COV', 'mean'),
            STD_UND_COV=('UND_COV', 'std'),
            MEAN_UND_HT=('UND_HT2', 'mean'),
            STD_UND_HT=('UND_HT2', 'std'),
            INV_PRESENT=('INV_PRESENT', 'first'),
            INV_SP=('INV_SP', fcalc.agg_inv_sp),
            NUM_FX_NOTES=('FX_MISC', fcalc.agg_count_notes),
            NUM_AGE_NOTES=('AGE_MISC', fcalc.agg_count_notes)
        ) \
        .reset_index() \
        .set_index([level])

    # Add mean under story height category values -- source: plot table
    gendesc['MEAN_UND_HT_RG'] = gendesc['MEAN_UND_HT'].map(fcalc.und_height_range_map)
    arcpy.AddMessage("    General DF Created")

    #  Calculate TPA & BA for live trees
    tpa_ba_live = fcalc.tpa_ba_qmdbh_level(tree_table=tree_table,
                                           filter_statement=~tree_table.TR_HLTH.isin(["D", "DEAD"]),
                                           level=level)

    # Clean up TPA & BA for live tree dataframe
    tpa_ba_live_df = tpa_ba_live\
        .drop(columns=['tree_count', 'stand_dens', 'plot_count']) \
        .rename(columns={'TPA': 'TPA_LIVE', 'BA': 'BA_LIVE', 'QM_DBH': 'QM_DBH_LIVE'}) \
        .set_index(level)
    arcpy.AddMessage("    TPA & BA Live Tree DF Created")

    # Calculate total num trees (all, no filter) -- source: tree table
    tr_all = tree_table \
        .groupby([level]) \
        .apply(fcalc.tree_count)

    # Convert tot num trees series to dataframe
    tr_all_df = pd.DataFrame({level: tr_all.index, 'NUM_TR': tr_all.values}).set_index([level])
    arcpy.AddMessage("    Total Tree Count DF Created")

    # Calculate total num live trees -- source: tree table
    tr_live = tree_table[~tree_table.TR_HLTH.isin(["D", "DEAD"])] \
        .groupby([level]) \
        .apply(fcalc.tree_count)

    # Convert tot num live trees series to dataframe
    tr_live_df = pd.DataFrame({level: tr_live.index, 'NUM_TR_LIVE': tr_live.values}).set_index([level])
    arcpy.AddMessage("    Total Live Tree Count DF Created")

    # Calculate total num dead trees -- source: tree table
    tr_dead = tree_table[tree_table.TR_HLTH.isin(["D", "DEAD"])] \
        .groupby([level]) \
        .apply(fcalc.tree_count)

    # Convert total num dead trees series to dataframe
    tr_dead_df = pd.DataFrame({level: tr_dead.index, 'NUM_TR_DEAD': tr_dead.values}).set_index([level])
    arcpy.AddMessage("    Total Dead Tree Count DF Created")

    # Average Mean Diameter live trees - tree table
    # Calculate Max DBH and Mean Diameter live trees -- source: tree table
    diam_df = tree_table[~tree_table.TR_HLTH.isin(["D", "DEAD"])] \
        .groupby([level]) \
        .agg(
            AMD=('TR_DIA', 'mean'),
            MAX_DBH=('TR_DIA', 'max')
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
    date_df["COL_YEAR"] = date_df.apply(lambda x: fcalc.date_range(x["min_year"], x["max_year"]), axis=1)

    # Clean up collection date dataframe
    date_df = date_df.drop(columns=['min_date', 'max_date', 'min_year', 'max_year']).set_index(level)
    arcpy.AddMessage("    Collection Date DF Created")

    # Merge component dataframes onto the base dataframe
    out_df = base_df \
        .join([gendesc,
               tpa_ba_live_df,
               tr_all_df,
               tr_live_df,
               tr_dead_df,
               diam_df,
               date_df],
              how='left')\
        .reset_index()
    arcpy.AddMessage("    All Component DFs Merged")

    # Export to gdb table
    table_name = "General_Summary_" + level
    table_path = os.path.join(out_gdb, table_name)
    out_df.spatial.to_table(table_path)
    arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

arcpy.AddMessage('Complete')
