# -*- coding: UTF-8 -*-
# FMG QA Tools Function Library

import os
import sys
import arcpy
import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor

arcpy.env.overwriteOutput = True


def yes_no(df_name, field_name):
    df_name.loc[df_name[field_name] == 1, field_name] = "Yes"
    df_name.loc[df_name[field_name] == 0, field_name] = "No"


def match(col_a, col_b):
    if col_a == col_b:
        return "Yes"
    else:
        return "No"


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


def check_plot_ids(fc_center, center_plot_id_field, fc_check, check_plot_id_field):
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
        f"Checking Plot ID fields for {fc_center}"
    )

    # create dataframes
    center_df = pd.DataFrame.spatial.from_featureclass(fc_center)
    check_df = pd.DataFrame.spatial.from_featureclass(fc_check)

    # check main plot ID field to ensure it is integer
    if center_df[center_plot_id_field].dtype == 'int64':
        arcpy.AddMessage(f"    {os.path.basename(fc_center)} plot ID field type is correct")
    else:
        try:
            center_df[center_plot_id_field] = center_df[center_plot_id_field].astype(int)
            arcpy.AddMessage(
                f"{os.path.basename(fc_center)} plot ID field type converted to integer.")
        except:
            arcpy.AddError(f"{os.path.basename(fc_center)} plot ID field type must be short or long integer, quitting.")
            sys.exit(0)

    # check input plot ID field to ensure it is integer
    if check_df[check_plot_id_field].dtype == 'int64':
        arcpy.AddMessage(f"    {os.path.basename(fc_check)} plot ID field type is correct")
    else:
        try:
            check_df[check_plot_id_field] = check_df[check_plot_id_field].astype(int)
            arcpy.AddMessage(
                f"{os.path.basename(fc_check)} plot ID field type converted to integer.")
        except:
            arcpy.AddError(f"{os.path.basename(fc_check)} plot ID field type must be short or long integer, quitting.")
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

    arcpy.AddMessage("Checking spatial relationship between plot center and fixed plots")

    # output fc
    center_fixed_join = os.path.join(in_gdb, "center_fixed_SPjoin")

    # add unique plot ID fields
    arcpy.management.CalculateField(fc_center, "PLOT_center", '!' + center_plot_id_field + '!', field_type='TEXT')
    arcpy.management.CalculateField(fc_fixed, "PLOT_fixed", '!' + fixed_plot_id_field + '!', field_type='TEXT')

    arcpy.analysis.SpatialJoin(fc_fixed,
                               fc_center,
                               center_fixed_join,
                               match_option="CLOSEST",
                               distance_field_name="DIST_FROM_CENTER_M")

    # create dataframes
    join_df = pd.DataFrame.spatial.from_featureclass(center_fixed_join)
    fixed_df = pd.DataFrame.spatial.from_featureclass(fc_fixed)

    # populate CORRECT_PLOT_ID field based on plot center ID == fixed plot ID
    join_df["CORRECT_PLOT_ID"] = join_df.apply(lambda x: match(x["PLOT_center"], x["PLOT_fixed"]), axis=1)

    # add DIST_FROM_ACTUAL_M and CORRECT_PLOT_ID fields to fixed_df
    fixed_df = fixed_df.assign(
        DIST_FROM_CENTER_M=fixed_df['OBJECTID'].map(join_df.set_index('OBJECTID')["DIST_FROM_CENTER_M"]))

    fixed_df = fixed_df.assign(
        CORRECT_PLOT_ID=fixed_df['OBJECTID'].map(join_df.set_index('OBJECTID')["CORRECT_PLOT_ID"]))

    # cleanup
    fixed_df = fixed_df.drop(columns=['PLOT_fixed'])
    arcpy.management.DeleteField(fc_center, "PLOT_center")
    arcpy.management.DeleteField(fc_fixed, "PLOT_fixed")
    arcpy.management.Delete(center_fixed_join)

    arcpy.AddMessage(f"\nFlag fields populated, check of {os.path.basename(fc_center)} "
                     f"and {os.path.basename(fc_fixed)} complete")

    # overwrite input FC
    fixed_df.spatial.to_featureclass(fc_fixed, sanitize_columns=False)
    return fc_fixed


def check_prism_fixed(fc_prism, prism_plot_id, fc_fixed, fixed_plot_id, in_gdb):
    """ Checks to make sure there is a prism plot for every fixed plot and that there is a
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
        "Checking for existence of corresponding prism and fixed plots"
    )

    # create dataframes
    prism_df = pd.DataFrame.spatial.from_featureclass(fc_prism)
    fixed_df = pd.DataFrame.spatial.from_featureclass(fc_fixed)

    # clear flag field from any previous run
    if 'PRISM_ID_MATCHES' in fixed_df.columns:
        fixed_df = fixed_df.drop(columns=['PRISM_ID_MATCHES'])

    # flag prism plot IDs without corresponding fixed plot
    prism_df["HAS_FIXED"] = prism_df[prism_plot_id].isin(fixed_df[fixed_plot_id])
    yes_no(prism_df, 'HAS_FIXED')
    arcpy.AddMessage(
        f"    Prism plots {fc_prism} checked for corresponding fixed plots")

    # flag fixed plot IDs without corresponding prism plot
    fixed_df["HAS_PRISM"] = fixed_df[fixed_plot_id].isin(prism_df[prism_plot_id])
    yes_no(fixed_df, 'HAS_PRISM')
    arcpy.AddMessage(
        f"    Fixed plots {fc_fixed} checked for corresponding prism plots")

    arcpy.AddMessage(
        "Checking spatial relationship between prism and fixed plots")

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
                               distance_field_name="DIST_FROM_FIXED_M")

    # create dataframe from spatial join
    join_df = pd.DataFrame.spatial.from_featureclass(prism_fixed_join)

    # populate CORRECT_PLOT_ID field based on plot center ID == fixed plot ID
    join_df["CORRECT_PLOT_ID"] = join_df.apply(lambda x: match(x["PLOT_prism"], x["PLOT_fixed"]), axis=1)

    # add DIST_FROM_ACTUAL_M and CORRECT_PLOT_ID fields to prism_df
    prism_df = prism_df.assign(
        DIST_FROM_FIXED_M=prism_df['OBJECTID'].map(join_df.set_index('TARGET_FID')["DIST_FROM_FIXED_M"]))

    prism_df = prism_df.assign(
        CORRECT_PLOT_ID=prism_df['OBJECTID'].map(join_df.set_index('TARGET_FID')["CORRECT_PLOT_ID"]))

    # if all prism IDs agree with fixed ID, PRISM_ID_MATCHES = Yes, else No
    # group join_df by fixed plot ID, count unique values in CORRECT_PLOT_ID field
    # if count = 2, field included both Yes and No values for given plot ID and should be checked
    prism_accuracy = join_df.groupby('PLOT_fixed')['CORRECT_PLOT_ID'].nunique()

    # rename field before merging with fixed
    prism_accuracy = prism_accuracy.rename("PRISM_ID_MATCHES")

    # change series to dataframe, add index (PLOT) as series and cast as int
    prism_count = prism_accuracy.to_frame()
    prism_count[fixed_plot_id] = prism_count.index.astype(int)

    def unique_val(x):
        if x == 1:
            return "Yes"
        else:
            return "No"

    # merge dataframes on fixed plot ID
    merge_fixed = fixed_df.merge(prism_count, on=fixed_plot_id)
    # convert count to Yes/No
    merge_fixed['PRISM_ID_MATCHES'] = merge_fixed.apply(lambda x: unique_val(x['PRISM_ID_MATCHES']), axis=1)

    arcpy.AddMessage(f"\nFlag fields populated, completed check of {os.path.basename(fc_prism)} "
                     f"and {os.path.basename(fc_fixed)}")

    # cleanup
    arcpy.management.DeleteField(fc_prism, "PLOT_prism")
    arcpy.management.DeleteField(fc_fixed, "PLOT_fixed")
    arcpy.management.Delete(prism_fixed_join)

    # overwrite input FC
    prism_df.spatial.to_featureclass(fc_prism, sanitize_columns=False)
    merge_fixed.spatial.to_featureclass(fc_fixed, sanitize_columns=False)
    return fc_prism, fc_fixed


def check_contractor_age_plots(fc_center, center_plot_id_field, age_flag_field, fc_age, age_plot_id):
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
    arcpy.AddMessage("Checking plots for corresponding age record")

    # create dataframes
    center_df = pd.DataFrame.spatial.from_featureclass(fc_center)
    age_df = pd.DataFrame.spatial.from_featureclass(fc_age)

    # populate HAS_AGE field for each plot where age_flag_field = A (if not A, HAS_AGE = 'N/A')
    center_df.loc[center_df[age_flag_field] == 'A', 'HAS_AGE'] = center_df[center_plot_id_field].isin(
        age_df[age_plot_id])
    yes_no(center_df, 'HAS_AGE')

    center_df.loc[center_df[age_flag_field] != 'A', 'HAS_AGE'] = 'N/A'

    # reset plot to int
    center_df["PLOT"] = center_df["PLOT"].astype(int)

    arcpy.AddMessage("\nCheck complete")

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
    arcpy.AddMessage("Begin check of plot center points")

    # list of required fields
    rf_center = [
        "PLOT",
        "TYPE"
    ]

    # create dataframe
    center_df = pd.DataFrame.spatial.from_featureclass(fc_center)

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
    arcpy.AddMessage("\nCheck complete")

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

    arcpy.AddMessage("Begin check of prism plots")

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
    prism_df.loc[prism_df.TR_SP.isin(["NONE", "NoTree"]), 'MIS_FIELDS'] = prism_df[["COL_CREW",
                                                                                    "COL_DATE"]].apply(
        lambda x: ', '.join(x[x.isnull()].index), axis=1)

    arcpy.AddMessage("    MIS_FIELDS populated for no tree records")

    # if TR_SP is not 'NONE' or 'NoTree', or is null, check that all fields are filled out
    prism_df.loc[~prism_df.TR_SP.isin(["NONE", "NoTree"]), 'MIS_FIELDS'] = prism_df[["TR_SP",
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

    arcpy.AddMessage("    MIS_FIELDS populated for treed records")

    # populate HAS_MIS_FIELD
    prism_df.loc[prism_df['MIS_FIELDS'] != '', 'HAS_MIS_FIELD'] = "Yes"
    prism_df.loc[prism_df['MIS_FIELDS'] == '', 'HAS_MIS_FIELD'] = "No"

    arcpy.AddMessage("    HAS_MIS_FIELDS populated for treed records")

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

    arcpy.AddMessage("\nCheck complete")

    # overwrite input FC
    prism_df.spatial.to_featureclass(fc_prism,
                                     overwrite=True,
                                     sanitize_columns=False)
    return fc_prism


def check_required_fields_age(fc_age, plot_name, species_name, dia_name, height_name, orig_name, grw_name, misc_name, crew_name,
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

    arcpy.AddMessage("Begin check of age plots")

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
    age_df.loc[age_df['AGE_ORIG'] > 1499, 'VALID_AGE'] = "Yes"
    age_df.loc[age_df['AGE_ORIG'] <= 1499, 'VALID_AGE'] = "No"
    age_df.loc[age_df['AGE_ORIG'].isnull(), 'VALID_AGE'] = "No"

    arcpy.AddMessage("    VALID_AGE populated")

    # recast numerical fields to correct type
    age_df["AGE_DIA"] = age_df["AGE_DIA"].round(1)

    arcpy.AddMessage("\nCheck complete")

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

    arcpy.AddMessage("Begin check of fixed plots")

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
    arcpy.AddMessage("\nCheck complete")

    # overwrite input FC
    fixed_df.spatial.to_featureclass(fc_fixed,
                                     overwrite=True,
                                     sanitize_columns=False)

    return fc_fixed


def remove_duplicates(fc_prism, fc_fixed, fixed_plot_id, fc_age):
    """Checks prism, fixed, and age plots for duplicate geometry. Fixed plots are also checked for duplicate plot IDs.

    Keyword Arguments:
    fc_prism  -- Path to prism feature class
    fc_fixed  -- Path to fixed feature class
    fc_age    -- Path to age feature class
    """

    arcpy.AddMessage("Checking for and removing duplicates")

    # create dataframes
    prism_df = pd.DataFrame.spatial.from_featureclass(fc_prism)
    fixed_df = pd.DataFrame.spatial.from_featureclass(fc_fixed)
    age_df = pd.DataFrame.spatial.from_featureclass(fc_age)

    # generate dataframes of duplicate rows
    prism_duplicates = prism_df[prism_df.duplicated(["SHAPE"])]
    fixed_duplicates = fixed_df[fixed_df.duplicated([fixed_plot_id, "SHAPE"])]
    age_duplicates = age_df[age_df.duplicated(["SHAPE"])]

    # add boolean DUPLICATE field
    prism_df["DUPLICATE"] = prism_df['OBJECTID'].isin(prism_duplicates['OBJECTID'])
    fixed_df["DUPLICATE"] = fixed_df['OBJECTID'].isin(fixed_duplicates['OBJECTID'])
    age_df["DUPLICATE"] = age_df['OBJECTID'].isin(age_duplicates['OBJECTID'])

    # subset rows where DUPLICATE is false and drop field
    prism_df = prism_df[(~prism_df.DUPLICATE)].drop(columns=['DUPLICATE'])
    fixed_df = fixed_df[(~fixed_df.DUPLICATE)].drop(columns=['DUPLICATE'])
    age_df = age_df[(~age_df.DUPLICATE)].drop(columns=['DUPLICATE'])

    # overwrite input FCs
    prism_df.spatial.to_featureclass(fc_prism,
                                     overwrite=True,
                                     sanitize_columns=False)
    fixed_df.spatial.to_featureclass(fc_fixed,
                                     overwrite=True,
                                     sanitize_columns=False)
    age_df.spatial.to_featureclass(fc_age,
                                   overwrite=True,
                                   sanitize_columns=False)

    arcpy.AddMessage("\nCheck complete"
                     f"\nRemoved {len(prism_duplicates.index)} duplicates from prism plots"
                     f"\nRemoved {len(fixed_duplicates.index)} duplicates from fixed plots"
                     f"\nRemoved {len(age_duplicates.index)} duplicates from age plots")

    return fc_prism, fc_fixed, fc_age
