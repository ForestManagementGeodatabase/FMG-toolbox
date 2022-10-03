# FMG QA Tools Function Library

import os
import sys
import arcpy
import math
import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor

arcpy.env.overwriteOutput = True


def plot_count(df):
    plot_num = df.PLOT.nunique()

    return plot_num


# Trees Per Acre (TPA)
def density(df):
    """Calculates trees per acre. Returns one value.

    Keyword Arguments:
    df       -- Input prism dataframe
    plot_num -- Number of plots in the hierarchy level being summarized

    Details: Trees per acre is the total number of trees in a given acre.
    """
    assert isinstance(df, pd.DataFrame), "Must be a pandas DataFrame"
    assert df.columns.isin(["TR_DIA"]).any(), "df must contain column TR_DIA"
    assert df.columns.isin(["TR_SP"]).any(), "df must contain column TR_SP"

    baf = 10

    # if there is no tree, density = 0
    df.loc[df.TR_SP.isin(["NONE", "NoTree"]), 'DENSITY'] = 0

    # if there is a tree, use density calc
    df.loc[~df.TR_SP.isin(["NONE", "NoTree"]), 'DENSITY'] = (baf / (0.00545 * df['TR_DIA'] ** 2))

    return df


# Basal Area (BA)
def ba(df, plot_num):
    """Calculates basal area per acre. Returns one value.

    Keyword Arguments:
    df       -- Input prism dataframe
    plot_num -- Number of plots in the hierarchy level being summarized

    Details: Basal area per acre is the cross-section area of all the trees on an acre.
    """
    assert isinstance(df, pd.DataFrame), "must be a pandas DataFrame"
    assert df.columns.isin(["TR_SP"]).any(), "dataframe must contain column TR_SP"
    assert isinstance(plot_num, int), "plot_num must be an integer"

    baf = 10
    trees = ~df.TR_SP.isin(["NONE", "NoTree", "", " ", None])
    no_trees = df.TR_SP.isin(["NONE", "NoTree", "", " ", None]).values.sum()

    tree_count = trees.values.sum() + no_trees

    if tree_count < 1:
        tree_count = 0

    basal_area = (tree_count * baf) / plot_num

    return basal_area


# Quadratic Mean Diameter at Breast Height (QM DBH)
def qm_dbh(df, ba, tpa):
    """Calculates quadratic mean at diameter breast height. Returns one value.

    Keyword Arguments:
    df  -- Input dataframe
    ba  -- Basal area
    tpa -- Trees per acre

    Details:
    Quadratic Mean Diameter ( Dq ) is the diameter of the tree of average per tree basal area.
    This becomes convenient in that we often have basal area per acre and trees per acre but
    not the diameters of all the trees.
    """
    assert isinstance(df, pd.DataFrame), "Must be a pandas DataFrame"

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
