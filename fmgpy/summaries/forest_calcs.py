# FMG QA Tools Function Library

import os
import sys
import arcpy
import math
import pandas as pd
import numpy as np
from arcgis.features import GeoAccessor, GeoSeriesAccessor

arcpy.env.overwriteOutput = True


def fmg_level(level):
    """Get the FMG level field

    :param: level   str; The FMG hierarchical level. One of: "unit", "site",
                    "stand", "plot".

    :return: The Field name of the FMG level.
    """
    assert level in ["unit", "site", "stand", "plot"], "supply correct level"

    if level == "unit":
        level_field = "UNIT"
    elif level == "site":
        level_field = "SITE"
    elif level == "stand":
        level_field = "SID"
    elif level == "plot":
        level_field = "PID"

    return level_field


def plot_count(df):
    """Count the number unique plots

    :param: df   DataFrame; An FMG "Age", Fixed", or "Prism" plot dataset.

    :return: An integer count of unique plots.
    """
    plot_num = df.PID.nunique()

    return plot_num


def agg_plot_count(PID):
    """Counts unique plots, including no tree plots.

    Keyword Arguments:
    PID -- Input plot ID column.

    Details: Function returns a single value and is to be used within a
    dataframe to create a plot count column (.groupby, .agg).
    """
    return float(PID.nunique())


def tree_count(df):
    """Count the number of trees

    :param: df   DataFrame; An FMG "Prism" plot dataset.

    :return: An integer count of trees
    """
    # boolean series
    trees = ~df.TR_SP.isin(["NONE", "NoTree", "", " ", None])

    # sum number of True instances
    num_trees = trees.values.sum()
    return num_trees


def agg_tree_count(tr_sp):
    """Counts trees, excluding no tree records.

    Keyword Arguments:
    tr_sp -- Input tree species column.

    Details: Function returns a single value and is to be used within a
    dataframe to create a tree count column (.groupby, .agg).
    """
    trees = []
    for val in tr_sp:
        if val == 'NoTree':
            continue
        elif val == 'NONE':
            continue
        elif val == '':
            continue
        elif val == ' ':
            continue
        elif val is None:
            continue
        else:
            trees.append(val)
    return float(len(trees))


# Trees Per Acre (TPA)
def tpa(df_prism):
    """Calculates trees per acre. Returns one value.

    Keyword Arguments:
    df_prism -- Input prism dataframe

    Details: Trees per acre is a measure of stand density, i.e. the total number of trees in a given area.
    """
    assert isinstance(df_prism, pd.DataFrame), "must be a pandas DataFrame"
    assert df_prism.columns.isin(["TR_DIA"]).any(), "df must contain column TR_DIA"
    assert df_prism.columns.isin(["TR_SP"]).any(), "df must contain column TR_SP"

    baf = 10

    # if filtered dataframe is empty (no plots), return null
    if df_prism.PID.count() == 0:
        density = None
    # if there are no trees, tpa = 0
    elif tree_count(df_prism) == 0:
        density = 0
    else:
        # if there are trees, use density calc
        # replace null TR_DIA with 0 for rows without a tree
        no_nan = df_prism
        no_nan.loc[no_nan.TR_SP.isin(["NONE", "NoTree"]), 'TR_DIA'] = 0

        # expansion factor = BAF / Tree Basal Area [.005454 x DBH^2] / Plots
        expansion_factor = baf / (0.005454 * (no_nan['TR_DIA'] ** 2)) / plot_count(df_prism)

        # replace infinity values with 0 for rows with no tree (diameter of 0)
        rm_inf = expansion_factor.replace([np.inf, -np.inf], 0)

        # TPA = sum of expansion factors
        density = rm_inf.values.sum()

    return density


# Basal Area (BA)
def ba(df_prism):
    """Calculates basal area, returns one value.

    Keyword Arguments:
    df_prism  -- Input prism dataframe

    Details: Basal area is the cross-section area of all the trees in a given acre.
    Total Basal Area per acre calculation from Washington State University Extension:
    (Trees * BAF)/Plots
    For a Basal Area Factor of 10, each "in" tree represents 10 square feet of basal area.
    """
    assert isinstance(df_prism, pd.DataFrame), "must be a pandas DataFrame"
    assert df_prism.columns.isin(["TR_SP"]).any(), "dataframe must contain column TR_SP"
    assert df_prism.columns.isin(["PID"]).any(), "dataframe must contain column TR_SP"

    # if filtered dataframe is empty (no plots), return null
    if df_prism.PID.count() == 0:
        basal_area = None
    else:
        baf = 10
        basal_area = (tree_count(df_prism) * baf) / plot_count(df_prism)

    return basal_area


# Quadratic Mean Diameter at Breast Height (QM DBH)
def qm_dbh(ba, tpa):
    """Calculates quadratic mean at diameter breast height. Returns one value.

    Keyword Arguments:
    ba  -- Basal area
    tpa -- Trees per acre

    Details:
    Quadratic Mean Diameter ( Dq ) is the diameter of the tree of average per tree basal area.
    This becomes convenient in that we often have basal area per acre and trees per acre but
    not the diameters of all the trees.
    """
    #assert isinstance(ba, (float, np.float64)), "basal area must be a float"
    #assert isinstance(tpa, float, np.float64), "tpa must be a float"

    qmdbh = np.sqrt((ba / tpa) / 0.005454154)
    return qmdbh


# Most prevalent ([health, species] by TPA)

# Most prevalent (percent)

# Highest Frequency Species

# Stocking Percent (Total)
def stocking_pct(avg_tpa, qm_dbh):
    """Calculates stocking percentage for all live trees by polygon for specified hierarchy level.
    Returns one float value.

    Keyword Arguments:
    avg_tpa -- Average trees per acre at specified hierarchy
    qm_dbh  -- Quadratic mean DBH at specified hierarchy

    Details:
    Based on DOI:10.1093/njaf/27.4.132, "A Stocking Diagram for Midwestern Eastern Cottonwood-Silver
    Maple-American Sycamore Bottomland Forests"
    """
    assert isinstance(avg_tpa, float), "avg_tpa must be a float"
    assert isinstance(qm_dbh, float), "qm_dbh must be a float"

    percent = avg_tpa * (0.0685724 + 0.0010125 * (0.259 + (0.973 * qm_dbh)) + 0.0023656 + qm_dbh ** 2)

    return percent

# Stocking Percent (Hard Mast)

# Species Richness

# Importance Value

# Forest Community (species list, numeric ID)

# Inventory Date (year, range of years)


# Percent Cover
def cover_pct(fixed, level):
    """Calculate Average Plot Percent Canopy Cover of Overstory

    Calculate the overstory canopy cover percent for the specified FMG
    hierarchical level.

    :param: fixed   DataFrame; An FMG Fixed Plot data frame.
    :param: level   str; The FMG hierarchical level. One of: "unit", "site",
                    "stand", "plot".

    :return: A data frame of percent canopy cover values for the specified
    FMG hierarchical level.
    """
    assert isinstance(fixed, pd.DataFrame), "fixed must be a DataFrame"
    assert isinstance(level, str), "level must be a string"
    assert level in ["unit", "site", "stand", "plot"], "supply correct level"

    # Get the FMG level to summarize by
    level_field = fmg_level(level)

    # Summarize
    level_cover_pct = (fixed
                       .groupby(level_field,
                                as_index=False)["OV_CLSR_NUM"]
                       .agg(["mean"])
                       .rename(columns={"mean": "canopy_per"})
                       .round({"canopy_per": 2}))

    return level_cover_pct


# Assign size class categorical variable column
def size_class_map(tr_dia):
    """Maps a size class categorical variable onto the tree diameter range
     as specified by USACE foresters

     Keyword Args
     tr_dia -- diameter of a given tree

     Details: written to function within the pandas .loc method
     """

    if 1 <= tr_dia <=6:
        return 'Sappling'
    if 6 < tr_dia <= 12:
        return 'Pole'
    if 12 < tr_dia <= 18:
        return 'Saw'
    if 18 < tr_dia <= 24:
        return 'Mature'
    if tr_dia > 24:
        return 'Over Mature'


# Create tree intermediate table
def create_tree_table(prism_df):
    """Creates the tree dataframe for use in downstream forest summaries by:
        Column TR_DIA is set to 0 for no tree rows
        Column TR_SIZE is added and populated with size class based on tree diameter ranges
        Column TR_BA is added and populated with the eq (tree_count * BAF) / plot_count
        Column TR_DENS is added and populated with the eq (0.005454 * (tr_dia ** 2)) / plot_count

    Keyword Args
    prism_df -- the prism plot feature class directly imported as a dataframe

    Details: None
    """

    # Create Tree Data Frame
    tree_table = prism_df.drop \
        (['CREATED_USER', 'CREATED_DATE', 'LAST_EDITED_USER', 'LAST_EDITED_DATE', 'SE_ANNO_CAD_DATA'],
         axis=1,
         errors='ignore')

    # Set TR_DIA to 0 if TR_SP is NoTree or None
    tree_table.loc[tree_table.TR_SP.isin(["NONE", "NoTree"]), 'TR_DIA'] = 0

    # Add a tree size class field (Sap, Pole, Saw, Mature, Over Mature)
    tree_table['TR_SIZE'] = tree_table['TR_DIA'].map(size_class_map)

    # Define constants for BA & Density calcs, assuming 1 tree, 1 plot
    tree_count = 1
    plot_count = 1
    baf = 10
    forester_constant = 0.005454

    # Add and Calculate BA column, then set BA to 0 where no tree
    tree_table['TR_BA'] = (tree_count * baf) / plot_count
    tree_table.loc[tree_table.TR_SP.isin(["NONE", "NoTree"]), 'TR_BA'] = 0

    # Add and calculate density column (TPA)
    tree_table['TR_DENS'] = (forester_constant * (tree_table['TR_DIA'] ** 2)) / plot_count

    return tree_table


# Create plot intermediate table
def create_plot_table(fixed_df, age_df):
    """ Create the plot dataframe for use in downstream summaries by:
            Combining Fixed and Age Plot dataframes

    Keyword Args
    fixed_df -- the fixed plot feature class directly imported as a dataframe
    age_df   -- the age plot feature class directly imported as a dataframe

    Details: None
    """

    # Create and clean fixed plot dataframe
    cleanfixed_df = fixed_df \
        .drop(['CREATED_USER', 'CREATED_DATE', 'LAST_EDITED_USER', 'LAST_EDITED_DATE', 'SE_ANNO_CAD_DATA', 'OBJECTID'],
              axis=1,
              errors='ignore') \
        .rename(columns={'MISC': 'FX_MISC'}) \
        .set_index('PID')

    # create and clean age plot dataframe
    cleanage_df = age_df[['PID', 'AGE_SP', 'AGE_DIA', 'AGE_ORIG', 'AGE_GRW', 'MISC']] \
        .rename(columns={'MISC': 'AGE_MISC'}) \
        .set_index('PID')

    # join age dataframe to fixed dataframe
    plot_table = cleanfixed_df \
        .merge(right=cleanage_df, how='left', left_on='PID', right_on='PID') \
        .reset_index()

    return plot_table





