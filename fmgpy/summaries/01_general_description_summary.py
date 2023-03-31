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


# Create base table
base_df = create_level_df(level, plot_table)

# total num age trees - plot table
# total num plots (all, no filter) - plot table
# mean overstory closure - plot table
# overstory closure standard deviation - plot table
# mean overstory height - plot table
# overstory height standard deviation - plot table
# mean understory cover - plot table
# understory cover standard deviation - plot table
# mean understory height (number) - plot table
# understory height standard deviation - plot table
# invasive species present - plot table
# invasive species list - plot table
gendesc = plot_table \
    .groupby([level]) \
    .agg(
    NUM_PLOTS=('PID', agg_plot_count),
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
    INV_SP=('INV_SP', agg_inv_sp),
    NUM_FX_NOTES=('FX_MISC', agg_count_notes),
    NUM_AGE_NOTES=('AGE_MISC', agg_count_notes)
) \
    .reset_index() \
    .set_index([level])

# mean under story height (range value) - plot table
gendesc['MEAN_UND_HT_RG'] = gendesc['MEAN_UND_HT'].map(und_height_range_map)

# TPA & BA for live trees
tpa_ba_live = tpa_ba_qmdbh_level(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]), level)
tpa_ba_live_df = tpa_ba_live\
    .drop(columns=['tree_count', 'stand_dens', 'plot_count']) \
    .rename(columns={'TPA': 'TPA_LIVE', 'BA': 'BA_LIVE', 'QM_DBH': 'QM_DBH_LIVE'}) \
    .set_index(level)

# total num trees (all, no filter) - tree table
tr_all = tree_table \
    .groupby([level]) \
    .apply(tree_count)
tr_all_df = pd.DataFrame({level: tr_all.index, 'NUM_TR': tr_all.values}).set_index([level])

# total num live trees - tree table
tr_live = tree_table[~tree_table.TR_HLTH.isin(["D", "DEAD"])] \
    .groupby([level]) \
    .apply(tree_count)
tr_live_df = pd.DataFrame({level: tr_live.index, 'NUM_TR_LIVE': tr_live.values}).set_index([level])

# total num dead trees - tree table
tr_dead = tree_table[tree_table.TR_HLTH.isin(["D", "DEAD"])] \
    .groupby([level]) \
    .apply(tree_count)
tr_dead_df = pd.DataFrame({level: tr_dead.index, 'NUM_TR_DEAD': tr_dead.values}).set_index([level])

# Average Mean Diameter live trees - tree table
# Max DBH live trees - tree table
diam_df = tree_table[~tree_table.TR_HLTH.isin(["D", "DEAD"])] \
    .groupby([level]) \
    .agg(
    AMD=('TR_DIA', 'mean'),
    MAX_DBH=('TR_DIA', 'max')
) \
    .reset_index() \
    .set_index([level])

# Collection date
date_df = tree_table\
    .groupby([level], as_index=False) \
    .agg(
        min_date=('COL_DATE', 'min'),
        max_date=('COL_DATE', 'max')
        )
date_df['min_year'] = date_df['min_date'].dt.year
date_df['max_year'] = date_df['max_date'].dt.year
date_df["COL_YEAR"] = date_df.apply(lambda x: date_range(x["min_year"], x["max_year"]), axis=1)

date_df = date_df.drop(columns=['min_date', 'max_date', 'min_year', 'max_year']).set_index(level)

# merge component dataframes
gendesc_df = base_df \
    .join([gendesc,
           tpa_ba_live_df,
           tr_all_df,
           tr_live_df,
           tr_dead_df,
           diam_df,
           date_df],
          how='left') \
    .reset_index()