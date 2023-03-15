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
import importlib
import fmgpy.summaries.forest_calcs as fcalc
import fmgpy.summaries.agg_function_testing as tcalc

# Define Some input data
output_gdb = r'C:\LocalProjects\FMG\LocalWorking\FMG_Code_Testing.gdb'
level = 'SID'
age = r'C:\LocalProjects\FMG\FMG-Toolbox\test\data\FMG_OracleSchema.gdb\AGE_PLOTS'
fixed = r'C:\LocalProjects\FMG\FMG-Toolbox\test\data\FMG_OracleSchema.gdb\FIXED_PLOTS'
prism = r'C:\LocalProjects\FMG\FMG-Toolbox\test\data\FMG_OracleSchema.gdb\PRISM_PLOTS'

# Reimport statements for dev changes
# importlib.reload(arcpy)
# importlib.reload(fcalc)
# importlib.reload(tcalc)

# Create dataframes
age_df = pd.DataFrame.spatial.from_featureclass(age)
fixed_df = pd.DataFrame.spatial.from_featureclass(fixed)
prism_df = pd.DataFrame.spatial.from_featureclass(prism)
### Console Testing Set Up End