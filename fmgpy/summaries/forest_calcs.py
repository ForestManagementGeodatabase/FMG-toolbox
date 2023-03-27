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

     Keyword Args:
        tr_dia -- diameter of a given tree

     Details: written to function within the pandas .map method
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


# Assign understory height range categorical variable column
def und_height_range_map(height):
    if height < 2:
        return '<2'
    if 2 <= height < 5:
        return '2-5'
    if 5 <= height < 10:
        return '5-10'
    if 10 <= height < 15:
        return '10-15'
    if 15 <= height < 20:
        return '15-20'
    if 20 <= height < 25:
        return '20-25'
    if 25 <= height < 30:
        return '25-30'
    if 30 <= height < 35:
        return '30-35'
    if 35 <= height < 40:
        return '35-40'
    if 40 <= height < 45:
        return '40-45'
    if 45 <= height < 50:
        return '45-50'
    if height >= 50:
        return '>50'


# Create an unfiltered df at specified level, including upstream levels
def create_level_df(level, plot_table):
    """ Creates a data frame to be used as a merge base, it aggregates the plot table based
    on a give level and includes all of the upstream level columns

    Keyword Args:
        level  --  FMG level, use to group input dataframe
        plot_table -- dataframe produced by the create_plot_table function
    """

    if level == 'SID':
        base_df = plot_table \
            .groupby(level) \
            .agg(
                POOL=('POOL', 'first'),
                COMP=('COMP', 'first'),
                UNIT=('UNIT', 'first'),
                SITE=('SITE', 'first')
                ) \
            .reset_index() \
            .set_index(level)
        return base_df

    elif level == 'SITE':
        base_df = plot_table \
            .groupby(level) \
            .agg(
                POOL=('POOL', 'first'),
                COMP=('COMP', 'first'),
                UNIT=('UNIT', 'first')
                ) \
            .reset_index() \
            .set_index(level)
        return base_df

    elif level == 'UNIT':
        base_df = plot_table \
            .groupby(level) \
            .agg(
                POOL=('POOL', 'first'),
                COMP=('COMP', 'first')
                ) \
            .reset_index() \
            .set_index(level)
        return base_df

# Assign vertical composition categorical variable column
def vert_comp_class_map(tr_cl):
    """Maps a vertical forest composition variable onto the tree canopy class
    as specified by USACE foresters

    Keyword Args:
        tr_cl -- canopy class (D:Dominant, CD:Co-Dominant, S:Suppressed, I:Intermediate)
                 for a given tree

    Details: written to function within the pandas .map method
    """

    if tr_cl == 'D':
        return 'Canopy'
    if tr_cl == 'CD':
        return 'Canopy'
    if tr_cl == 'S':
        return 'Midstory'
    if tr_cl == 'I':
        return 'Midstory'


# Create tree intermediate table
def create_tree_table(prism_df):
    """Creates the tree dataframe for use in downstream forest summaries by:
        Column TR_DIA is set to 0 for no tree rows
        Column TR_SIZE is added and populated with size class based on tree diameter ranges
        Column VERT_COMP is added and populated with vertical composition class based on canopy class
        Column TR_BA is added and populated with the eq (tree_count * BAF) / plot_count
        Column TR_DENS is added and populated with the eq (0.005454 * (tr_dia ** 2)) / plot_count

    Keyword Args:
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

    # Add a vertical composition field (Canopy, Midstory)
    tree_table['VERT_COMP'] = tree_table['TR_CL'].map(vert_comp_class_map)

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

    Keyword Args:
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


def tpa_ba_qmdbh_plot(tree_table, filter_statement, group_column):
    """Creates a dataframe with BA, TPA and QM DBH columns at the plot level. The function pivots on the
    group column supplied resulting in BA, TPA and QM DBH columns for each category in the group column.
    For example, if mast_type is specified as the group column BA, TPA and QM DBH will be calculated for
    each mast type for each plot - ba_hard, ba_lightseed, ba_soft, etc.

    Keyword Args:
        tree_table       -- dataframe: input tree_table, produced by the create_tree_table function
        filter_statement -- pandas method: filter statement to be used on the input dataframe, should be a full filter
                            statement i.e. dataframe.field.filter. If no filter is required, None should be supplied.
        group_column     -- string: field name for groupby and pivot_table methods, ba, tpa and qm dbh will be calculated
                            for each category in this field

    Details: filter statement should not be a string, rather just the pandas dataframe filter statement:
    for live trees use: ~tree_table.TR_HLTH.isin(["D", "DEAD"])
    for dead trees use: tree_table.TR_HLTH.isin(["D", "DEAD"])
    if no filter is required, None should be passed in as the keyword argument.
    """
    # Check input parameters are valid
    assert isinstance(tree_table, pd.DataFrame), "must be a pandas DataFrame"
    assert tree_table.columns.isin([group_column]).any(), "df must contain column specified as group column param"
    assert tree_table.columns.isin(["PID"]).any(), "df must contain column PID"

    # Create data frame that preserves unfiltered count of plots by level
    plotcount_df = tree_table \
        .groupby('PID', as_index=False) \
        .agg(plot_count=('PID', agg_plot_count))\
        .set_index('PID')

    # Test for filter statement and run script based on filter or no filter
    if filter_statement is not None:

        # Filter, group and sum tree table
        filtered_df = tree_table[filter_statement] \
            .groupby(['PID', group_column], as_index=False) \
            .agg(
                tree_count=('TR_SP', agg_tree_count),
                plot_count=('PID', agg_plot_count),
                TPA=('TR_DENS', sum),
                BA=('TR_BA', sum)
            )

        # Add and Calculate QM DBH
        filtered_df['QM_DBH'] = qm_dbh(filtered_df['BA'], filtered_df['TPA'])

        # Pivot sizes and metrics to columns
        pivot_df = filtered_df\
            .pivot_table(
                index='PID',
                columns=group_column,
                values=['BA', 'TPA', 'QM_DBH'],
                fill_value=0)\
            .reset_index()

        # flatten column multi index and set index for merge
        pivot_df.columns = list(map(str("_" + group_column + "_").join, pivot_df.columns))
        fixpivot_df = pivot_df.rename(columns={str('PID' + "_" + group_column + "_"): 'PID'}).set_index('PID')

        # Join results back to full set of PIDs and fill nans with 0
        out_df = plotcount_df \
            .drop(['plot_count'], axis=1) \
            .merge(right=fixpivot_df,
                   how='left',
                   on='PID') \
            .fillna(0) \
            .reset_index()

        return out_df

    elif filter_statement is None:

        # Group and sum tree table
        filtered_df = tree_table \
            .groupby(['PID', group_column], as_index=False) \
            .agg(
                tree_count=('TR_SP', agg_tree_count),
                plot_count=('PID', agg_plot_count),
                TPA=('TR_DENS', sum),
                BA=('TR_BA', sum)
            )

        # Add and Calculate QM DBH
        filtered_df['QM_DBH'] = qm_dbh(filtered_df['BA'], filtered_df['TPA'])

        # Pivot sizes and metrics to columns
        pivot_df = filtered_df \
            .pivot_table(
                index='PID',
                columns=group_column,
                values=['BA', 'TPA', 'QM_DBH'],
                fill_value=0) \
            .reset_index()

        # flatten column multi index and set index for merge
        pivot_df.columns = list(map(str("_" + group_column + "_").join, pivot_df.columns))
        fixpivot_df = pivot_df.rename(columns={str('PID' + "_" + group_column + "_"): 'PID'}).set_index('PID')

        # Join results back to full set of PIDs and fill nans with 0
        out_df = plotcount_df \
            .drop(['plot_count'], axis=1) \
            .merge(right=fixpivot_df,
                   how='left',
                   on='PID') \
            .fillna(0) \
            .reset_index()

        return out_df


def tpa_ba_qmdbh_level(tree_table, filter_statement, group_column, level):
    """Creates a dataframe with BA, TPA and QM DBH columns at a specified level. The function pivots on the
    group column supplied resulting in BA, TPA and QM DBH columns for each category in the group column.
    For example, if mast_type is specified as the group column BA, TPA and QM DBH will be calculated for
    each mast type for each level polygon - ba_hard, ba_lightseed, ba_soft, etc.

    Keyword Args:
        tree_table       -- dataframe: input tree_table, produced by the create_tree_table function
        filter_statement -- pandas method: filter statement to be used on the input dataframe, should be a full filter
                            statement i.e. dataframe.field.filter. If no filter is required, None should be supplied.
        group_column     -- string: field name for groupby and pivot_table methods, ba, tpa and qm dbh will be
                            calculated for each category in this field
        level            -- string: field name for desired FMG level, i.e. SID, SITE, UNIT

    Details: filter statement should not be a string, rather just the pandas dataframe filter statement:
    for live trees use: ~tree_table.TR_HLTH.isin(["D", "DEAD"])
    for dead trees use: tree_table.TR_HLTH.isin(["D", "DEAD"])
    if no filter is required, None should be passed in as the keyword argument.
    """

    # Check input parameters are valid
    assert isinstance(tree_table, pd.DataFrame), "must be a pandas DataFrame"
    assert tree_table.columns.isin([group_column]).any(), "df must contain column specified as group column param"
    assert tree_table.columns.isin([level]).any(), "df must contain column specified as level param"

    # Create data frame that preserves unfiltered count of plots by level
    plotcount_df = tree_table \
        .groupby(level, as_index=False) \
        .agg(plot_count=('PID', agg_plot_count)) \
        .set_index(level)

    # Test for filter statement and run script based on filter or no filter
    if filter_statement is not None:

        # Filter, group and sum tree table, add unfiltered plot count field
        filtered_df = tree_table[filter_statement] \
            .groupby([level, group_column], as_index=False) \
            .agg(
                tree_count=('TR_SP', agg_tree_count),
                stand_dens=('TR_DENS', sum)
            ) \
            .set_index(level) \
            .merge(right=plotcount_df,
                   how='left',
                   on=level) \
            .reset_index()

        # Add and calculate TPA, BA, QM_DBH
        baf = 10
        filtered_df['TPA'] = filtered_df['stand_dens'] / filtered_df['plot_count']
        filtered_df['BA'] = (filtered_df['tree_count'] * baf) / filtered_df['plot_count']
        filtered_df['QM_DBH'] = qm_dbh(filtered_df['BA'], filtered_df['TPA'])

        # Pivot sizes and metrics to columns
        pivot_df = filtered_df \
            .pivot_table(
                index=level,
                columns=group_column,
                values=['BA', 'TPA', 'QM_DBH'],
                fill_value=0) \
            .reset_index()

        # flatten column to multi index
        pivot_df.columns = list(map(str("_" + group_column + "_").join, pivot_df.columns))
        fixpivot_df = pivot_df.rename(columns={str(level + "_" + group_column + "_"): level}).set_index(level)

        # Join results back to full set of level polygons and fill nans with 0
        out_df = plotcount_df \
            .drop(['plot_count'], axis=1) \
            .merge(right=fixpivot_df,
                   how='left',
                   on=level) \
            .fillna(0) \
            .reset_index()

        return out_df

    elif filter_statement is None:

        # Group and sum tree table
        filtered_df = tree_table \
            .groupby([level, group_column], as_index=False) \
            .agg(
                tree_count=('TR_SP', agg_tree_count),
                stand_dens=('TR_DENS', sum),
            ) \
            .set_index(level) \
            .merge(right=plotcount_df,
                   how='left',
                   on=level) \
            .reset_index()

        # Add and calculate TPA, BA, QM_DBH
        baf = 10
        filtered_df['TPA'] = filtered_df['stand_dens'] / filtered_df['plot_count']
        filtered_df['BA'] = (filtered_df['tree_count'] * baf) / filtered_df['plot_count']
        filtered_df['QM_DBH'] = qm_dbh(filtered_df['BA'], filtered_df['TPA'])

        # Pivot sizes and metrics to columns
        pivot_df = filtered_df \
            .pivot_table(
                index=level,
                columns=group_column,
                values=['BA', 'TPA', 'QM_DBH'],
                fill_value=0) \
            .reset_index()

        # flatten column to multi index
        pivot_df.columns = list(map(str("_" + group_column + "_").join, pivot_df.columns))
        fixpivot_df = pivot_df.rename(columns={str(level + "_" + group_column + "_"): level}).set_index(level)

        # Join results back to full set of level polygons and fill nan with 0
        out_df = plotcount_df \
            .drop(['plot_count'], axis=1) \
            .merge(right=fixpivot_df,
                   how='left',
                   on=level) \
            .fillna(0) \
            .reset_index()

        return out_df


def date_range(min_year, max_year):
    if min_year == max_year:
        return str(min_year)
    else:
        return str(min_year) + "-" + str(max_year)


def create_general_description_level(tree_table, plot_table, level):
    # Create base table
    base_df = create_level_df(level, tree_table)

    # total num age trees - plot table
    # total num plots (all, no filter) - plot table
    # mean overstory closure - plot table
    # overstory closure standard deviation - plot table
    # mean overstory height - plot table
    # overstory height standard deviation - plot table
    # mean understory cover - plot table
    # understory cover standard deviation - plot table
    # mean understory height (number) - plot table
    # understory height standard deviation - plot table
    gendesc = plot_table \
        .groupby([level]) \
        .agg(
        NUM_PLOTS=('PID', agg_plot_count),
        NUM_AGE_TR=('AGE_SP', 'count'),
        MEAN_OV_CLSR=('OV_CLSR', 'mean'),
        STD_OV_CLSR=('OV_CLSR', 'std'),
        MEAN_OV_HT=('OV_HT', 'mean'),
        STD_OV_HT=('OV_HT', 'std'),
        MEAN_UND_COV=('UND_COV', 'mean'),
        STD_UND_COV=('UND_COV', 'std'),
        MEAN_UND_HT=('UND_HT2', 'mean'),
        STD_UND_HT=('UND_HT2', 'std')
    ) \
        .reset_index() \
        .set_index([level])

    # mean under story height (range value) - plot table
    gendesc['MEAN_UND_HT_RG'] = gendesc['MEAN_UND_HT'].map(und_height_range_map)

    # BA live trees - tree table
    ba_live = tree_table[~tree_table.TR_HLTH.isin(["D", "DEAD"])] \
        .groupby([level]) \
        .apply(ba)
    ba_live_df = pd.DataFrame({level: ba_live.index, 'BA_LIVE': ba_live.values}).set_index([level])

    # TPA live trees - tree table
    tpa_live = tree_table[~tree_table.TR_HLTH.isin(["D", "DEAD"])] \
        .groupby([level]) \
        .apply(tpa)
    tpa_live_df = pd.DataFrame({level: tpa_live.index, 'TPA_LIVE': tpa_live.values}).set_index([level])

    # total num trees (all, no filter) - tree table
    tr_all = tree_table \
        .groupby([level]) \
        .apply(tree_count)
    tr_all_df = pd.DataFrame({level: tr_all.index, 'NUM_TR': tr_all.values}).set_index([level])

    # total num live trees - tree table
    tr_live = tree_table[~tree_table.TR_HLTH.isin(["D", "DEAD"])] \
        .groupby([level]) \
        .apply(tree_count)
    tr_live_df = pd.DataFrame({level: tr_live.index, 'NUM_TR_LIVE': tr_live.values}).set_index([level])

    # total num dead trees - tree table
    tr_dead = tree_table[tree_table.TR_HLTH.isin(["D", "DEAD"])] \
        .groupby([level]) \
        .apply(tree_count)
    tr_dead_df = pd.DataFrame({level: tr_dead.index, 'NUM_TR_DEAD': tr_dead.values}).set_index([level])

    # Average Mean Diameter live trees - tree table
    # Max DBH live trees - tree table
    diam_df = tree_table[~tree_table.TR_HLTH.isin(["D", "DEAD"])] \
        .groupby([level]) \
        .agg(
        AMD=('TR_DIA', 'mean'),
        MAX_DBH=('TR_DIA', 'max')
    ) \
        .reset_index() \
        .set_index([level])

    # Collection date
    date_df = tree_table\
        .groupby([level], as_index=False) \
        .agg(
            min_date=('COL_DATE', 'min'),
            max_date=('COL_DATE', 'max')
            )
    date_df['min_year'] = date_df['min_date'].dt.year
    date_df['max_year'] = date_df['max_date'].dt.year
    date_df["COL_YEAR"] = date_df.apply(lambda x: date_range(x["min_year"], x["max_year"]), axis=1)

    date_df = date_df.drop(columns=['min_date', 'max_date', 'min_year', 'max_year']).set_index(level)

    # merge component dataframes
    gendesc_df = base_df \
        .join([gendesc,
               ba_live_df,
               tpa_live_df,
               tr_all_df,
               tr_live_df,
               tr_dead_df,
               diam_df,
               date_df]) \
        .reset_index()

    # QM DBH live trees - tree table
    gendesc_df['QM_DBH_LIVE'] = qm_dbh(gendesc_df['BA_LIVE'], gendesc_df['TPA_LIVE'])

    return gendesc_df
