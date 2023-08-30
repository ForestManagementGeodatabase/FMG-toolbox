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
    assert isinstance(ba, float), "basal area must be a float"
    assert isinstance(tpa, float), "tpa must be a float"

    qmdbh = math.sqrt((ba / tpa) / 0.005454154)
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








