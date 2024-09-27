# Tool to assemble the summary tables into a set of feature classes for forester visualization

# Do Imports
import os
import arcpy
import sys
import arcgis
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import pandas as pd
import fmglib.forest_calcs as fcalc

# Define input geodatabase with summary tables parameter
arcpy.AddMessage('Starting: Create FMG Forester View')
in_summary_gdb = arcpy.GetParameterAsText(0)

# Define FMG hierarchy levels for output parameters (script tool radio buttons)
plot_view = arcpy.GetParameterAsText(1)
stand_view = arcpy.GetParameterAsText(3)
site_view = arcpy.GetParameterAsText(5)
unit_view = arcpy.GetParameterAsText(7)
comp_view = arcpy.GetParameterAsText(9)
pool_view = arcpy.GetParameterAsText(11)

# Define FMG Hierarchy polygon feature class parameters
PLOT = arcpy.GetParameterAsText(2)
STAND = arcpy.GetParameterAsText(4)
SITE = arcpy.GetParameterAsText(6)
UNIT = arcpy.GetParameterAsText(8)
COMP = arcpy.GetParameterAsText(10)
POOL = arcpy.GetParameterAsText(12)

# Define output geodatabase
out_view_gdb = arcpy.GetParameterAsText(13)
arcpy.AddMessage('Input parameters defined')

# Build list of levels and dict of geometries
levels = []
summary_geom = {}
if plot_view.lower() == 'true':
    levels.append('PID')
    summary_geom.update(PID=PLOT)
if stand_view.lower() == 'true':
    levels.append('SID')
    summary_geom.update(SID=STAND)
if site_view.lower() == 'true':
    levels.append('SITE')
    summary_geom.update(SITE=SITE)
if unit_view.lower() == 'true':
    levels.append('UNIT')
    summary_geom.update(UNIT=UNIT)
if comp_view.lower() == 'true':
    levels.append('COMP')
    summary_geom.update(COMP=COMP)
if pool_view.lower() == 'true':
    levels.append('POOL')
    summary_geom.update(POOL=POOL)

# Set GIS environments
arcpy.env.workspace = in_summary_gdb

# Pull list of all tables
summary_tables = arcpy.ListTables()

# Create empty list to hold output feature classes
out_feature_classes = []
arcpy.AddMessage('Level list, workspace, and summary geometries defined')

# import field definitions
df_field_ref = pd.read_csv('resources/forester_view_cols.csv')

# Start work loop
for level in levels:
    arcpy.AddMessage('Creating public view table for {0}'.format(level))

    # Build and sort list of summary tables if they have the current loop's level in the name
    level_tables = [i for i in summary_tables if level in i]
    level_tables.sort()

    # make the dataframes
    df_age_sum = pd.DataFrame.spatial.from_table(level_tables[0]).set_index(level)
    df_age_ref = df_field_ref[df_field_ref['SRC_TAB'] == 'Age']
    df_age_flt = df_age_sum.filter(items=df_age_ref['COL_NAME'].tolist())

    df_gen_sum = pd.DataFrame.spatial.from_table(level_tables[1]).set_index(level)
    df_gen_ref = df_field_ref[df_field_ref['SRC_TAB'] == 'General']
    df_gen_flt = df_gen_sum.filter(items=df_gen_ref['COL_NAME'].tolist())

    df_hlt_sum = pd.DataFrame.spatial.from_table(level_tables[2]).set_index(level)
    df_hlt_ref = df_field_ref[df_field_ref['SRC_TAB'] == 'Health']
    df_hlt_flt = df_hlt_sum.filter(items=df_hlt_ref['COL_NAME'].tolist())

    df_man_sum = pd.DataFrame.spatial.from_table(level_tables[3]).set_index(level)
    df_man_ref = df_field_ref[df_field_ref['SRC_TAB'] == 'Management']
    df_man_flt = df_man_sum.filter(items=df_man_ref['COL_NAME'].tolist())

    df_mst_sum = pd.DataFrame.spatial.from_table(level_tables[4]).set_index(level)
    df_mst_ref = df_field_ref[df_field_ref['SRC_TAB'] == 'Mast']
    df_mst_flt = df_mst_sum.filter(items=df_mst_ref['COL_NAME'].tolist())

    df_siz_sum = pd.DataFrame.spatial.from_table(level_tables[5]).set_index(level)
    df_siz_ref = df_field_ref[df_field_ref['SRC_TAB'] == 'Size']
    df_siz_flt = df_siz_sum.filter(items=df_siz_ref['COL_NAME'].tolist())

    df_spc_sum = pd.DataFrame.spatial.from_table(level_tables[6]).set_index(level)
    df_spc_ref = df_field_ref[df_field_ref['SRC_TAB'] == 'Species']
    df_spc_flt = df_spc_sum.filter(items=df_spc_ref['COL_NAME'].tolist())

    df_vtc_sum = pd.DataFrame.spatial.from_table(level_tables[7]).set_index(level)
    df_vtc_ref = df_field_ref[df_field_ref['SRC_TAB'] == 'Vertical']
    df_vtc_flt = df_vtc_sum.filter(items=df_vtc_ref['COL_NAME'].tolist())

    df_geometry = pd.DataFrame.spatial.from_featureclass(summary_geom[level]).set_index(level)
    df_geometry = df_geometry.drop(columns=['LAST_EDITED_DATE', 'LAST_EDITED_USER', 'CREATED_DATE', 'CREATED_USER',
                                            'SE_ANNO_CAD_DATA', 'OBJECTID'],
                                   errors='ignore')
    arcpy.AddMessage('    Tabular dataframes created')

    # make supporting geom df using the current loop's level as a key to extract path value from dict
    df_geometry = pd.DataFrame.spatial.from_featureclass(summary_geom[level]).set_index(level)
    arcpy.AddMessage('    Spatial dataframe created')

    # merge component dfs
    df_merged = df_geometry\
        .join(other=[df_age_flt,
                     df_gen_flt,
                     df_hlt_flt,
                     df_man_flt,
                     df_mst_flt,
                     df_siz_flt,
                     df_spc_flt,
                     df_vtc_flt],
              how='left')\
        .reset_index()
    arcpy.AddMessage('    Dataframes merged to create forester view')

    df_clean = df_merged.round(decimals=2)

    # Reindex output df
    reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                 col_csv='resources/forester_view_cols.csv')
    out_df = df_clean.reindex(labels=reindex_cols,
                              axis='columns')
    arcpy.AddMessage('    Create and reindex output dataframe')

    # Handle nan values appropriately
    nan_fill_dict = fcalc.fmg_nan_fill(col_csv='resources/forester_view_cols.csv')
    out_df = out_df\
        .fillna(value=nan_fill_dict)\
        .drop(columns=['index'], errors='ignore')
    arcpy.AddMessage('    Output dataframe nan values filled')

    # Enforce ESRI Compatible Dtypes
    dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/forester_view_cols.csv')
    out_df = out_df.astype(dtype=dtype_dict, copy=False)
    arcpy.AddMessage('    Output dataframe ESRI-compatible dtypes enforced')

    # send back to ESRI-land
    out_fc = os.path.join(out_view_gdb, f"{level}_ForesterView")
    out_feature_classes.append(out_fc)
    out_df.spatial.to_featureclass(location=out_fc,
                                   has_z=False,
                                   has_m=False,
                                   sanitize_columns=False)
    arcpy.AddMessage('    Output dataframe exported to {0}'.format(out_fc))

# Make pretty ESRI land data
arcpy.AddMessage('Setting field aliases for exported public views')

# Create dictionary for field name: field alias from field reference csv import
alias_dict = None
if len(df_field_ref.index) > 0:
    alias_keys = df_field_ref['COL_NAME'].values.tolist()
    alias_vals = df_field_ref['ALIAS'].values.tolist()
    alias_dict = dict(zip(alias_keys, alias_vals))
arcpy.AddMessage('Alias dictionary created')

# Iterate through output feature classes, setting field name alias
for feature_class in out_feature_classes:
    arcpy.AddMessage('Setting aliases on {0}'.format(feature_class))
    for field, alias in alias_dict.items():
        arcpy.management.AlterField(in_table=feature_class,
                                    field=field,
                                    new_field_alias=alias)
        arcpy.AddMessage('    Alias set on {0}'.format(field))
    arcpy.AddMessage('Aliases Set')
arcpy.AddMessage('Complete: Create FMG Public View')

# Set output parameter from out_feature_classes list
arcpy.SetParameter(14, out_feature_classes)

