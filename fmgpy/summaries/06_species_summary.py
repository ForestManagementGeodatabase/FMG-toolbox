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

        # UND_SP1 Most Frequent
        und_sp1_flt = fixed_df[~fixed_df.UND_SP1.isin(['NONE'])]

        und_sp1_freq = fcalc.get_groupby_modes(
            source=und_sp1_flt,
            keys=[level],
            values=['UND_SP1'],
            dropna=True,
            return_counts=False)\
            .set_index(level)

        # UND_SP2 Most Frequent
        # UND_SP3 Most Frequent
        # GRD_SP1 Most Frequent
        # GRD_SP2 Most Frequent
        # GRD_SP3 Most Frequent
        # NOT_SP1 Most Frequent
        # NOT_SP2 Most Frequent
        # NOT_SP3 Most Frequent