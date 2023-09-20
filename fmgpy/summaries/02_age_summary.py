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
out_gdb = r"C:\LocalProjects\FMG\FMG_CODE_TESTING.gdb"

# Import ESRi feature classes as pandas dataframes
fixed_df = pd.DataFrame.spatial.from_featureclass(fixed_fc)
age_df = pd.DataFrame.spatial.from_featureclass(age_fc)

# Create plot dataframe
plot_table = fcalc.create_plot_table(fixed_df=fixed_df,
                                     age_df=age_df)

# Filter plot table to just records with age trees
age_plots = plot_table.query("AGE_ORIG==AGE_ORIG")
arcpy.AddMessage('Age table created')

# Define list of levels
levels = ['PID', 'SID', 'SITE', 'UNIT', 'COMP', 'POOL']

# Allow output overwrite during testing
arcpy.env.overwriteOutput = True

# loop through levels producing an ages summary table for each
for level in levels:
    arcpy.AddMessage('Work on {0}'.format(level))

    # Create Base DF
    base_df = fcalc.create_level_df(level=level,
                                    plot_table=plot_table)
    arcpy.AddMessage('    Base df created')

    # Calculate unfiltered metrics group by agg:
    # Avg level Age (mean AGE_ORIG)
    # Avg level Dia (mean AGE_DIA)
    # Age Growth Rate (mean AGE_GRW)
    # Age Regen Rate or Avg Understory Cover (mean UND_COV decimal truncated)
    unfiltered_metrics = age_plots\
        .groupby([level])\
        .agg(
            AGE_ORIG=('AGE_ORIG', 'mean'),
            AGE_DBH=('AGE_DIA', 'mean'),
            AGE_GRW=('AGE_GRW', 'mean'),
            AGE_UND_COV=('UND_COV', 'mean')
            )\
        .reset_index()
    arcpy.AddMessage('    Unfiltered df created')

    # Adjust data types & set index
    unfiltered_metrics = unfiltered_metrics.astype({'AGE_ORIG': 'int', 'AGE_UND_COV': 'int'})
    unfiltered_metrics = unfiltered_metrics.set_index(level)

    # Calculate filtered metrics
    # Avg Age Hard Mast
    hm_age = age_plots[age_plots.MAST_TYPE.isin(["H", "Hard"])]\
        .groupby([level])\
        .agg(HM_ORIG=('AGE_ORIG', 'mean'))\
        .reset_index()
    arcpy.AddMessage('    Hard mast df created')

    # Avg Age Soft Mast
    sm_age = age_plots[age_plots.MAST_TYPE.isin(["S", "Soft"])]\
        .groupby([level]) \
        .agg(SM_ORIG=('AGE_ORIG', 'mean')) \
        .reset_index()
    arcpy.AddMessage('    Soft Mast df created')

    # Avg Age Lightseed
    lm_age = age_plots[age_plots.MAST_TYPE.isin(["L", "Lightseed"])]\
        .groupby([level]) \
        .agg(LM_ORIG=('AGE_ORIG', 'mean'))\
        .reset_index()
    arcpy.AddMessage('    Lightseed df created')

    # Adjust data types
    hm_age['HM_ORIG'] = hm_age['HM_ORIG'].astype(int)
    sm_age['SM_ORIG'] = sm_age['SM_ORIG'].astype(int)
    lm_age['LM_ORIG'] = lm_age['LM_ORIG'].astype(int)

    # Set indexes
    hm_age = hm_age.set_index(level)
    sm_age = sm_age.set_index(level)
    lm_age = lm_age.set_index(level)

    # Merge
    out_df = base_df \
        .join([unfiltered_metrics,
               hm_age,
               sm_age,
               lm_age])\
        .reset_index()
    arcpy.AddMessage('    dfs merged')

    # Reindex output dataframe
    age_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                     col_csv="resources/age_summary_cols.csv")
    out_df = out_df.reindex(labels=age_reindex_cols,
                            axis='columns')
    arcpy.AddMessage("    Columns reordered")

    # Handle Nan values
    nan_fill_dict = fcalc.fmg_nan_fill(col_csv='resources/age_summary_cols.csv')
    out_df = out_df.fillna(value=nan_fill_dict)
    arcpy.AddMessage("    No data/nan values set")

    # Enforce ESRI compatible DTypes
    dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/age_summary_cols.csv')
    out_df = out_df.astype(dtype=dtype_dict, copy=False)
    arcpy.AddMessage("    Dtypes Enforced")

    # Export to gdb table
    table_name = level + "_Age_Summary"
    table_path = os.path.join(out_gdb, table_name)
    out_df.spatial.to_table(table_path)
    arcpy.AddMessage('    merged df exported to {0}'.format(table_path))

arcpy.AddMessage("Complete")
