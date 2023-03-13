"""General Descriptive Forest Metrics Summary Table

Create a table of metrics used to describe the forest at a high level.

:param: output_gdb      str; Path the output geodatabase.
:param: level           str; The FMG hierarchical level. One of: "unit",
                        "site", "stand", "plot".
:param: age             str; Path to the FMG "Age" point feature class.
:param: fixed           str; Path to the FMG "Fixed" point feature class.
:param: prism           str; Path to the FMG "Prism" point feature class.

:return: Writes a geodatabase table containing a field for each metric in the
general descriptive tabel. The table is named "general_descriptive_metrics" with
suffix for the level.
"""
import os
import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import pandas as pd
import importlib
import fmgpy.summaries.forest_calcs
import fmgpy.summaries.agg_function_testing
import numpy

# Ensure changes are reloaded during interactive development session
importlib.reload(arcpy)
importlib.reload(forest_calcs)

arcpy.env.overwriteOutput = True

# Define input parameters
output_gdb = r'C:\LocalProjects\FMG\FMG_CODE_TESTING.gdb'  # arcpy.GetParameterAsText(0)
level = fmgpy.summaries.forest_calcs.fmg_level('site')  # arcpy.GetParameterAsText(1)
age = r'C:\LocalProjects\FMG\FMG-toolbox\test\data\FMG_OracleSchema.gdb\AGE_PLOTS'  # arcpy.GetParameterAsText(2)
fixed = r'C:\LocalProjects\FMG\FMG-toolbox\test\data\FMG_OracleSchema.gdb\FIXED_PLOTS'  # arcpy.GetParameterAsText(3)
prism = r'C:\LocalProjects\FMG\FMG-toolbox\test\data\FMG_OracleSchema.gdb\PRISM_PLOTS'  # arcpy.GetParameterAsText(4)


prism_df = pd.DataFrame.spatial.from_featureclass(prism)

# tried this
site_tpa = prism_df.groupby(level).agg(fmgpy.summaries.forest_calcs.tpa(prism_df))

# then tried this
site_tpa = prism_df.groupby(level).agg(float(fmgpy.summaries.forest_calcs.tpa(prism_df)))

# and then
site_tpa = prism_df.groupby(level).agg(numpy.float64(fmgpy.summaries.forest_calcs.tpa(prism_df)))

# and then
site_tpa = prism_df.groupby(level, as_index=False).agg(fmgpy.summaries.forest_calcs.tpa(prism_df))

# and then
site_tpa = prism_df.groupby(level, as_index=False).apply(fmgpy.summaries.forest_calcs.tpa(prism_df))

# amd then
site_tpa = prism_df.groupby(level, as_index=False).agg(10 / (0.005454 * (prism_df['TR_DIA'] ** 2)) / fmgpy.summaries.forest_calcs.plot_count(prism_df))

# and then
site_tpa = prism_df.groupby(level, as_index=False).agg(
    plot_count=('PID', 'nunique'),
    tree_count=('TR_SP', fmgpy.summaries.agg_function_testing.treecount)
)



