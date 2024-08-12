# Tool to assemble the summary tables into a set of feature classes for public visualization
# From Age Table: AGE_ORIG
# From Management: SP_RICH
# From General Descriptive: OV_CLSR_MEAN, UND_HT_RG, INV_PRESENT, LIVE_BA, INVT_YEAR, INV_SP
# From Health: DEAD_TPA, SD_TPA, STR_TPA, HLTH_TPA
# From Mast: HM_TPA
# From Vert Comp: CNP_DOM_HLTH, CNP_DOM_HLTH_PCMP, CNP_TPA, CNP_D_TPA, MID_DOM_HLTH, MID_DOM_HLTH_PCMP,
# MID_DOM_SP, MID_DOM_SP_PCMP, INT_DOM_SP, INT_DOM_SP_PCMP, INT_DOM_HLTH, INT_DOM_HLTH_PCMP

# Do Imports
import os
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
SITE = arcpy.GetParameterAsText(5)
UNIT = arcpy.GetParameterAsText(6)
COMP = arcpy.GetParameterAsText(7)
POOL = arcpy.GetParameterAsText(8)

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

# Create dict of geometry parameters
summary_geom = {'SITE': SITE, 'UNIT': UNIT, 'COMP': COMP, 'POOL': POOL}

# Start work loop
for level in levels:
    level_tables = [i for i in summary_tables if level in i]
    level_tables.sort()

    # make the dataframes
    df_age_sum = pd.DataFrame.spatial.from_table(level_tables[0]).set_index(level)
    df_gen_sum = pd.DataFrame.spatial.from_table(level_tables[1]).set_index(level)
    df_hlt_sum = pd.DataFrame.spatial.from_table(level_tables[2]).set_index(level)
    df_mst_sum = pd.DataFrame.spatial.from_table(level_tables[4]).set_index(level)
    df_vtc_sum = pd.DataFrame.spatial.from_table(level_tables[7]).set_index(level)

    # make supporting geom df
    df_geometry = pd.DataFrame.spatial.from_featureclass(summary_geom[level]).set_index(level)

    # Create new dfs with just the required columns
    df_age_filt = df_age_sum.filter(items=['AGE_ORIG'])
    df_gen_filt = df_gen_sum.filter(items=['OV_CLSR_MEAN', 'UND_HT_RG', 'LIVE_BA',
                                           'INV_PRESENT', 'INV_SP', 'INVT_YEAR'])
    df_hlt_filt = df_hlt_sum.filter(items=['DEAD_TPA', 'SD_TPA', 'STR_TPA', 'HLTH_TPA'])
    df_mst_filt = df_mst_sum.filter(items=['HM_TPA'])
    df_vtc_filt = df_vtc_sum.filter(items=['CNP_TPA', 'CNP_D_TPA', 'CNP_DOM_HLTH', 'CNP_DOM_HLTH_PCMP',
                                           'CNP_DOM_SP', 'CNP_DOM_SP_PCMP', 'MID_DOM_HLTH', 'MID_COM_HLTH_PCMP',
                                           'MID_DOM_SP', 'MID_DOM_SP_PCMP', 'INT_DOM_HLTH', 'INT_DOM_HLTH_PCMP',
                                           'INT_DOM_SP', 'INT_DOM_SP_PCMP'])
    df_geometry = df_geometry.drop(columns=['LAST_EDITED_DATE', 'LAST_EDITED_USER', 'CREATED_DATE', 'CREATED_USER',
                                            'SE_ANNO_CAD_DATA', 'OBJECTID'])

    # merge component dfs
    df_merged = df_geometry\
        .join(other=[df_gen_filt,
                     df_mst_filt,
                     df_age_filt,
                     df_hlt_filt,
                     df_vtc_filt],
              how='left')\
        .reset_index()

    df_clean = df_merged.round(decimals=2)

    # send back to ESRI-land
    out_fc = os.path.join(out_view_gdb, f"{level}_PublicView")
    df_clean.spatial.to_featureclass(location=out_fc,
                                     has_z=False,
                                     has_m=False,
                                     sanitize_columns=False)

    # Make pretty ESRI land data




