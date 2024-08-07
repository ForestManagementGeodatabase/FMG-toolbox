# Tool to assemble the summary tables into a set of feature classes for public visualization
# From Age Table: AGE_ORIG
# From Management: SP_RICH
# From General Descriptive: OV_CLSR_MEAN, UND_HT_RG, INV_PRESENT, LIVE_BA, INVT_YEAR, INV_SP
# From Health: DEAD_TPA, SD_TPA, STR_TPA, HLTH_TPA
# From Mast: HM_TPA
# From Vert Comp: CNP_DOM_HLTH, CNP_DOM_HLTH_PCMP, CNP_TPA, CNP_D_TPA, MID_DOM_HLTH, MID_DOM_HLTH_PCMP,
# MID_DOM_SP, MID_DOM_SP_PCMP, INT_DOM_SP, INT_DOM_SP_PCMP, INT_DOM_HLTH, INT_DOM_HLTH_PCMP

# Do Imports
import arcpy
import arcgis
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import pandas as pd

# Define input geodatabase with summary tables parameter
in_summary_gdb = arcpy.GetParameterAsText(0)

# Define FMG hierarchy levels for output parameters (script tool radio buttons)
site_view = arcpy.GetParameterAsText(1)
unit_view = arcpy.GetParameterAsText(2)
comp_view = arcpy.GetParameterAsText(3)
pool_view = arcpy.GetParameterAsText(4)

# Define FMG Hierarchy polygon feature class parameters (use validation to turn these on based on output levels
# selected above. See link for script tool validation code examples.
# https://pro.arcgis.com/en/pro-app/latest/arcpy/geoprocessing_and_python/customizing-script-tool-behavior.htm
site_poly = arcpy.GetParameterAsText(5)
unit_poly = arcpy.GetParameterAsText(6)
comp_poly = arcpy.GetParameterAsText(7)
pool_poly = arcpy.GetParameterAsText(8)

# Define output geodatabase (default to input geodatabase)
out_view_gdb = arcpy.GetParameterAsText(9)

# From input parameters, build a dictionary to guide work iterations
# Build list of levels to evaluate
levels = []
if site_view.lower() == 'true':
    levels.append('SITE')
if unit_view.lower() == 'true':
    levels.append('UNIT')
if comp_view.lower() == 'true':
    levels.append('COMP')
if pool_view.lower() == 'true':
    levels.append('POOL')

# Set GIS environments
arcpy.env.workspace = in_summary_gdb

# Pull list of all tables
summary_tables = arcpy.ListTables()

# Start work loop
for level in levels:
    level_tables = [i for i in summmary_tables if level in i]
    level_tables.sort()

    # make the dataframes
    df_age_sum = pd.DataFrame.spatial.from_table(level_tables[0])
    df_gen_sum = pd.DataFrame.spatial.from_table(level_tables[1])
    df_hlt_sum = pd.DataFrame.spatial.from_table(level_tables[2])
    df_mng_sum = pd.DataFrame.spatial.from_table(level_tables[3])
    df_mst_sum = pd.DataFrame.spatial.from_table(level_tables[4])
    df_vtc_sum = pd.DataFrame.spatial.from_table(level_tables[7])

    # Grab tables from input GDB