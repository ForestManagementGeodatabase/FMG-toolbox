# FMG QA Tools Function Library

import os
import sys
import arcpy
import math
import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor

arcpy.env.overwriteOutput = True


# Trees Per Acre (TPA)
def tpa(df):
    """Calculates trees per acre. Returns one value.

    Keyword Arguments:
    df -- Input dataframe

    Details: Trees per acre is the total number of trees in a given acre.
    """

    baf = 10
    dbh = df[df.TR_SP != 'NONE'].TR_DIA
    plot_count = df.PLOT.nunique()

    trees_per_acre = (baf / (0.00545 * dbh ** 2)) / plot_count

    total_tpa = trees_per_acre.sum()

    return total_tpa


# Basal Area (BA)
def ba(df):
    """Calculates basal area per acre. Returns one value.

    Keyword Arguments:
    df        -- Input dataframe

    Details: Basal area per acre is the cross-section area of all the trees on an acre.
    """
    assert isinstance(df, pd.DataFrame), "Must be a pandas DataFrame"
    assert df.columns.isin(["TR_SP"]).any(), "df must contain column TR_SP"
    assert df.columns.isin(["PLOT"]).any(), "df must contain column PLOT"

    baf = 10
    tree_count = df.TR_SP.count()
    plot_count = df.PLOT.nunique()

    basal_area = (tree_count * baf) / plot_count

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

    qmdbh = math.sqrt((ba / tpa) / 0.005454154)
    return qmdbh

# Most prevalent ([health, species] by TPA)

# Most prevalent (percent)

# Highest Frequency Species

# Stocking Percent (Total)

# Stocking Percent (Hard Mast)

# Species Richness

# Importance Value

# Forest Community (species list, numeric ID)

# Inventory Date (year, range of years)
