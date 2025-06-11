# -*- coding: UTF-8 -*-
# FMG QA Tools Function Library

import os
import sys
import arcpy
import re
import pandas as pd
from pathlib import Path
from pandas.api.types import is_string_dtype, is_numeric_dtype
import numpy as np
from arcgis.features import GeoAccessor, GeoSeriesAccessor

arcpy.env.overwriteOutput = True


def yes_no(df_name, field_name):
    df_name[field_name] = df_name[field_name].astype(str)
    df_name[field_name] = df_name[field_name].replace({'False': "No", 'True': "Yes"})


def get_value(d, val):
    for k, v in d.items():
        if k == val:
            return v


def match(col_a, col_b):
    if col_a == col_b:
        return "Yes"
    else:
        return "No"


def cast_as_int(df_name):
    col_list = list(df_name.select_dtypes(include=['Int64', 'int64', 'Int32']))
    for i in col_list:
        if i == 'OBJECTID':
            pass
        else:
            df_name[i] = df_name[i].astype('Int32')


def rename_fields(df, user_field, field_name):
    """Checks if required field name is already in use in dataset and, if different from supplied field,
    renames original field before renaming supplied field to prevent duplicate field names

    Keyword Arguments:
    df         -- Input dataframe
    user_field -- User-supplied name of required field
    field_name -- Required field name
    """
    # check if field name exists in dataset
    if field_name in df.columns:
        if field_name == user_field:
            # if required field name exists in the dataset and is the same as the supplied name, do nothing
            pass
        elif field_name != user_field:
            # if required field name exists and is different from the user-supplied name, rename existing field first
            new_field_name = field_name + "_old"
            df = df.rename(columns={field_name: new_field_name,
                                    user_field: field_name})
    else:
        # if field name doesn't exist in dataset, rename supplied field
        df = df.rename(columns={user_field: field_name})

    return df


def check_plot_ids(fc_center, center_plot_id_field, fc_check, check_plot_id_field, plot_id_string):
    """Checks plot IDs on a given input FMG field dataset (Fixed, Prism, Age) based on a list
    of plot IDs generated from a primary set of plot IDs, this primary set of plot IDs can be the
    target shapefile of plot locations used in TerraSync, the target Plot feature class used in
    TerraFlex/Collector or the Fixed plot locations, assuming that the fixed plots have correct
    Plot IDs. The function returns the string path to the checked dataset.

    Keyword Arguments:
    fc_center            --  The path to the feature class or table that contains the full list
                             of plot IDs, against which the field data will be checked.
    center_plot_id_field --  The field name containing Plot IDs
    fc_check             --  The path to the feature class or table that contains the field
                             data requiring plot ID checks
    check_plot_id_field  --  The field name containing Plot IDs
    """

    # check inputs

    arcpy.AddMessage(
        f"\nChecking Plot ID fields for {os.path.basename(fc_check)}"
    )

    # create dataframes and handle integer dtypes
    center_df = pd.DataFrame.spatial.from_featureclass(fc_center)
    check_df = pd.DataFrame.spatial.from_featureclass(fc_check)
    cast_as_int(center_df)
    cast_as_int(check_df)

    if plot_id_string.lower() == 'false':
        # check main plot ID field to ensure it is integer
        if center_df[center_plot_id_field].dtype == 'int64':
            pass
        else:
            try:
                center_df[center_plot_id_field] = center_df[center_plot_id_field].astype(int)
            except:
                arcpy.AddError(f"    {os.path.basename(fc_center)} plot ID field type must be short "
                               f"or long integer, quitting.")
                center_df.spatial.to_featureclass(fc_center,
                                                  overwrite=True,
                                                  sanitize_columns=False)
                sys.exit(0)

        # check input plot ID field to ensure it is integer
        if check_df[check_plot_id_field].dtype == 'int64':
            arcpy.AddMessage(f"    {os.path.basename(fc_check)} plot ID field type is correct")
        else:
            try:
                check_df[check_plot_id_field] = check_df[check_plot_id_field].astype(int)
            except:
                arcpy.AddError(f"    {os.path.basename(fc_check)} plot ID field type must be short "
                               f"or long integer, quitting.")
                check_df.spatial.to_featureclass(fc_check,
                                                 overwrite=True,
                                                 sanitize_columns=False)
                sys.exit(0)

    # check main plot ID field for duplicate values
    # if duplicates found, quit with message
    duplicate_plots = center_df[center_df.duplicated([center_plot_id_field])]

    if len(duplicate_plots.index) > 0:
        center_df["DUPLICATE_PLOT_ID"] = center_df[center_plot_id_field].isin(duplicate_plots[center_plot_id_field])
        yes_no(center_df, "DUPLICATE_PLOT_ID")

        arcpy.AddError(f"    Duplicate plot IDs found in {os.path.basename(fc_center)}, quitting."
                       f" Check flag field '"'DUPLICATE_PLOT_ID'"' and re-number plots before running again")
        center_df.spatial.to_featureclass(fc_center,
                                          overwrite=True,
                                          sanitize_columns=False)
        sys.exit(0)

    # flag plot IDs not in main fc (returns boolean)
    check_df["VALID_PLOT_ID"] = check_df[check_plot_id_field].isin(center_df[center_plot_id_field])
    yes_no(check_df, 'VALID_PLOT_ID')

    arcpy.AddMessage(f"VALID_PLOT_ID populated, check complete")

    # overwrite input FC
    center_df.spatial.to_featureclass(fc_center,
                                      overwrite=True,
                                      sanitize_columns=False)
    check_df.spatial.to_featureclass(fc_check,
                                     overwrite=True,
                                     sanitize_columns=False)
    return fc_check


def check_fixed_center(fc_center, center_plot_id_field, fc_fixed, fixed_plot_id_field, in_gdb):
    """Checks fixed plot IDs against the ID of the nearest plot center. If the nearest plot center has the same ID as
    the fixed plot ID, the fixed plot is considered to have the correct ID. If the nearest plot center has a different
    ID than the fixed plot, the fixed plot will be flagged and the ID should be checked manually.
    The function returns the string path to the fixed dataset after adding flag fields.

        Keyword Arguments:
        fc_center            --  Path to the feature class containing the full list
                                 of plot IDs, against which the field data will be checked
        center_plot_id_field --  Field name containing Plot IDs
        fc_fixed             --  Path to the fixed plot feature class
        fixed_plot_id_field  --  Field name containing Plot IDs
        in_gdb               --  Path to working geodatabase
        """

    arcpy.AddMessage("\nChecking fixed plots have correct plot ID")

    # output fc
    center_fixed_join = os.path.join(in_gdb, "center_fixed_SPjoin")

    # add unique plot ID fields
    arcpy.management.CalculateField(fc_center, "PLOT_center", '!' + center_plot_id_field + '!', field_type='TEXT')
    arcpy.management.CalculateField(fc_fixed, "PLOT_fixed", '!' + fixed_plot_id_field + '!', field_type='TEXT')

    arcpy.analysis.SpatialJoin(fc_fixed,
                               fc_center,
                               center_fixed_join,
                               match_option="CLOSEST",
                               distance_field_name="METERS_FROM_PLOT_CENTER")

    # create dataframes
    join_df = pd.DataFrame.spatial.from_featureclass(center_fixed_join)
    fixed_df = pd.DataFrame.spatial.from_featureclass(fc_fixed)
    cast_as_int(join_df)
    cast_as_int(fixed_df)

    # populate CORRECT_PLOT_ID field based on plot center ID == fixed plot ID
    join_df["CORRECT_PLOT_ID"] = join_df.apply(lambda x: match(x["PLOT_center"], x["PLOT_fixed"]), axis=1)

    # add DIST_FROM_ACTUAL_M and CORRECT_PLOT_ID fields to fixed_df
    fixed_df = fixed_df.assign(
        METERS_FROM_PLOT_CENTER=fixed_df['OBJECTID'].map(join_df.set_index('OBJECTID')["METERS_FROM_PLOT_CENTER"]))

    fixed_df = fixed_df.assign(
        CORRECT_PLOT_ID=fixed_df['OBJECTID'].map(join_df.set_index('OBJECTID')["CORRECT_PLOT_ID"]))

    # cleanup
    fixed_df = fixed_df.drop(columns=['PLOT_fixed'])
    arcpy.management.DeleteField(fc_center, "PLOT_center")
    arcpy.management.DeleteField(fc_fixed, "PLOT_fixed")
    arcpy.management.Delete(center_fixed_join)

    arcpy.AddMessage(f"CORRECT_PLOT_ID and METERS_FROM_PLOT_CENTER populated, check complete")

    # overwrite input FC
    fixed_df.spatial.to_featureclass(fc_fixed, sanitize_columns=False)
    return fc_fixed


def check_prism_fixed(fc_prism, prism_plot_id, fc_fixed, fixed_plot_id, in_gdb, plot_id_string):
    """Checks to make sure there is a prism plot for every fixed plot and that there is a
    fixed plot for each prism plot. This is accomplished by comparing unique sets of plot
    IDs present for each feature class and populating fields indicating if this relationship
    holds true.
    Also checks which fixed plot is closest to each prism plot. If the closest fixed plot
    does not have the same plot ID as the prism plot then the prism plot is flagged for review.

    Keyword Arguments:
    fc_prism        -- Path to prism feature class
    prism_plot_id   -- Prism feature class plot ID field
    fc_fixed        -- Path to fixed plot feature class
    fixed_plot_id   -- Fixed feature class plot ID field
    in_gdb          -- Path to working geodatabase
    """

    arcpy.AddMessage(
        "\nChecking for matched pairs of prism and fixed plots"
    )

    # create dataframes
    prism_df = pd.DataFrame.spatial.from_featureclass(fc_prism)
    fixed_df = pd.DataFrame.spatial.from_featureclass(fc_fixed)
    cast_as_int(prism_df)
    cast_as_int(fixed_df)

    # clear flag field from any previous run
    if 'PRISM_ID_MATCHES' in fixed_df.columns:
        fixed_df = fixed_df.drop(columns=['PRISM_ID_MATCHES'])

    # flag prism plot IDs without corresponding fixed plot
    prism_df["HAS_FIXED"] = prism_df[prism_plot_id].isin(fixed_df[fixed_plot_id])
    yes_no(prism_df, 'HAS_FIXED')
    arcpy.AddMessage(
        f"    Prism plots checked for corresponding fixed plots")

    # flag fixed plot IDs without corresponding prism plot
    fixed_df["HAS_PRISM"] = fixed_df[fixed_plot_id].isin(prism_df[prism_plot_id])
    yes_no(fixed_df, 'HAS_PRISM')
    arcpy.AddMessage(
        f"    Fixed plots checked for corresponding prism plots")

    arcpy.AddMessage(
        "    Checking spatial relationship between prism and fixed plots")

    # location for spatial join fc
    prism_fixed_join = os.path.join(in_gdb, "prism_fixed_SPjoin")

    # add unique plot ID fields
    arcpy.management.CalculateField(fc_fixed, "PLOT_fixed", '!' + fixed_plot_id + '!', field_type='TEXT')
    arcpy.management.CalculateField(fc_prism, "PLOT_prism", '!' + prism_plot_id + '!', field_type='TEXT')

    arcpy.analysis.SpatialJoin(target_features=fc_prism,
                               join_features=fc_fixed,
                               out_feature_class=prism_fixed_join,
                               join_operation="JOIN_ONE_TO_MANY",
                               match_option="CLOSEST",
                               distance_field_name="METERS_FROM_FIXED_PLOT")

    # create dataframe from spatial join
    join_df = pd.DataFrame.spatial.from_featureclass(prism_fixed_join)

    # populate CORRECT_PLOT_ID field based on plot center ID == fixed plot ID
    join_df["CORRECT_PLOT_ID"] = join_df.apply(lambda x: match(x["PLOT_prism"], x["PLOT_fixed"]), axis=1)

    # add DIST_FROM_ACTUAL_M and CORRECT_PLOT_ID fields to prism_df
    prism_df = prism_df.assign(
        METERS_FROM_FIXED_PLOT=prism_df['OBJECTID'].map(join_df.set_index('TARGET_FID')["METERS_FROM_FIXED_PLOT"]))

    prism_df = prism_df.assign(
        CORRECT_PLOT_ID=prism_df['OBJECTID'].map(join_df.set_index('TARGET_FID')["CORRECT_PLOT_ID"]))

    # if all prism IDs agree with fixed ID, PRISM_ID_MATCHES = Yes, else No
    # group join_df by fixed plot ID, count unique values in CORRECT_PLOT_ID field
    # if count = 2, field included both Yes and No values for given plot ID and should be checked
    prism_accuracy = join_df.groupby('PLOT_fixed')['CORRECT_PLOT_ID'].nunique()

    # rename field before merging with fixed
    prism_accuracy = prism_accuracy.rename("PRISM_ID_MATCHES")

    # change series to dataframe, add index (PLOT) as series and cast as int/str
    prism_count = prism_accuracy.to_frame()
    if plot_id_string.lower() == 'false':
        # cast plot ID as int
        prism_count[fixed_plot_id] = prism_count.index.astype(int)
    else:
        # cast plot ID as str
        prism_count[fixed_plot_id] = prism_count.index.astype(str)

    def unique_val(x):
        if x == 1:
            return "Yes"
        else:
            return "No"

    # merge dataframes on fixed plot ID
    merge_fixed = fixed_df.merge(prism_count, on=fixed_plot_id)
    # convert count to Yes/No
    merge_fixed['PRISM_ID_MATCHES'] = merge_fixed.apply(lambda x: unique_val(x['PRISM_ID_MATCHES']), axis=1)

    arcpy.AddMessage(f"Flag fields populated, completed check of prism and fixed plots")

    # cleanup
    arcpy.management.DeleteField(fc_prism, "PLOT_prism")
    arcpy.management.DeleteField(fc_fixed, "PLOT_fixed")
    arcpy.management.Delete(prism_fixed_join)

    # overwrite input FC
    prism_df.spatial.to_featureclass(fc_prism, sanitize_columns=False)
    merge_fixed.spatial.to_featureclass(fc_fixed, sanitize_columns=False)
    return fc_prism, fc_fixed


def check_contractor_age_plots(fc_center, center_plot_id_field, age_flag_field, fc_age, age_plot_id, plot_id_string):
    """Checks prescribed age plots against collected age plots. Returns the prescribed age
    plots with a flag field indicating if an age plot was collected.

    Keyword Arguments:
    fc_center            --  Path to feature class of required plot locations
    center_plot_id_field --  Field name of Plot ID column for required plot location feature class
    age_flag_field       --  Field name of age requirement flag field for required plot location feature class
    fc_age               --  Path to feature class of contractor submitted age plots
    age_plot_id          --  Field name of Plot ID column for contractor submitted age plot feature class
    """

    # check to ensure Age plots exit where required, adding and populating a flag field on the plot center feature class
    arcpy.AddMessage("\nChecking for presence of all needed age tree records")

    # create dataframes
    center_df = pd.DataFrame.spatial.from_featureclass(fc_center)
    age_df = pd.DataFrame.spatial.from_featureclass(fc_age)
    cast_as_int(center_df)
    cast_as_int(age_df)

    # populate HAS_AGE field for each plot where age_flag_field = A (if not A, HAS_AGE = 'N/A')
    # center_df.loc[center_df[age_flag_field] == 'A', 'HAS_AGE'] = center_df[center_plot_id_field].isin(
    #     age_df[age_plot_id])
    center_df['HAS_AGE'] = center_df[center_plot_id_field].isin(age_df[age_plot_id])
    yes_no(center_df, 'HAS_AGE')

    center_df.loc[center_df[age_flag_field] != 'A', 'HAS_AGE'] = 'N/A'

    # reset plot to int if not flagged as varchar
    if plot_id_string.lower() == 'false':
        # check main plot ID field to ensure it is integer
        center_df["PLOT"] = center_df["PLOT"].astype(int)
    else:
        pass

    arcpy.AddMessage("HAS_AGE populated, check complete")

    # overwrite input FC
    center_df.spatial.to_featureclass(fc_center, sanitize_columns=False)
    return fc_center


def check_required_fields_center(fc_center, plot_name, flag_name):
    """Checks plot centers for presence of required fields and for missing values in those fields.

    Keyword Arguments:
    fc_center -- Path to plot center feature class
    plot_name -- Name of plot field
    flag_name -- Name of plot type flag field
    """
    # check plot center fc has all needed fields
    arcpy.AddMessage("\nChecking plot centers for required fields")

    # list of required fields
    rf_center = [
        "PLOT",
        "TYPE"
    ]

    # create dataframe
    center_df = pd.DataFrame.spatial.from_featureclass(fc_center)
    cast_as_int(center_df)

    # format field names
    center_df = rename_fields(center_df, plot_name, "PLOT")
    center_df = rename_fields(center_df, flag_name, "TYPE")

    # replace blank strings with NaN
    for i in rf_center:
        center_df.loc[center_df[i] == ' ', i] = None
        center_df.loc[center_df[i] == '', i] = None

    # populate MIS_FIELDS with list of fields missing values
    center_df['MIS_FIELDS'] = center_df[["PLOT",
                                         "TYPE"]].apply(
        lambda x: ', '.join(x[x.isnull()].index), axis=1)

    arcpy.AddMessage("    MIS_FIELDS populated")

    # populate HAS_MIS_FIELD
    center_df.loc[center_df['MIS_FIELDS'] != '', 'HAS_MIS_FIELD'] = "Yes"
    center_df.loc[center_df['MIS_FIELDS'] == '', 'HAS_MIS_FIELD'] = "No"

    arcpy.AddMessage("    HAS_MIS_FIELDS populated")
    arcpy.AddMessage("Check complete")

    # overwrite input FC
    center_df.spatial.to_featureclass(fc_center, sanitize_columns=False)
    return fc_center


def check_required_fields_prism(fc_prism, plot_name, species_name, dia_name, class_name, health_name, misc_name,
                                crew_name, date_name):
    """Checks prism plots for presence of required fields and for missing values in those fields.

    Keyword Arguments:
    fc_prism     -- Path to prism feature class
    plot_name    -- Name of plot field
    species_name -- Name of tree species field
    dia_name     -- Name of tree diameter field
    class_name   -- Name of tree class field
    health_name  -- Name of tree health field
    misc_name    -- Name of miscellaneous notes field (not required, but requires a standardized name)
    crew_name    -- Name of crew field
    date_name    -- Name of date field
    """

    arcpy.AddMessage("\nChecking prism plots for required fields")

    # list of required fields
    rf_prism = [
        "PLOT",
        "TR_SP",
        "TR_DIA",
        "TR_CL",
        "TR_HLTH",
        "COL_CREW",
        "COL_DATE"
    ]

    # create dataframe
    prism_df = pd.DataFrame.spatial.from_featureclass(fc_prism)
    cast_as_int(prism_df)

    # format field names
    prism_df = rename_fields(prism_df, plot_name, "PLOT")
    prism_df = rename_fields(prism_df, species_name, "TR_SP")
    prism_df = rename_fields(prism_df, dia_name, "TR_DIA")
    prism_df = rename_fields(prism_df, class_name, "TR_CL")
    prism_df = rename_fields(prism_df, health_name, "TR_HLTH")
    prism_df = rename_fields(prism_df, misc_name, "MISC")
    prism_df = rename_fields(prism_df, crew_name, "COL_CREW")
    prism_df = rename_fields(prism_df, date_name, "COL_DATE")

    # null values allowed only when TR_SP is null (no tree) or "NoTree"
    # check TR_SP against list of accepted values

    # replace blank strings with NaN
    for i in rf_prism:
        prism_df.loc[prism_df[i] == ' ', i] = None
        prism_df.loc[prism_df[i] == '', i] = None

    # populate MIS_FIELDS with list of fields missing values
    # if TR_SP is 'NONE' or 'NoTree', check that TR_CREW and TR_DATE fields are filled out
    prism_df.loc[prism_df.TR_SP.isin(["NONE", "NoTree", "NO TREES"]), 'MIS_FIELDS'] = prism_df[["COL_CREW",
                                                                                                "COL_DATE"]].apply(
        lambda x: ', '.join(x[x.isnull()].index), axis=1)

    arcpy.AddMessage("    MIS_FIELDS populated for no tree records")

    # if TR_SP is not 'NONE' or 'NoTree', or is null, check that all fields are filled out
    prism_df.loc[~prism_df.TR_SP.isin(["NONE", "NoTree", "NO TREES"]), 'MIS_FIELDS'] = prism_df[["TR_SP",
                                                                                                 "TR_DIA",
                                                                                                 "TR_CL",
                                                                                                 "TR_HLTH",
                                                                                                 "COL_CREW",
                                                                                                 "COL_DATE"]].apply(
        lambda x: ', '.join(x[x.isnull()].index), axis=1)

    prism_df.loc[prism_df['TR_SP'].isnull(), 'MIS_FIELDS'] = prism_df[["TR_SP",
                                                                       "TR_DIA",
                                                                       "TR_CL",
                                                                       "TR_HLTH",
                                                                       "COL_CREW",
                                                                       "COL_DATE"]].apply(
        lambda x: ', '.join(x[x.isnull()].index), axis=1)

    arcpy.AddMessage("    MIS_FIELDS populated for tree records")

    # populate HAS_MIS_FIELD
    prism_df.loc[prism_df['MIS_FIELDS'] != '', 'HAS_MIS_FIELD'] = "Yes"
    prism_df.loc[prism_df['MIS_FIELDS'] == '', 'HAS_MIS_FIELD'] = "No"

    arcpy.AddMessage("    HAS_MIS_FIELDS populated for tree records")

    # add mast type field
    # add mast type field
    if 'MAST_TYPE' in prism_df.columns:
        # delete field if already in dataset
        prism_df = prism_df.drop(columns=['MAST_TYPE'])
    elif 'MAST_TYPE_y' in prism_df.columns:
        prism_df = prism_df.drop(columns=['MAST_TYPE_y'])
    elif 'MAST_TYPE_x' in prism_df.columns:
        prism_df = prism_df.drop(columns=['MAST_TYPE_x'])
    else:
        pass

    # crosswalk_df = pd.read_csv('resources/MAST_SP_TYP_Crosswalk.csv') \
    mast_csv = Path(__file__).parent / "../resources/MAST_SP_TYP_Crosswalk.csv"
    crosswalk_df = pd.read_csv(mast_csv) \
        .filter(items=['TR_SP', 'MAST_TYPE'])

    prism_df = prism_df.merge(right=crosswalk_df, how='left', on='TR_SP')

    arcpy.AddMessage("    MAST_TYPE field populated")

    # populate CANOPY_DBH_FLAG
    # flag all trees with dia > 50"
    prism_df.loc[prism_df['TR_DIA'] > 50, 'CANOPY_DBH_FLAG'] = "Tree diameter > 50in"

    # flag trees where dia >18 AND intermediate
    prism_df.loc[(prism_df.TR_DIA > 18) & (prism_df.TR_CL == 'I'),
    'CANOPY_DBH_FLAG'] = "Class = I and diameter > 18in"

    # flag trees where dia <12 AND co-dominant
    prism_df.loc[(prism_df.TR_DIA < 12) & (prism_df.TR_CL == 'CD'),
    'CANOPY_DBH_FLAG'] = "Class = CD and diameter < 12in"

    # flag trees where dia <30 AND dominant
    prism_df.loc[(prism_df.TR_DIA < 30) & (prism_df.TR_CL == 'D'),
    'CANOPY_DBH_FLAG'] = "Class = D and diameter < 30in"

    arcpy.AddMessage("Check complete")

    # overwrite input FC
    prism_df.spatial.to_featureclass(fc_prism,
                                     overwrite=True,
                                     sanitize_columns=False)
    return fc_prism


def check_required_fields_age(fc_age, plot_name, species_name, dia_name, height_name, orig_name, grw_name, misc_name,
                              crew_name,
                              date_name):
    """Checks age plots for presence of required fields and for missing values in those fields.

    Keyword Arguments:
    fc_age       -- Path to age feature class
    plot_name    -- Name of plot field
    species_name -- Name of tree species field
    dia_name     -- Name of tree diameter field
    height_name  -- Name of tree height field
    orig_name    -- Name of tree origin date field
    grw_name     -- Name of tree growth field
    misc_name    -- Name of miscellaneous notes field (not required, but requires a standardized name)
    crew_name    -- Name of crew field
    date_name    -- Name of date field
    """

    arcpy.AddMessage("\nChecking age plots for required fields")

    # list of required fields
    rf_age = [
        "PLOT",
        "AGE_SP",
        "AGE_DIA",
        "AGE_HT",
        "AGE_ORIG",
        "AGE_GRW",
        "COL_CREW",
        "COL_DATE"
    ]

    # create dataframe
    age_df = pd.DataFrame.spatial.from_featureclass(fc_age)
    cast_as_int(age_df)

    # format field names
    age_df = rename_fields(age_df, plot_name, "PLOT")
    age_df = rename_fields(age_df, species_name, "AGE_SP")
    age_df = rename_fields(age_df, dia_name, "AGE_DIA")
    age_df = rename_fields(age_df, height_name, "AGE_HT")
    age_df = rename_fields(age_df, orig_name, "AGE_ORIG")
    age_df = rename_fields(age_df, grw_name, "AGE_GRW")
    age_df = rename_fields(age_df, misc_name, "MISC")
    age_df = rename_fields(age_df, crew_name, "COL_CREW")
    age_df = rename_fields(age_df, date_name, "COL_DATE")

    # replace blank strings with NaN
    for i in rf_age:
        age_df.loc[age_df[i] == ' ', i] = None
        age_df.loc[age_df[i] == '', i] = None

    # replace 0 in AGE_ORIG field with None
    age_df.loc[age_df['AGE_ORIG'] == 0, 'AGE_ORIG'] = None

    # populate MIS_FIELDS with list of fields missing values
    age_df['MIS_FIELDS'] = age_df[["AGE_SP",
                                   "AGE_DIA",
                                   "AGE_HT",
                                   "AGE_ORIG",
                                   "AGE_GRW",
                                   "COL_CREW",
                                   "COL_DATE"]].apply(
        lambda x: ', '.join(x[x.isnull()].index), axis=1)

    arcpy.AddMessage("    MIS_FIELDS populated")

    # populate HAS_MIS_FIELD
    age_df.loc[age_df['MIS_FIELDS'] != '', 'HAS_MIS_FIELD'] = "Yes"
    age_df.loc[age_df['MIS_FIELDS'] == '', 'HAS_MIS_FIELD'] = "No"

    arcpy.AddMessage("    HAS_MIS_FIELDS populated")

    # revert NA values to 0

    # check for valid years, must have full 4 digits
    age_df.loc[age_df['AGE_ORIG'] > 1900, 'VALID_AGE'] = "Yes"
    age_df.loc[age_df['AGE_ORIG'] <= 1900, 'VALID_AGE'] = "No"
    age_df.loc[age_df['AGE_ORIG'].isnull(), 'VALID_AGE'] = "No"

    arcpy.AddMessage("    VALID_AGE populated")

    # add mast type field
    if 'MAST_TYPE' in age_df.columns:
        # delete field if already in dataset
        prism_df = age_df.drop(columns=['MAST_TYPE'])
    elif 'MAST_TYPE_y' in age_df.columns:
        prism_df = age_df.drop(columns=['MAST_TYPE_y'])
    elif 'MAST_TYPE_x' in age_df.columns:
        prism_df = age_df.drop(columns=['MAST_TYPE_x'])
    else:
        pass

    mast_csv = Path(__file__).parent / "../resources/MAST_SP_TYP_Crosswalk.csv"
    crosswalk_df = pd.read_csv(mast_csv) \
        .filter(items=['TR_SP', 'MAST_TYPE']) \
        .rename(columns={'TR_SP': 'AGE_SP'})

    age_df = age_df.merge(right=crosswalk_df, how='left', on='AGE_SP')

    arcpy.AddMessage("    MAST_TYPE field populated")

    # recast numerical fields to correct type
    age_df["AGE_DIA"] = age_df["AGE_DIA"].round(1)

    arcpy.AddMessage("Check complete")

    # overwrite input FC
    age_df.spatial.to_featureclass(fc_age,
                                   overwrite=True,
                                   sanitize_columns=False)

    return fc_age


def check_required_fields_fixed(fc_fixed, plot_name, closure_name, height_name, un_ht_name, un_cover_name, un_sp_name,
                                gr_sp_name, misc_name, crew_name, date_name):
    """Checks fixed plots for presence of required fields and for missing values in those fields.

    Keyword Arguments:
    fc_fixed      -- Path to fixed feature class
    plot_name     -- Name of plot field
    closure_name  -- Name of overstory closure field
    height_name   -- Name of overstory height field
    un_ht_name    -- Name of understory height field
    un_cover_name -- Name of understory cover field
    un_sp_name    -- Name of understory species field
    gr_sp_name    -- Name of ground species field
    misc_name     -- Name of miscellaneous notes field (not required, but requires a standardized name)
    crew_name     -- Name of crew field
    date_name     -- Name of date field
    """

    arcpy.AddMessage("\nChecking fixed plots for required fields")

    # list of required fields
    rf_fixed = [
        "PLOT",
        "OV_CLSR",
        "OV_HT",
        "UND_HT",
        "UND_COV",
        "UND_SP1",
        "GRD_SP1",
        "COL_CREW",
        "COL_DATE"
    ]

    # create dataframe
    fixed_df = pd.DataFrame.spatial.from_featureclass(fc_fixed)
    cast_as_int(fixed_df)

    # format field names
    fixed_df = rename_fields(fixed_df, plot_name, "PLOT")
    fixed_df = rename_fields(fixed_df, closure_name, "OV_CLSR")
    fixed_df = rename_fields(fixed_df, height_name, "OV_HT")
    fixed_df = rename_fields(fixed_df, un_ht_name, "UND_HT")
    fixed_df = rename_fields(fixed_df, un_cover_name, "UND_COV")
    fixed_df = rename_fields(fixed_df, un_sp_name, "UND_SP1")
    fixed_df = rename_fields(fixed_df, gr_sp_name, "GRD_SP1")
    fixed_df = rename_fields(fixed_df, misc_name, "MISC")
    fixed_df = rename_fields(fixed_df, crew_name, "COL_CREW")
    fixed_df = rename_fields(fixed_df, date_name, "COL_DATE")

    # replace blank strings with NaN
    for i in rf_fixed:
        fixed_df.loc[fixed_df[i] == ' ', i] = None
        fixed_df.loc[fixed_df[i] == '', i] = None

    # if UND_SP1 = NONE, UND_HT = 0
    if is_string_dtype(fixed_df.UND_HT):
        fixed_df.loc[fixed_df.UND_SP1.isin([" ", ""]), 'UND_HT'] = '0'
        fixed_df.loc[fixed_df.UND_SP1.str.contains('none', flags=re.IGNORECASE, regex=True), 'UND_HT'] = '0'
        fixed_df.loc[fixed_df['UND_SP1'].isnull(), 'UND_HT'] = '0'
    elif is_numeric_dtype(fixed_df.UND_HT):
        fixed_df.loc[fixed_df.UND_SP1.isin([" ", ""]), 'UND_HT'] = 0
        fixed_df.loc[fixed_df.UND_SP1.str.contains('none', flags=re.IGNORECASE, regex=True), 'UND_HT'] = 0
        fixed_df.loc[fixed_df['UND_SP1'].isnull(), 'UND_HT'] = 0
    else:
        pass

    # if UND_SP1 not null or NONE (i.e. contains species code) and UND_HT = 0, set UND_HT to null
    fixed_df.loc[(~fixed_df.UND_SP1.isin(["NONE", "NONE ", "None", " ", ""])) & (fixed_df.UND_HT == 0), 'UND_HT'] = None

    # populate MIS_FIELDS with list of fields missing values
    fixed_df['MIS_FIELDS'] = fixed_df[["OV_CLSR",
                                       "OV_HT",
                                       "UND_HT",
                                       "UND_COV",
                                       "UND_SP1",
                                       "GRD_SP1",
                                       "COL_CREW",
                                       "COL_DATE"]].apply(
        lambda x: ', '.join(x[x.isnull()].index), axis=1)

    arcpy.AddMessage("    MIS_FIELDS populated")

    # populate HAS_MIS_FIELD
    fixed_df.loc[fixed_df['MIS_FIELDS'] != '', 'HAS_MIS_FIELD'] = "Yes"
    fixed_df.loc[fixed_df['MIS_FIELDS'] == '', 'HAS_MIS_FIELD'] = "No"

    arcpy.AddMessage("    HAS_MIS_FIELDS populated")

    # add UND_HT2 field with average height (float) of understory, converted from the range in UND_HT
    heights = {'0': 0,
               '<2': 1,
               '2-5': 3.5,
               '5-10': 7.5,
               '10-15': 12.5,
               '15-20': 17.5,
               '20-25': 22.5,
               '25-30': 27.5,
               '30-35': 32.5,
               '35-40': 37.5,
               '40-45': 42.5,
               '45-50': 47.5,
               '>50': 52.5,
               "0'": 0,
               "<2'": 1,
               "2'-5'": 3.5,
               "5'-10'": 7.5,
               "10'-15'": 12.5,
               "15'-20'": 17.5,
               "20'-25'": 22.5,
               "25'-30'": 27.5,
               "30'-35'": 32.5,
               "35'-40'": 37.5,
               "40'-45'": 42.5,
               "45'-50'": 47.5,
               ">50'": 52.5,
               "NONE": 0,
               "None": 0,
               "None ": 0,
               "": 0,
               " ": 0
               }

    # return average of height range
    if is_string_dtype(fixed_df.UND_HT):
        # if UND_HT is string, use get_value function to convert string range to number using the heights dictionary
        fixed_df['UND_HT2'] = fixed_df.apply(
            lambda x: get_value(heights, x['UND_HT']) if (pd.notnull(x['UND_HT'])) else None, axis=1)
    elif is_numeric_dtype(fixed_df.UND_HT):
        # if UND_HT is numeric (int/float), copy value to UND_HT2
        fixed_df['UND_HT2'] = fixed_df['UND_HT']
    else:
        pass

    # fixed_df.loc[fixed_df['UND_HT'].notna(), 'UND_HT2'] = fixed_df.apply(lambda x: get_value(heights, x['UND_HT']),
    #                                                                      axis=1)
    # fixed_df['UND_HT2'] = fixed_df[fixed_df['UND_HT'].notna()].apply(lambda x: get_value(heights, x['UND_HT']),
    #                                                                  axis=1)
    # fixed_df['UND_HT2'] = fixed_df.loc[~fixed_df.MIS_FIELDS.isin(["UND_HT"])].apply(lambda x: get_value(heights, x['UND_HT']), axis=1)
    # fixed_df['UND_HT2'] = fixed_df.apply(lambda x: get_value(heights, x['UND_HT']), axis=1)

    # fixed_df['UND_HT2'] = fixed_df.apply(lambda x: get_value(heights, x['UND_HT']) if (pd.notnull(x['UND_HT'])) else 0, axis=1)

    arcpy.AddMessage("Check complete")

    # overwrite input FC
    fixed_df.spatial.to_featureclass(fc_fixed,
                                     overwrite=True,
                                     sanitize_columns=False)

    return fc_fixed


def remove_duplicates(fc_prism, fc_fixed, fc_age, fc_center):
    """Checks prism, fixed, and age plots for duplicate geometry. Fixed plots are also checked for duplicate plot IDs.

    Keyword Arguments:
    fc_prism  -- Path to prism feature class
    fc_fixed  -- Path to fixed feature class
    fc_age    -- Path to age feature class
    """

    arcpy.AddMessage("\nChecking for and flagging duplicates")

    # create dataframes
    center_df = pd.DataFrame.spatial.from_featureclass(fc_center)
    prism_df = pd.DataFrame.spatial.from_featureclass(fc_prism)
    fixed_df = pd.DataFrame.spatial.from_featureclass(fc_fixed)
    age_df = pd.DataFrame.spatial.from_featureclass(fc_age)
    cast_as_int(prism_df)
    cast_as_int(fixed_df)
    cast_as_int(age_df)

    # generate dataframes of duplicate rows
    # if checking for duplicate shape fields, cannot include other fields
    center_duplicates = center_df[center_df.duplicated(["SHAPE"])]
    prism_duplicates = prism_df[prism_df.duplicated(['PLOT', 'TR_SP', 'TR_DIA', 'TR_CL', 'TR_HLTH'])]
    fixed_duplicates = fixed_df[fixed_df.duplicated(["SHAPE"])]
    age_duplicates = age_df[age_df.duplicated(["SHAPE"])]

    # add boolean DUPLICATE field
    center_df["DUPLICATE"] = center_df['OBJECTID'].isin(center_duplicates['OBJECTID'])
    prism_df["DUPLICATE"] = prism_df['OBJECTID'].isin(prism_duplicates['OBJECTID'])
    fixed_df["DUPLICATE"] = fixed_df['OBJECTID'].isin(fixed_duplicates['OBJECTID'])
    age_df["DUPLICATE"] = age_df['OBJECTID'].isin(age_duplicates['OBJECTID'])

    yes_no(center_df, "DUPLICATE")
    yes_no(prism_df, "DUPLICATE")
    yes_no(fixed_df, "DUPLICATE")
    yes_no(age_df, "DUPLICATE")

    # subset rows where DUPLICATE is false and drop field
    # *** skip this for now, Tate wants to just flag duplicates
    # FieldMaps has the ability to snap to existing geometry
    # prism_df = prism_df[(~prism_df.DUPLICATE)].drop(columns=['DUPLICATE'])
    # fixed_df = fixed_df[(~fixed_df.DUPLICATE)].drop(columns=['DUPLICATE'])
    # age_df = age_df[(~age_df.DUPLICATE)].drop(columns=['DUPLICATE'])

    # overwrite input FCs
    center_df.spatial.to_featureclass(fc_center,
                                      overwrite=True,
                                      sanitize_columns=False)
    prism_df.spatial.to_featureclass(fc_prism,
                                     overwrite=True,
                                     sanitize_columns=False)
    fixed_df.spatial.to_featureclass(fc_fixed,
                                     overwrite=True,
                                     sanitize_columns=False)
    age_df.spatial.to_featureclass(fc_age,
                                   overwrite=True,
                                   sanitize_columns=False)

    arcpy.AddMessage("Check complete"
                     f"\nFlagged {len(center_duplicates.index)} duplicate plot centers"
                     f"\nFlagged {len(prism_duplicates.index)} duplicates from prism plots"
                     f"\nFlagged {len(fixed_duplicates.index)} duplicates from fixed plots"
                     f"\nFlagged {len(age_duplicates.index)} duplicates from age plots")

    return fc_prism, fc_fixed, fc_age, fc_center


def import_hierarchy(fc_polygons, fc_center, fc_prism, fc_fixed, fc_age, pool, comp, unit, site, stand):
    """Adds FMG hierarchy levels to plot center fc through spatial join. Adds hierarchy levels to prism, fixed, and
    age fc through tabular join on plot ID.

    Keyword Arguments:
    fc_polygons     -- Path to FMG polygon feature class
    fc_center       -- Path to plot center feature class
    fc_prism        -- Path to prism feature class
    fc_fixed        -- Path to fixed plot feature class
    fc_age          -- Path to fixed plot feature class
    pool            -- FMG polygon pool ID field
    comp            -- FMG polygon comp ID field
    unit            -- FMG polygon unit ID field
    site            -- FMG polygon site ID field
    stand           -- FMG polygon stand ID field
    """

    # create dataframes
    center_df = pd.DataFrame.spatial.from_featureclass(fc_center)
    prism_df = pd.DataFrame.spatial.from_featureclass(fc_prism)
    fixed_df = pd.DataFrame.spatial.from_featureclass(fc_fixed)
    age_df = pd.DataFrame.spatial.from_featureclass(fc_age)
    cast_as_int(center_df)
    cast_as_int(prism_df)
    cast_as_int(fixed_df)
    cast_as_int(age_df)

    # remove hierarchy fields from any previous tool run
    levels = [pool, comp, unit, site, stand, 'PID', 'COMP', 'VALID_SID']
    for l in levels:
        if l in center_df.columns:
            center_df = center_df.drop(columns=[l])
        if l in prism_df.columns:
            prism_df = prism_df.drop(columns=[l])
        if l in fixed_df.columns:
            fixed_df = fixed_df.drop(columns=[l])
        if l in age_df.columns:
            age_df = age_df.drop(columns=[l])

    arcpy.management.DeleteField(fc_center, levels)

    arcpy.AddMessage(
        "\nChecking spatial relationship between plots and FMG polygons")

    # location for spatial join fc
    in_gdb = arcpy.Describe(fc_center).path
    plots_spatial_join = os.path.join(in_gdb, "plots_spatial_join")

    arcpy.analysis.SpatialJoin(target_features=fc_center,
                               join_features=fc_polygons,
                               out_feature_class=plots_spatial_join,
                               join_operation="JOIN_ONE_TO_ONE",
                               match_option="INTERSECT")

    with arcpy.da.UpdateCursor(plots_spatial_join, "SID") as cursor:
        for row in cursor:
            if row[0] is None:
                row[0] = ''
            cursor.updateRow(row)

    # create dataframe from spatial join
    join_df = pd.DataFrame.spatial.from_featureclass(plots_spatial_join)
    cast_as_int(join_df)

    arcpy.AddMessage(
        "Adding fields")

    # pad PLOT ID with leading zeroes if less than 4 numbers
    center_df['PLOT_PAD'] = center_df['PLOT'].astype(str)
    center_df['PLOT_PAD'] = center_df['PLOT_PAD'].str.zfill(4)

    # add fields
    center_merge_df = center_df.merge(join_df[['PLOT', pool, comp, unit, site, stand]], on='PLOT', how='left') \
        .rename(columns={pool: 'POOL', comp: 'COMP', unit: 'UNIT', site: 'SITE', stand: 'SID'})

    # add padded plot ID to stand ID
    center_merge_df['PID'] = center_merge_df['SID'] + "p" + center_merge_df['PLOT_PAD']

    # populate flag field - an empty SID means the plot is outside the FMG polygons
    center_merge_df.loc[center_merge_df['SID'] != '', 'VALID_SID'] = "Yes"
    center_merge_df.loc[center_merge_df['SID'] == '', 'VALID_SID'] = "No"

    # populate flag field - a PID < 14 is likely missing one or more hierarchies
    center_merge_df.loc[center_merge_df['PID'].str.len() >= 14, 'FULL_PID'] = "Yes"
    center_merge_df.loc[center_merge_df['PID'].str.len() < 14, 'FULL_PID'] = "No"

    # add hierarchy fields to prism, fixed, and age
    prism_merge_df = prism_df \
        .merge(center_merge_df[['PLOT', 'POOL', 'COMP', 'UNIT', 'SITE', 'SID', 'PID', 'VALID_SID']],
               on='PLOT', how='left')
    fixed_merge_df = fixed_df \
        .merge(center_merge_df[['PLOT', 'POOL', 'COMP', 'UNIT', 'SITE', 'SID', 'PID', 'VALID_SID']],
               on='PLOT', how='left')
    age_merge_df = age_df \
        .merge(center_merge_df[['PLOT', 'POOL', 'COMP', 'UNIT', 'SITE', 'SID', 'PID', 'VALID_SID']],
               on='PLOT', how='left')

    # cleanup
    center_merge_df = center_merge_df.drop(columns=['PLOT_PAD'])
    arcpy.Delete_management(plots_spatial_join)

    arcpy.AddMessage(
        "Saving output")

    # overwrite input FC
    center_merge_df.spatial.to_featureclass(fc_center, overwrite=True, sanitize_columns=False)
    prism_merge_df.spatial.to_featureclass(fc_prism, overwrite=True, sanitize_columns=False)
    fixed_merge_df.spatial.to_featureclass(fc_fixed, overwrite=True, sanitize_columns=False)
    age_merge_df.spatial.to_featureclass(fc_age, overwrite=True, sanitize_columns=False)

    return fc_polygons, center_merge_df, prism_merge_df, fixed_merge_df, age_merge_df
