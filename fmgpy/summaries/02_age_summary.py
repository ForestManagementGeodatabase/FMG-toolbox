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
arcpy.AddMessage('Plot table created')

# Filter plot table to just records with age trees
age_plots = plot_table.query("AGE_ORIG==AGE_ORIG")
arcpy.AddMessage('Age table created')

# Define list of levels
levels = ['PID', 'SID', 'SITE', 'UNIT']

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
            AGE_DIA=('AGE_DIA', 'mean'),
            AGE_GRW=('AGE_GRW', 'mean'),
            UND_COV=('UND_COV', 'mean')
            )\
        .reset_index()
    arcpy.AddMessage('    Unfiltered df created')

    # Adjust data types & set index
    unfiltered_metrics = unfiltered_metrics.astype({'AGE_ORIG':'int', 'UND_COV':'int'})
    unfiltered_metrics = unfiltered_metrics.set_index(level)

    # Calculate filtered metrics
    # Avg Age Hard Mast
    hm_age = age_plots[age_plots.MAST_TYPE.isin(["H", "Hard"])]\
        .groupby([level])\
        .agg(HARD_MAST_AGE=('AGE_ORIG', 'mean'))\
        .reset_index()
    arcpy.AddMessage('    Hard mast df created')

    # Avg Age Soft Mast
    sm_age = age_plots[age_plots.MAST_TYPE.isin(["S", "Soft"])]\
        .groupby([level]) \
        .agg(SOFT_MAST_AGE=('AGE_ORIG', 'mean')) \
        .reset_index()
    arcpy.AddMessage('    Soft Mast df created')

    # Avg Age Lightseed
    lm_age = age_plots[age_plots.MAST_TYPE.isin(["L", "Lightseed"])]\
        .groupby([level]) \
        .agg(LIGHTSEED_MAST_AGE=('AGE_ORIG', 'mean'))\
        .reset_index()
    arcpy.AddMessage('    Lightseed df created')

    # Adjust data types
    hm_age['HARD_MAST_AGE'] = hm_age['HARD_MAST_AGE'].astype(int)
    sm_age ['SOFT_MAST_AGE'] = sm_age['SOFT_MAST_AGE'].astype(int)
    lm_age ['LIGHTSEED_MAST_AGE'] = lm_age['LIGHTSEED_MAST_AGE'].astype(int)

    # Set indexs
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

    # Export to gdb table
    table_name = "AGE_Summary_" + level
    table_path = os.path.join(out_gdb, table_name)
    out_df.spatial.to_table(table_path)
    arcpy.AddMessage('    merged df exported to {0}'.format(table_path))

arcpy.AddMessage("Complete")




