### Console Testing Set Up Start
# Do Some Imports
import os
import sys
import arcpy
import arcgis
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import math
import pandas as pd
import numpy as np
import itertools
import importlib
import fmgpy.summaries.forest_calcs as fcalc


# Define Some input data
output_gdb = r'C:\LocalProjects\FMG\LocalWorking\FMG_Code_Testing.gdb'
level = 'SID'
age = r'C:\LocalProjects\FMG\FMG-Toolbox\test\data\FMG_OracleSchema.gdb\AGE_PLOTS'
fixed = r'C:\LocalProjects\FMG\FMG-Toolbox\test\data\FMG_OracleSchema.gdb\FIXED_PLOTS'
prism = r'C:\LocalProjects\FMG\FMG-Toolbox\test\data\FMG_OracleSchema.gdb\PRISM_PLOTS'
filter_statement = None

# Reimport statements for dev changes
# importlib.reload(arcpy)
# importlib.reload(fcalc)
# importlib.reload(tcalc)

# Create dataframes
age_df = pd.DataFrame.spatial.from_featureclass(age)
fixed_df = pd.DataFrame.spatial.from_featureclass(fixed)
prism_df = pd.DataFrame.spatial.from_featureclass(prism)
tree_table = fcalc.create_tree_table(prism_df)
plot_table = fcalc.create_plot_table(fixed_df, age_df)
### Console Testing Set Up End