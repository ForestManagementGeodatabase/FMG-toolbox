# FMG QA Tools Function Library

import os
import sys
import arcpy
import math
import pandas as pd
import numpy as np
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import itertools
arcpy.env.overwriteOutput = True


# Set summary level based on user input
def fmg_level(level):
    """Get the FMG level field

    :param level: The FMG hierarchical level. One of: "unit", "site", "stand", "plot"
    :type level: string
    :returns: The Field name of the FMG level
    :rtype: str
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


# Create an unfiltered df at specified level, including upstream levels
def create_level_df(level, plot_table):
    """ Creates a data frame to be used as a merge base, it aggregates the plot table based
    on a given level and includes all the upstream level columns

    :param level: FMG level, used to group input dataframe
    :type level: str
    :param plot_table: Specific dataframe produced by the create_plot_table function
    :type plot_table: pandas.DataFrame
    :returns: Data frame with level IDs
    :rtype: pandas.DataFrame
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

    elif level == 'COMP':
        base_df = plot_table\
            .groupby(level)\
            .agg(
                POOL=('POOL', 'first'))\
            .reset_index()\
            .set_index(level)
        return base_df

    elif level == 'POOL':
        base_df = plot_table\
            .groupby(level)\
            .agg(PLT_CT=('PID', 'count'))\
            .reset_index()\
            .set_index(level)
        return base_df

    elif level == 'PID':
        base_df = plot_table \
            .groupby(level) \
            .agg(
                POOL=('POOL', 'first'),
                COMP=('COMP', 'first'),
                UNIT=('UNIT', 'first'),
                SITE=('SITE', 'first'),
                SID=('SID', 'first')
                )\
            .reset_index()\
            .set_index(level)
        return base_df


# Create ordered list of columns for output gdb tables
def fmg_column_reindex_list(level, col_csv):
    """ Creates a list of hierarchy and statistic columns in a specific order. Primarily used when creating
    thematic output tables for use in GIS

    :param level: FMG level, one of any PID, SID, SITE, UNIT, COMP, POOL
    :type level: str
    :param col_csv: csv defining the table schema
    :type col_csv: csv
    :returns: a list of column names to be used in a reindex method
    :rtype: list
    """

    # Create list of upstream levels based on current level
    levels_list = []
    if level == 'PID':
        levels_list = ['POOL', 'COMP', 'UNIT', 'SITE', 'SID', 'PID']
    elif level == 'SID':
        levels_list = ['POOL', 'COMP', 'UNIT', 'SITE', 'SID']
    elif level == 'SITE':
        levels_list = ['POOL', 'COMP', 'UNIT', 'SITE']
    elif level == 'UNIT':
        levels_list = ['POOL', 'COMP', 'UNIT']
    elif level == 'COMP':
        levels_list = ['POOL', 'COMP']
    elif level == 'POOL':
        levels_list = ['POOL']

    # Import the column definition csv
    col_list_df = pd.read_csv(col_csv)

    # Covert column definition df to list
    col_list = col_list_df['COL_NAME'].values.tolist()
    reindex_cols = levels_list + col_list

    return reindex_cols


# Create dictionary of nan fill values for output gdb tables
def fmg_nan_fill(col_csv):
    """ Creates a dictionary with key value pairs of field name and nan fill value.
    Used to clean up the data frame prior to export to ArcGIS GDB table

    :param col_csv: csv defining the table schema
    :type col_csv: csv
    :returns: a dictionary of column names (keys) and their nan fill values (values)
    :rtype: dict
    """

    # import the column definition csv
    col_list_df = pd.read_csv(col_csv)

    # Create dictionary for just string fill nans
    col_list_str = col_list_df[col_list_df['REQ_NAN_STR_FILL'] == 'Yes']
    str_dict = None
    if len(col_list_str.index) > 0:
        str_cols = col_list_str['COL_NAME'].values.tolist()
        str_vals = col_list_str['VALUE_NAN_STR'].values.tolist()
        str_dict = dict(zip(str_cols, str_vals))

    # Create df for just num fill nans
    col_list_num = col_list_df[col_list_df['REQ_NAN_NUM_FILL'] == 'Yes']
    num_dict = None
    if len(col_list_num.index) > 0:
        num_cols = col_list_num['COL_NAME'].values.tolist()
        num_vals = col_list_num['VALUE_NAN_NUM'].values.tolist()
        num_dict = dict(zip(num_cols, num_vals))

    # Return either or, or, if there are both str and num dicts, combine
    if str_dict is None:
        out_dict = num_dict
    elif num_dict is None:
        out_dict = str_dict
    else:
        out_dict = num_dict | str_dict

    return out_dict


# Function to enforce data types in Python/Pandas
def fmg_dtype_enforce(col_csv):
    """ Creates a dictionary of dtypes for each column name as defined by the columns in the csv.

    :param col_csv: csv defining the correct data types by column name
    :type col_csv: csv
    :returns: a dictionary of column names (keys) and their dtypes (values)
    :rtype: dict
    """

    # Import the column csv
    dtype_list_df = pd.read_csv(col_csv)

    # Create the dictionary
    dtype_cols = dtype_list_df['COL_NAME'].values.tolist()
    dtype_types = dtype_list_df['OUTPUT_DTYPE'].values.tolist()
    dtype_dict = dict(zip(dtype_cols, dtype_types))

    return dtype_dict


# Plot count: use with group by - agg
def agg_plot_count(PID):
    """Generates a count of unique plots. Designed to be used in a group by, agg pattern with a pandas dataframe.

    :param PID: data frame column name for plot IDs
    :type PID: str
    :returns: a count of unique plots
    :rtype: float
    """
    return float(PID.nunique())


# Tree count: use with group by - agg
def agg_tree_count(tr_sp):
    """Generates a count of trees, excluding no tree records. Designed to be used in a group by, agg pattern with a
    pandas dataframe.

    :param tr_sp: data frame column name for tree species
    :type tr_sp: str
    :returns: a count of trees
    :rtype: float
    """
    trees = []
    for val in tr_sp:
        if val == 'NoTree':
            continue
        elif val == 'NONE':
            continue
        elif val == 'NO TREE':
            continue
        elif val == 'NO TREES':
            continue
        elif val == 'NOTREE':
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


# List of invasive species: use with group by - agg
def agg_inv_sp(inv_sp):
    """Builds a list of unique invasive species from a pandas group by object. Designed to be used in a group by,
       agg pattern with a pandas dataframe.

       :param inv_sp: data frame column name for invasive species
       :type inv_sp: str
       :returns: A string formatted as a comma-seperated list of unique invasive species
       :rtype: str
    """

    sp_temp = []

    # Build list of invasive species codes
    for val in inv_sp:
        if val == '':
            continue
        elif val is not None:
            sp_temp.append(val.split(', '))

    sp = list(itertools.chain.from_iterable(itertools.repeat(x, 1) if isinstance(x, str) else x for x in sp_temp))

    # Convert array to list then single string
    sp_array = np.array(sp)
    sp_unique = np.unique(sp_array)
    spval = ', '.join(sp_unique.tolist())

    return spval


# Create function to return YES if invasive species are present
def agg_inv_present(inv_present):
    """Generates a single yes/no value based on items in a pandas group by object. Designed to be used in a group by,
       agg pattern with a pandas dataframe.

       :param inv_present: data frame column name indicating if invasive species are present
       :type inv_present: str
       :returns: a single yes or no value
       :rtype: str
    """
    inv_pres = []
    for val in inv_present:
        if val == 'No':
            continue
        else:
            inv_pres.append(val)

    if len(inv_pres) > 0:
        inv_present = 'Yes'

    return inv_present


# Count of notes: use with group by - agg
def agg_count_notes(note_column):
    """Generates a single value representing a count of strings present in a single column in a pandas group by
       object. Designed to be used in a group by, agg pattern with a pandas dataframe

       :param note_column: Data frame column name containing notes
       :type note_column: str
       :returns: a single integer representing rows with strings
       :rtype: int
    """
    note_column.replace('', pd.NA, inplace=True)
    note_column.replace(' ', pd.NA, inplace=True)
    note_column_clean = note_column.dropna()
    notecount = len(note_column_clean)
    return notecount


# Tree count: use with group by - apply
def tree_count(df):
    """Generates a count of trees excluding none or no tree records. Designed to be used in a pandas group by, apply
       pattern. Assumes a column named TR_SP exists.

       :param df: A dataframe containing individual tree records (prism plots)
       :type df: pandas.DataFrame
       :returns: a single integer representing number of trees
       :rtype: int
    """
    # boolean series
    trees = ~df.TR_SP.isin(["NONE", "NoTree", "", " ", None])

    # sum number of True instances
    num_trees = trees.values.sum()
    return num_trees


# Populate column with list of invasive species codes: use with apply - lambda
def inv_sp_list(col_list):
    """Generates a list of unique invasive species codes found in the provided list of pandas dataframe columns.
       Designed to be used in a pandas group by, apply pattern. Function should be passed as a lambda function.
       Curently, this only looks for the invasive species HUJA, PHAR3, and PHAU7.

       :params col_list: a list of column names from a pandas dataframe
       :type col_list: pandas.Index
       :returns: a string listing the invasive species codes
       :rtype: str
    """

    sp_list = []
    for col in col_list:
        if col == 'HUJA':
            sp_list.append('HUJA')
        elif col == 'PHAR3':
            sp_list.append('PHAR3')
        elif col == 'PHAU7':
            sp_list.append('PHAU7')
    sp_set = set(sp_list)
    sp_val = ', '.join(sp_set)
    return sp_val


# Create a column with year or year range: use with apply - lambda
def date_range(min_year, max_year):
    """Generates a single year or year range for a pandas group by object. Designed to be used in a pandas group by,
       apply pattern and passed in as a lambda function.

       :param min_year: pandas dataframe column containing the minimum year
       :type min_year: pandas.Index
       :param max_year: pandas dataframe column containing the maximum year
       :type max_year: pandas.Index
       :returns: a single year or year range formatted as a string value
       :rtype: str
    """
    if min_year == max_year:
        return str(min_year)
    else:
        return str(min_year) + "-" + str(max_year)


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


# Assign size class categorical variable column
def size_class_map(tr_dia):
    """Maps a size class categorical variable onto the tree diameter range
     as specified by USACE foresters

     Keyword Args:
        tr_dia -- diameter of a given tree

     Details: written to function within the pandas .map method
     """

    if 1 <= tr_dia <=6:
        return 'Sapling'
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


# Assign tree type categorical variable column
def tree_type_map(tr_dia):
    if tr_dia >= 30:
        return 'Wildlife'


def overstory_sp_map(sp_rank):
    if sp_rank == 1:
        return 'OV_SP1'
    if sp_rank == 2:
        return 'OV_SP2'
    if sp_rank == 3:
        return 'OV_SP3'
    if sp_rank == 4:
        return 'OV_SP4'
    if sp_rank == 5:
        return 'OV_SP5'


def health_rank_map(tr_hlth):
    if tr_hlth == 'H':
        return 1
    if tr_hlth == 'S':
        return 2
    if tr_hlth == 'SD':
        return 3
    if tr_hlth == 'D':
        return 4
    if tr_hlth == 'NT':
        return 5


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

    try:
        qmdbh = np.sqrt((ba / tpa) / 0.005454154)
    except TypeError:
        qmdbh = None

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
    #assert isinstance(avg_tpa, float), "avg_tpa must be a float"
    #assert isinstance(qm_dbh, float), "qm_dbh must be a float"

    # Define equation params
    amd_p1 = 0.259
    amd_p2 = 0.973
    a_line_p1 = 0.0685724
    a_line_p2 = 0.0010125
    a_line_p3 = 0.0023656

    try:
        # Convert QM DBH to AMD
        amd = amd_p1 + (amd_p2 * qm_dbh)

        # Run stocking percent equation
        stock_pct = avg_tpa * (a_line_p1 + a_line_p2 * amd + a_line_p3 * qm_dbh ** 2)

    except TypeError:
        stock_pct = None

    return stock_pct


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
    tree_table.loc[tree_table.TR_SP.isin(["NONE", "NoTree", "NOTREE"]), 'TR_DIA'] = 0

    # Add a tree size class field (Sap, Pole, Saw, Mature, Over Mature)
    tree_table['TR_SIZE'] = tree_table['TR_DIA'].map(size_class_map)

    # Add a vertical composition field (Canopy, Midstory)
    tree_table['VERT_COMP'] = tree_table['TR_CL'].map(vert_comp_class_map)

    # Add a tree type field (currently only wildlife)
    tree_table['TR_TYPE'] = tree_table['TR_DIA'].map(tree_type_map)

    # Define constants for BA & Density calcs, assuming 1 tree, 1 plot
    tree_count = 1
    plot_count = 1
    baf = 10
    forester_constant = 0.005454

    # Add and Calculate BA column, then set BA to 0 where no tree
    tree_table['TR_BA'] = (tree_count * baf) / plot_count
    tree_table.loc[tree_table.TR_SP.isin(["NONE", "NoTree", "NOTREE"]), 'TR_BA'] = 0

    # Add and calculate density column (TPA)
    tree_table['TR_DENS'] = np.where(tree_table['TR_DIA'] > 0,
                                     (baf / (forester_constant * (tree_table['TR_DIA'] ** 2))),
                                     0)
    tree_table = tree_table.astype({'TR_DENS': 'float64'})

    # Add SP_TYPE Column
    crosswalk_df = pd.read_csv('resources/MAST_SP_TYP_Crosswalk.csv')\
        .filter(items=['TR_SP', 'TYP_FOR_MVR', 'SP_RICH_TYPE'])

    tree_table = tree_table\
        .merge(right=crosswalk_df, how='left', on='TR_SP')\
        .rename(columns={'TYP_FOR_MVR': 'SP_TYPE'})

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
        .drop(columns=['CREATED_USER', 'CREATED_DATE',
                       'LAST_EDITED_USER', 'LAST_EDITED_DATE',
                       'SE_ANNO_CAD_DATA', 'OBJECTID'],
              errors='ignore') \
        .rename(columns={'MISC': 'FX_MISC'}) \
        .set_index('PID')

    # create and clean age plot dataframe
    cleanage_df = age_df[['PID', 'AGE_SP', 'AGE_DIA', 'AGE_ORIG', 'AGE_GRW', 'MISC', 'MAST_TYPE']] \
        .rename(columns={'MISC': 'AGE_MISC'}) \
        .set_index('PID')

    # join age dataframe to fixed dataframe
    plot_table = cleanfixed_df \
        .merge(right=cleanage_df, how='left', left_on='PID', right_on='PID') \
        .reset_index()

    # Define list of specific invasive species
    invsp = ['HUJA', 'PHAR3', 'PHAU7']

    # Drop shape from plot table
    plot_table2 = plot_table.drop(columns=['SHAPE'])

    # filter dataset to just records with invasive species
    invsp_filter_df = plot_table2[plot_table['GRD_SP1'].isin(invsp) |
                                  plot_table['GRD_SP2'].isin(invsp) |
                                  plot_table['GRD_SP3'].isin(invsp) |
                                  plot_table['NOT_SP1'].isin(invsp) |
                                  plot_table['NOT_SP2'].isin(invsp) |
                                  plot_table['NOT_SP3'].isin(invsp) |
                                  plot_table['NOT_SP4'].isin(invsp) |
                                  plot_table['NOT_SP5'].isin(invsp)] \
        .reset_index()

    # Count the rows in the filtered dataset
    invsp_filter_df_len = len(invsp_filter_df)

    # do the invasive species operations only if there are invasive species present

    if invsp_filter_df_len == 0:

        # Add and populate invasive species columns
        plot_table['INV_SP'] = ''
        plot_table['INV_PRESENT'] = 'No'

        # Clean up plot table
        plot_table = plot_table\
            .reset_index() \
            .drop(columns=['index', 'level_0'], errors='ignore') \
            .astype(dtype={"INV_SP": 'string', "INV_PRESENT": 'string'}) \
            .fillna(value={"AGE_MISC": ''})

    elif invsp_filter_df_len != 0:

        # add and populate invasive presence column
        invsp_filter_df['INV_PRESENT'] = 'Yes'

        # add and populate invasive species present column
        invsp_filter_df['INV_SP'] = invsp_filter_df \
            .apply(lambda x: inv_sp_list([x['GRD_SP1'], x['GRD_SP2'], x['GRD_SP3'],
                                          x['NOT_SP1'], x['NOT_SP2'], x['NOT_SP3'],
                                          x['NOT_SP4'], x['NOT_SP5']]), axis=1)

        # Set indices for merge
        plot_table.set_index('PID')
        invsp_filter_df.set_index('PID')

        plot_table = plot_table \
            .merge(right=invsp_filter_df,
                   how='left')\
            .reset_index()\
            .drop(columns=['index', 'level_0']) \
            .astype(dtype={"INV_SP": 'string', "INV_PRESENT": 'string'}) \
            .fillna(value={"AGE_MISC": '', "INV_SP": '', "INV_PRESENT": 'No'})

    return plot_table


# Generate TPA, BA, QM DBH at PID level
def tpa_ba_qmdbh_plot(tree_table, filter_statement):
    """Creates a dataframe with BA, TPA and QM DBH columns at the plot level, based on the specified filter.

    Keyword Args:
        tree_table       -- dataframe: input tree_table, produced by the create_tree_table function
        filter_statement -- pandas series: filter statement to be used on the input dataframe, should be a full filter
                            statement i.e. dataframe.field.filter. If no filter is required, None should be supplied.

    Details: filter statement should not be a string, rather just the pandas dataframe filter statement:
    for live trees use: ~tree_table.TR_HLTH.isin(["D", "DEAD"])
    for dead trees use: tree_table.TR_HLTH.isin(["D", "DEAD"])
    if no filter is required, None should be passed in as the keyword argument.
    """
    # Check input parameters are valid
    assert isinstance(tree_table, pd.DataFrame), "must be a pandas DataFrame"
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
            .groupby(['PID'], as_index=False) \
            .agg(
                tree_count=('TR_SP', agg_tree_count),
                plot_count=('PID', agg_plot_count),
                TPA=('TR_DENS', sum),
                BA=('TR_BA', sum)
            )

        # Add and Calculate QM DBH
        filtered_df['QM_DBH'] = np.where(filtered_df['tree_count'] > 0,
                                         (np.sqrt((filtered_df['BA'] / filtered_df['TPA']) / 0.005454154)),
                                         0)

        # Enforce dtypes
        filtered_df = filtered_df.astype({'tree_count': 'int32',
                                          'plot_count': 'int32',
                                          'TPA': 'float64',
                                          'BA': 'float64',
                                          'QM_DBH': 'float64'})

        # Set index for merge
        filtered_df.set_index('PID')

        # Join results back to full set of PIDs and fill nans with 0
        merge_df = plotcount_df \
            .drop(columns=['plot_count']) \
            .merge(right=filtered_df,
                   how='left',
                   on='PID') \
            .reset_index()

        # Test merged df for data, then fillna if data
        if len(merge_df.index) > 0:
            out_df = merge_df.fillna(0)
        else:
            out_df = merge_df

        return out_df

    elif filter_statement is None:

        # Group and sum tree table
        filtered_df = tree_table \
            .groupby(['PID'], as_index=False) \
            .agg(
                tree_count=('TR_SP', agg_tree_count),
                plot_count=('PID', agg_plot_count),
                TPA=('TR_DENS', sum),
                BA=('TR_BA', sum)
            )

        # Add and Calculate QM DBH
        filtered_df['QM_DBH'] = np.where(filtered_df['tree_count'] > 0,
                                         (np.sqrt((filtered_df['BA'] / filtered_df['TPA']) / 0.005454154)),
                                         0)

        # Enforce QM_DBH dtype
        filtered_df = filtered_df.astype({'QM_DBH': 'float64'})

        # Set index for merge
        filtered_df.set_index('PID')

        # Join results back to full set of PIDs and fill nans with 0
        out_df = plotcount_df \
            .drop(columns=['plot_count']) \
            .merge(right=filtered_df,
                   how='left',
                   on='PID') \
            .fillna(0) \
            .reset_index()

        return out_df


# Generate TPA, BA, QM DBH given a case field at PID level (pivots on case field to wide)
def tpa_ba_qmdbh_plot_by_case(tree_table, filter_statement, case_column):
    """Creates a dataframe with BA, TPA and QM DBH columns at the plot level. The function pivots on the
    case column supplied resulting in BA, TPA and QM DBH columns for each category in the case column.
    For example, if mast_type is specified as the group column BA, TPA and QM DBH will be calculated for
    each mast type for each plot - ba_hard, ba_lightseed, ba_soft, etc.

    Keyword Args:
        tree_table       -- dataframe: input tree_table, produced by the create_tree_table function
        filter_statement -- pandas series: filter statement to be used on the input dataframe, should be a full filter
                            statement i.e. dataframe.field.filter. If no filter is required, None should be supplied.
        case_column      -- string: column name for groupby and pivot_table methods, ba, tpa and qm dbh will be calculated
                            for each case in this column

    Details: filter statement should not be a string, rather just the pandas dataframe filter statement:
    for live trees use: ~tree_table.TR_HLTH.isin(["D", "DEAD"])
    for dead trees use: tree_table.TR_HLTH.isin(["D", "DEAD"])
    if no filter is required, None should be passed in as the keyword argument.
    """
    # Check input parameters are valid
    assert isinstance(tree_table, pd.DataFrame), "must be a pandas DataFrame"
    assert tree_table.columns.isin([case_column]).any(), "df must contain column specified as group column param"
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
            .groupby(['PID', case_column], as_index=False) \
            .agg(
                tree_count=('TR_SP', agg_tree_count),
                plot_count=('PID', agg_plot_count),
                TPA=('TR_DENS', sum),
                BA=('TR_BA', sum)
            )

        # Add and Calculate QM DBH
        filtered_df['QM_DBH'] = np.where(filtered_df['tree_count'] > 0,
                                         (np.sqrt((filtered_df['BA'] / filtered_df['TPA']) / 0.005454154)),
                                         0)

        # Pivot sizes and metrics to columns
        pivot_df = filtered_df\
            .pivot_table(
                index='PID',
                columns=case_column,
                values=['BA', 'TPA', 'QM_DBH'],
                fill_value=0)\
            .reset_index()

        # flatten column multi index and set index for merge
        pivot_df.columns = list(map(str("_" + case_column + "_").join, pivot_df.columns))
        fixpivot_df = pivot_df.rename(columns={str('PID' + "_" + case_column + "_"): 'PID'}).set_index('PID')

        # Join results back to full set of PIDs and fill nans with 0
        out_df = plotcount_df \
            .drop(columns=['plot_count']) \
            .merge(right=fixpivot_df,
                   how='left',
                   on='PID') \
            .fillna(0) \
            .reset_index()

        return out_df

    elif filter_statement is None:

        # Group and sum tree table
        filtered_df = tree_table \
            .groupby(['PID', case_column], as_index=False) \
            .agg(
                tree_count=('TR_SP', agg_tree_count),
                plot_count=('PID', agg_plot_count),
                TPA=('TR_DENS', sum),
                BA=('TR_BA', sum)
            )

        # Add and Calculate QM DBH
        filtered_df['QM_DBH'] = np.where(filtered_df['tree_count'] > 0,
                                         (np.sqrt((filtered_df['BA'] / filtered_df['TPA']) / 0.005454154)),
                                         0)

        # Pivot sizes and metrics to columns
        pivot_df = filtered_df \
            .pivot_table(
                index='PID',
                columns=case_column,
                values=['BA', 'TPA', 'QM_DBH'],
                fill_value=0) \
            .reset_index()

        # flatten column multi index and set index for merge
        pivot_df.columns = list(map(str("_" + case_column + "_").join, pivot_df.columns))
        fixpivot_df = pivot_df.rename(columns={str('PID' + "_" + case_column + "_"): 'PID'}).set_index('PID')

        # Join results back to full set of PIDs and fill nans with 0
        out_df = plotcount_df \
            .drop(columns=['plot_count']) \
            .merge(right=fixpivot_df,
                   how='left',
                   on='PID') \
            .fillna(0) \
            .reset_index()

        return out_df


# Generate TPA, BA, QM DBH given a case field at PID level (no pivot, stays long)
def tpa_ba_qmdbh_plot_by_case_long(tree_table, filter_statement, case_column):
    """Creates a dataframe with BA, TPA and QM DBH columns at the plot level. The function does not pivot
    on the case field, instead leaving it in long form. Each row of the resulting data frame will be a
    single instance of a plot/PID and case, with just 3 columns for TPA, BA and QDBH.

    Keyword Args:
        tree_table       -- dataframe: input tree_table, produced by the create_tree_table function
        filter_statement -- pandas series: filter statement to be used on the input dataframe, should be a full filter
                            statement i.e. dataframe.field.filter. If no filter is required, None should be supplied.
        case_column      -- string: column name for groupby and pivot_table methods, ba, tpa and qm dbh will be calculated
                            for each case in this column

    Details: filter statement should not be a string, rather just the pandas dataframe filter statement:
    for live trees use: ~tree_table.TR_HLTH.isin(["D", "DEAD"])
    for dead trees use: tree_table.TR_HLTH.isin(["D", "DEAD"])
    if no filter is required, None should be passed in as the keyword argument.
    """
    # Check input parameters are valid
    assert isinstance(tree_table, pd.DataFrame), "must be a pandas DataFrame"
    assert tree_table.columns.isin([case_column]).any(), "df must contain column specified as group column param"
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
            .groupby(['PID', case_column], as_index=False) \
            .agg(
                tree_count=('TR_SP', agg_tree_count),
                plot_count=('PID', agg_plot_count),
                TPA=('TR_DENS', sum),
                BA=('TR_BA', sum)
            )

        # Add and Calculate QM DBH
        filtered_df['QM_DBH'] = np.where(filtered_df['tree_count'] > 0,
                                         (np.sqrt((filtered_df['BA'] / filtered_df['TPA']) / 0.005454154)),
                                         0)

        # Join results back to full set of PIDs
        out_df = plotcount_df \
            .drop(columns=['plot_count']) \
            .merge(right=filtered_df,
                   how='inner',
                   on='PID') \
            .reset_index()

        return out_df

    elif filter_statement is None:

        # Group and sum tree table
        filtered_df = tree_table \
            .groupby(['PID', case_column], as_index=False) \
            .agg(
                tree_count=('TR_SP', agg_tree_count),
                plot_count=('PID', agg_plot_count),
                TPA=('TR_DENS', sum),
                BA=('TR_BA', sum)
            )

        # Add and Calculate QM DBH
        filtered_df['QM_DBH'] = np.where(filtered_df['tree_count'] > 0,
                                         (np.sqrt((filtered_df['BA'] / filtered_df['TPA']) / 0.005454154)),
                                         0)

        # Join results back to full set of PIDs
        out_df = plotcount_df \
            .drop(columns=['plot_count']) \
            .merge(right=filtered_df,
                   how='inner',
                   on='PID') \
            .reset_index()

        return out_df


# Generate TPA, BA, QM DBH given multiple case fields at PID level (no pivot, stays long)
def tpa_ba_qmdbh_plot_by_multi_case_long(tree_table, filter_statement, case_columns):
    """Creates a dataframe with BA, TPA and QM DBH columns at the plot level. The function does not pivot
    on the case field, instead leaving it in long form. Each row of the resulting data frame will be a
    single instance of a plot/PID and case, with just 3 columns for TPA, BA and QDBH.

    Keyword Args:
        tree_table       -- dataframe: input tree_table, produced by the create_tree_table function
        filter_statement -- pandas series: filter statement to be used on the input dataframe, should be a full filter
                            statement i.e. dataframe.field.filter. If no filter is required, None should be supplied.
        case_column      -- list: column names for groupby and pivot_table methods, ba, tpa and qm dbh will be calculated
                            for each case in this column

    Details: filter statement should not be a string, rather just the pandas dataframe filter statement:
    for live trees use: ~tree_table.TR_HLTH.isin(["D", "DEAD"])
    for dead trees use: tree_table.TR_HLTH.isin(["D", "DEAD"])
    if no filter is required, None should be passed in as the keyword argument.
    """
    # Check input parameters are valid
    assert isinstance(tree_table, pd.DataFrame), "must be a pandas DataFrame"
    assert tree_table.columns.isin(case_columns).any(), "df must contain column specified as group column param"
    assert tree_table.columns.isin(["PID"]).any(), "df must contain column PID"

    # Create data frame that preserves unfiltered count of plots by level
    plotcount_df = tree_table \
        .groupby('PID', as_index=False) \
        .agg(plot_count=('PID', agg_plot_count)) \
        .set_index('PID')

    # Add level to case columns
    case_columns.insert(0, 'PID')

    # Test for filter statement and run script based on filter or no filter
    if filter_statement is not None:

        # Filter, group and sum tree table
        filtered_df = tree_table[filter_statement] \
            .groupby(by=case_columns, as_index=False) \
            .agg(
                Tree_Count=('TR_SP', agg_tree_count),
                Plot_Count=('PID', agg_plot_count),
                TPA=('TR_DENS', sum),
                BA=('TR_BA', sum)
            )

        # Add and Calculate QM DBH
        filtered_df['QM_DBH'] = np.where(filtered_df['Tree_Count'] > 0,
                                         (np.sqrt((filtered_df['BA'] / filtered_df['TPA']) / 0.005454154)),
                                         0)

        # Join results back to full set of PIDs
        out_df = plotcount_df \
            .drop(columns=['Plot_Count']) \
            .merge(right=filtered_df,
                   how='inner',
                   on='PID') \
            .reset_index()

        # Set dtypes
        out_df = out_df.astype({'TPA': 'float64', 'QM_DBH': 'float64'})\
                       .fillna(value={'QM_DBH': 0})\
                       .drop(columns=['index'])

        return out_df

    elif filter_statement is None:

        # Group and sum tree table
        filtered_df = tree_table \
            .groupby(by=case_columns, as_index=False) \
            .agg(
                Tree_Count=('TR_SP', agg_tree_count),
                Plot_Count=('PID', agg_plot_count),
                TPA=('TR_DENS', sum),
                BA=('TR_BA', sum)
            )

        # Add and Calculate QM DBH
        filtered_df['QM_DBH'] = np.where(filtered_df['Tree_Count'] > 0,
                                         (np.sqrt((filtered_df['BA'] / filtered_df['TPA']) / 0.005454154)),
                                         0)

        # Join results back to full set of PIDs
        out_df = plotcount_df \
            .drop(columns=['plot_count']) \
            .merge(right=filtered_df,
                   how='inner',
                   on='PID') \
            .reset_index()

        # Set dtypes
        out_df = out_df.astype({'TPA': 'float64', 'QM_DBH': 'float64'})\
                       .fillna(value={'QM_DBH': 0})\
                       .drop(columns=['index'])

        return out_df


# Generate TPA, BA, QM DBH at non-PID levels
def tpa_ba_qmdbh_level(tree_table, filter_statement, level):
    """Creates a dataframe with BA, TPA and QM DBH columns at a specified level based on the provided filter.

    Keyword Args:
        tree_table       -- dataframe: input tree_table, produced by the create_tree_table function
        filter_statement -- pandas method: filter statement to be used on the input dataframe, should be a full filter
                            statement i.e. dataframe.field.filter. If no filter is required, None should be supplied.
        level            -- string: field name for desired FMG level, i.e. SID, SITE, UNIT

    Details: filter statement should not be a string, rather just the pandas dataframe filter statement:
    for live trees use: ~tree_table.TR_HLTH.isin(["D", "DEAD"])
    for dead trees use: tree_table.TR_HLTH.isin(["D", "DEAD"])
    if no filter is required, None should be passed in as the keyword argument.
    """

    # Check input parameters are valid
    assert isinstance(tree_table, pd.DataFrame), "must be a pandas DataFrame"
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
            .groupby([level], as_index=False) \
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
        filtered_df['QM_DBH'] = np.where(filtered_df['tree_count'] > 0,
                                         (np.sqrt((filtered_df['BA'] / filtered_df['TPA']) / 0.005454154)),
                                         0)

        # Set index for merge
        filtered_df.set_index(level)

        # Join results back to full set of level polygons and fill nans with 0
        out_df = plotcount_df \
            .drop(columns=['plot_count']) \
            .merge(right=filtered_df,
                   how='left',
                   on=level) \
            .fillna(0) \
            .reset_index()

        return out_df

    elif filter_statement is None:

        # Group and sum tree table
        filtered_df = tree_table \
            .groupby([level], as_index=False) \
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
        filtered_df['QM_DBH'] = np.where(filtered_df['tree_count'] > 0,
                                         (np.sqrt((filtered_df['BA'] / filtered_df['TPA']) / 0.005454154)),
                                         0)

        # Set index for merge
        filtered_df.set_index(level)

        # Join results back to full set of level polygons and fill nan with 0
        out_df = plotcount_df \
            .drop(columns=['plot_count']) \
            .merge(right=filtered_df,
                   how='left',
                   on=level) \
            .fillna(0) \
            .reset_index()

        return out_df


# Generate TPA, BA, QM DBH given a case field at non-PID levels (pivots on case field to wide)
def tpa_ba_qmdbh_level_by_case(tree_table, filter_statement, case_column, level):
    """Creates a dataframe with BA, TPA and QM DBH columns at a specified level. The function pivots on the
    case column supplied resulting in BA, TPA and QM DBH columns for each category in the case column.
    For example, if mast_type is specified as the case column BA, TPA and QM DBH will be calculated for
    each mast type for each level polygon - ba_hard, ba_lightseed, ba_soft, etc.

    Keyword Args:
        tree_table       -- dataframe: input tree_table, produced by the create_tree_table function
        filter_statement -- pandas method: filter statement to be used on the input dataframe, should be a full filter
                            statement i.e. dataframe.field.filter. If no filter is required, None should be supplied.
        case_column     -- string: field name for groupby and pivot_table methods, ba, tpa and qm dbh will be
                            calculated for each category in this field
        level            -- string: field name for desired FMG level, i.e. SID, SITE, UNIT

    Details: filter statement should not be a string, rather just the pandas dataframe filter statement:
    for live trees use: ~tree_table.TR_HLTH.isin(["D", "DEAD"])
    for dead trees use: tree_table.TR_HLTH.isin(["D", "DEAD"])
    if no filter is required, None should be passed in as the keyword argument.
    """

    # Check input parameters are valid
    assert isinstance(tree_table, pd.DataFrame), "must be a pandas DataFrame"
    assert tree_table.columns.isin([case_column]).any(), "df must contain column specified as group column param"
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
            .groupby([level, case_column], as_index=False) \
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
        filtered_df['QM_DBH'] = np.where(filtered_df['tree_count'] > 0,
                                         (np.sqrt((filtered_df['BA'] / filtered_df['TPA']) / 0.005454154)),
                                         0)

        # Pivot sizes and metrics to columns
        pivot_df = filtered_df \
            .pivot_table(
                index=level,
                columns=case_column,
                values=['BA', 'TPA', 'QM_DBH'],
                fill_value=0) \
            .reset_index()

        # flatten column to multi index
        pivot_df.columns = list(map(str("_" + case_column + "_").join, pivot_df.columns))
        fixpivot_df = pivot_df.rename(columns={str(level + "_" + case_column + "_"): level}).set_index(level)

        # Join results back to full set of level polygons and fill nans with 0
        out_df = plotcount_df \
            .drop(columns=['plot_count']) \
            .merge(right=fixpivot_df,
                   how='left',
                   on=level) \
            .fillna(0) \
            .reset_index()

        return out_df

    elif filter_statement is None:

        # Group and sum tree table
        filtered_df = tree_table \
            .groupby([level, case_column], as_index=False) \
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
        filtered_df['QM_DBH'] = np.where(filtered_df['tree_count'] > 0,
                                         (np.sqrt((filtered_df['BA'] / filtered_df['TPA']) / 0.005454154)),
                                         0)

        # Pivot sizes and metrics to columns
        pivot_df = filtered_df \
            .pivot_table(
                index=level,
                columns=case_column,
                values=['BA', 'TPA', 'QM_DBH'],
                fill_value=0) \
            .reset_index()

        # flatten column to multi index
        pivot_df.columns = list(map(str("_" + case_column + "_").join, pivot_df.columns))
        fixpivot_df = pivot_df.rename(columns={str(level + "_" + case_column + "_"): level}).set_index(level)

        # Join results back to full set of level polygons and fill nan with 0
        out_df = plotcount_df \
            .drop(columns=['plot_count']) \
            .merge(right=fixpivot_df,
                   how='left',
                   on=level) \
            .fillna(0) \
            .reset_index()

        return out_df


# Generate TPA, BA, QM DBH given a case field at non-PID level (no pivot, stays long)
def tpa_ba_qmdbh_level_by_case_long(tree_table, filter_statement, case_column, level):
    """Creates a dataframe with BA, TPA and QM DBH columns at a specified level. The function does not pivot
    on the case field, instead leaving it in long form. Each row of the resulting dataframe will be a single
    instance of a level and case, with just 3 columns for TPA, BA and QMDBH

    Keyword Args:
        tree_table       -- dataframe: input tree_table, produced by the create_tree_table function
        filter_statement -- pandas method: filter statement to be used on the input dataframe, should be a full filter
                            statement i.e. dataframe.field.filter. If no filter is required, None should be supplied.
        case_column      -- string: field name for groupby  method, ba, tpa and qm dbh will be
                            calculated for each category in this field
        level            -- string: field name for desired FMG level, i.e. SID, SITE, UNIT

    Details: filter statement should not be a string, rather just the pandas dataframe filter statement:
    for live trees use: ~tree_table.TR_HLTH.isin(["D", "DEAD"])
    for dead trees use: tree_table.TR_HLTH.isin(["D", "DEAD"])
    if no filter is required, None should be passed in as the keyword argument.
    """

    # Check input parameters are valid
    assert isinstance(tree_table, pd.DataFrame), "must be a pandas DataFrame"
    assert tree_table.columns.isin([case_column]).any(), "df must contain column specified as group column param"
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
            .groupby([level, case_column], as_index=False) \
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
        filtered_df['QM_DBH'] = np.where(filtered_df['tree_count'] > 0,
                                         (np.sqrt((filtered_df['BA'] / filtered_df['TPA']) / 0.005454154)),
                                         0)

        # Join results back to full set of level polygons
        out_df = plotcount_df \
            .drop(columns=['plot_count']) \
            .merge(right=filtered_df,
                   how='inner',
                   on=level) \
            .reset_index()

        return out_df

    elif filter_statement is None:

        # Group and sum tree table
        filtered_df = tree_table \
            .groupby([level, case_column], as_index=False) \
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
        filtered_df['QM_DBH'] = np.where(filtered_df['tree_count'] > 0,
                                         (np.sqrt((filtered_df['BA'] / filtered_df['TPA']) / 0.005454154)),
                                         0)

        # Join results back to full set of level polygons and fill nan with 0
        out_df = plotcount_df \
            .drop(columns=['plot_count']) \
            .merge(right=filtered_df,
                   how='left',
                   on=level) \
            .reset_index()

        return out_df


# Generate TPA, BA, QM DBH given a case field at non-PID level (no pivot, stays long)
def tpa_ba_qmdbh_level_by_multi_case_long(tree_table, filter_statement, case_columns, level):
    """Creates a dataframe with BA, TPA and QM DBH columns at a specified level. The function does not pivot
    on the case field, instead leaving it in long form. Each row of the resulting dataframe will be a single
    instance of a level and case, with just 3 columns for TPA, BA and QMDBH

    Keyword Args:
        tree_table       -- dataframe: input tree_table, produced by the create_tree_table function
        filter_statement -- pandas method: filter statement to be used on the input dataframe, should be a full filter
                            statement i.e. dataframe.field.filter. If no filter is required, None should be supplied.
        case_column      -- string: field name for groupby  method, ba, tpa and qm dbh will be
                            calculated for each category in this field
        level            -- string: field name for desired FMG level, i.e. SID, SITE, UNIT

    Details: filter statement should not be a string, rather just the pandas dataframe filter statement:
    for live trees use: ~tree_table.TR_HLTH.isin(["D", "DEAD"])
    for dead trees use: tree_table.TR_HLTH.isin(["D", "DEAD"])
    if no filter is required, None should be passed in as the keyword argument.
    """

    # Check input parameters are valid
    assert isinstance(tree_table, pd.DataFrame), "must be a pandas DataFrame"
    assert tree_table.columns.isin(case_columns).any(), "df must contain column specified as group column param"
    assert tree_table.columns.isin([level]).any(), "df must contain column specified as level param"

    # Create data frame that preserves unfiltered count of plots by level
    plotcount_df = tree_table \
        .groupby(level, as_index=False) \
        .agg(Plot_Count=('PID', agg_plot_count)) \
        .set_index(level)

    # Add level to case columns
    case_columns.insert(0, level)

    # Test for filter statement and run script based on filter or no filter
    if filter_statement is not None:

        # Filter, group and sum tree table, add unfiltered plot count field
        filtered_df = tree_table[filter_statement] \
            .groupby(by=case_columns, as_index=False) \
            .agg(
            Tree_Count=('TR_SP', agg_tree_count),
            Stand_Dens=('TR_DENS', sum)
        ) \
            .set_index(level) \
            .merge(right=plotcount_df,
                   how='left',
                   on=level) \
            .reset_index()

        # Add and calculate TPA, BA, QM_DBH
        baf = 10
        filtered_df['TPA'] = filtered_df['Stand_Dens'] / filtered_df['Plot_Count']
        filtered_df['BA'] = (filtered_df['Tree_Count'] * baf) / filtered_df['Plot_Count']
        filtered_df['QM_DBH'] = np.where(filtered_df['Tree_Count'] > 0,
                                         (np.sqrt((filtered_df['BA'] / filtered_df['TPA']) / 0.005454154)),
                                         0)

        # Join results back to full set of level polygons
        out_df = plotcount_df \
            .drop(columns=['Plot_Count']) \
            .merge(right=filtered_df,
                   how='inner',
                   on=level) \
            .reset_index()

        # Handle Dtypes
        out_df = out_df.astype({'TPA': 'float64', 'QM_DBH': 'float64'})\
                       .fillna(value={'QM_DBH': 0})\
                       .drop(columns=['index'])

        return out_df

    elif filter_statement is None:

        # Group and sum tree table
        filtered_df = tree_table \
            .groupby(by=case_columns, as_index=False) \
            .agg(
                Tree_Count=('TR_SP', agg_tree_count),
                Stand_Dens=('TR_DENS', sum),
            ) \
            .set_index(level) \
            .merge(right=plotcount_df,
                   how='left',
                   on=level) \
            .reset_index()

        # Add and calculate TPA, BA, QM_DBH
        baf = 10
        filtered_df['TPA'] = filtered_df['Stand_Dens'] / filtered_df['Plot_Count']
        filtered_df['BA'] = (filtered_df['Tree_Count'] * baf) / filtered_df['Plot_Count']
        filtered_df['QM_DBH'] = np.where(filtered_df['Tree_Count'] > 0,
                                         (np.sqrt((filtered_df['BA'] / filtered_df['TPA']) / 0.005454154)),
                                         0)

        # Join results back to full set of level polygons and fill nan with 0
        out_df = plotcount_df \
            .drop(columns=['Plot_Count'])\
            .merge(right=filtered_df,
                   how='left',
                   on=level) \
            .reset_index()

        # Handle dtypes
        out_df = out_df.astype({'TPA': 'float64', 'QM_DBH': 'float64'})\
                       .fillna(value={'QM_DBH': 0})\
                       .drop(columns=['index'])

        return out_df


# Generate dominate health and percent composition for plot summaries
def health_dom_plot(tree_table, filter_statement):
    """Creates a dataframe with most dominant health and percentage of total that health category comprises
     for the plot level - these metrics are based on TPA for each health category and the subset of trees defined
     by the filter statement.
     The function will accept and apply a filter to determine health prevalence for specific subsets of trees.

    Keyword Args:
        tree_table       -- dataframe: input tree_table, produced by the create_tree_table function
        filter_statement -- pandas method: filter statement to be used on the input dataframe, should be a full filter
                            statement i.e. dataframe.field.filter. If no filter is required, None should be supplied.

    Details: filter statement should not be a string, rather just the pandas dataframe filter statement:
    for live trees use: ~tree_table.TR_HLTH.isin(["D", "DEAD"])
    for dead trees use: tree_table.TR_HLTH.isin(["D", "DEAD"])
    if no filter is required, None should be passed in as the keyword argument.
    """
    # Create DF with filtered TPA at specified level, ignoring health categories
    # TPA from this step will be used to calculate the prevalence percent
    unfilt_tpa_df = tpa_ba_qmdbh_plot(
        tree_table=tree_table,
        filter_statement=filter_statement)

    unfilt_tpa_df = unfilt_tpa_df \
        .drop(
            columns=['index',
                     'tree_count',
                     'plot_count',
                     'BA',
                     'QM_DBH']) \
        .rename(columns={'TPA': 'OVERALL_TPA'}) \
        .set_index('PID')

    # Create DF with filtered TPA
    health_base_df = tpa_ba_qmdbh_plot_by_case_long(
        tree_table=tree_table,
        filter_statement=filter_statement,
        case_column='TR_HLTH')

    # Create DF with max TPA for each level
    health_max_df = health_base_df \
        .groupby('PID') \
        .agg(TPA=('TPA', 'max')) \
        .reset_index()

    # Join max df back to filtered base df on compound key level, TPA
    # The resulting dataframe contains health codes by max tpa, with some edge cases
    health_join_df = health_base_df \
        .merge(
            right=health_max_df,
            how='inner',
            left_on=['PID', 'TPA'],
            right_on=['PID', 'TPA']) \
        .reset_index()

    # Edge cases are where TPAs may be identical between health ratings within a level
    # i.e. level 123 has a health rating of H with a TPA of 5 and S with a TPA of 5.
    # To deal with these cases  we assign a numeric code to each health category, sort the resulting
    # dataframe by those numeric codes then drop duplicate rows by level, keeping the first if duplicates
    # are present. This results in a data frame of most prevalent health, wighted toward the healthiest
    # switching the sort method would result in a data frame of most prevalent health, weighted toward
    # the least healthy

    # Assign Numeric codes to health categories
    health_join_df['TR_HLTH_NUM'] = health_join_df['TR_HLTH'].map(health_rank_map)

    # Sort dataframe by numeric ranking codes
    health_dom_df = health_join_df \
        .sort_values(
            by=['PID', 'TR_HLTH_NUM'])

    # Drop duplicate rows, keeping the first row
    health_dom_df = health_dom_df \
        .drop_duplicates(
            subset='PID',
            keep='first')

    # Rename tpa column and prep for join
    health_dom_df = health_dom_df \
        .rename(columns={'TPA': 'HLTH_TPA'}) \
        .set_index('PID')

    # Join overall TPA to health prevalence table to calculate prevalence percentage
    health_dom_pct_df = health_dom_df \
        .join(
            other=unfilt_tpa_df,
            how='left')

    # Calculate prevalence percentage column
    health_dom_pct_df['HLTH_DOM_PCMP'] = (health_dom_pct_df['HLTH_TPA'] / health_dom_pct_df['OVERALL_TPA']) * 100

    # Clean up dataframe for export
    health_dom_pct_df = health_dom_pct_df \
        .drop(columns=['level_0',
                       'index',
                       'tree_count',
                       'plot_count',
                       'BA',
                       'QM_DBH',
                       'TR_HLTH_NUM',
                       'HLTH_TPA',
                       'OVERALL_TPA']) \
        .rename(columns={'TR_HLTH': 'HLTH_DOM'}) \
        .astype({'HLTH_DOM_PCMP': 'float64'}) \
        .reset_index()

    return health_dom_pct_df


# Generate dominate health and percent composition for level summaries
def health_dom_level(tree_table, filter_statement, level):
    """Creates a dataframe with dominant health and percentage of total that health category comprises
     for specified level - these metrics are based on TPA for each health category and the subset of trees defined
     by the filter statement.
     The function will accept and apply a filter to determine health prevalence for specific subsets of trees.

    Keyword Args:
        tree_table       -- dataframe: input tree_table, produced by the create_tree_table function
        filter_statement -- pandas method: filter statement to be used on the input dataframe, should be a full filter
                            statement i.e. dataframe.field.filter. If no filter is required, None should be supplied.
        level            -- string: field name for desired FMG level, i.e. SID, SITE, UNIT

    Details: filter statement should not be a string, rather just the pandas dataframe filter statement:
    for live trees use: ~tree_table.TR_HLTH.isin(["D", "DEAD"])
    for dead trees use: tree_table.TR_HLTH.isin(["D", "DEAD"])
    if no filter is required, None should be passed in as the keyword argument.
    """
    # Create DF with filtered TPA at specified level, ignoring health categories
    # TPA from this step will be used to calculate the prevalence percent
    unfilt_tpa_df = tpa_ba_qmdbh_level(
        tree_table=tree_table,
        filter_statement=filter_statement,
        level=level)

    unfilt_tpa_df = unfilt_tpa_df \
        .drop(
            columns=['index',
                     'tree_count',
                     'stand_dens',
                     'plot_count',
                     'BA',
                     'QM_DBH']) \
        .rename(columns={'TPA': 'OVERALL_TPA'}) \
        .set_index(level)

    # Create DF with filtered TPA by health category
    health_base_df = tpa_ba_qmdbh_level_by_case_long(
        tree_table=tree_table,
        filter_statement=filter_statement,
        case_column='TR_HLTH',
        level=level)

    # Create DF with max TPA for each level
    health_max_df = health_base_df \
        .groupby(level) \
        .agg(TPA=('TPA', 'max')) \
        .reset_index()

    # Join max df back to filtered base df on compound key: level, TPA
    # The resulting dataframe contains health codes by max tpa, with some edge cases
    health_join_df = health_base_df \
        .merge(
            right=health_max_df,
            how='inner',
            left_on=[level, 'TPA'],
            right_on=[level, 'TPA']) \
        .reset_index()

    # Edge cases are where TPAs may be identical between health ratings within a level
    # i.e. level 123 has a health rating of H with a TPA of 5 and S with a TPA of 5.
    # To deal with these cases  we assign a numeric code to each health category, sort the resulting
    # dataframe by those numeric codes then drop duplicate rows by level, keeping the first if duplicates
    # are present. This results in a data frame of most prevalent health, wighted toward the healthiest
    # switching the sort method would result in a data frame of most prevalent health, weighted toward
    # the least healthy

    # Assign numeric ranking codes to each health category
    health_join_df['TR_HLTH_NUM'] = health_join_df['TR_HLTH'].map(health_rank_map)

    # Sort dataframe by numeric ranking codes
    health_dom_df = health_join_df \
        .sort_values(
            by=[level, 'TR_HLTH_NUM'])

    # Drop duplicate rows, keeping the first row
    health_dom_df = health_dom_df \
        .drop_duplicates(
            subset=level,
            keep='first')

    # Rename tpa column and prep for join
    health_dom_df = health_dom_df \
        .rename(columns={'TPA': 'HLTH_TPA'}) \
        .set_index(level)

    # Join overall TPA to health prevalence table to calculate prevalence percentage
    health_dom_pct_df = health_dom_df \
        .join(
            other=unfilt_tpa_df,
            how='left')

    # Calculate prevalence percentage column
    health_dom_pct_df['HLTH_DOM_PCMP'] = (health_dom_pct_df['HLTH_TPA'] / health_dom_pct_df['OVERALL_TPA']) * 100

    # Clean up dataframe for export
    health_dom_pct_df = health_dom_pct_df \
        .drop(columns=['level_0',
                       'index',
                       'tree_count',
                       'stand_dens',
                       'plot_count',
                       'BA',
                       'QM_DBH',
                       'TR_HLTH_NUM',
                       'HLTH_TPA',
                       'OVERALL_TPA']) \
        .rename(columns={'TR_HLTH': 'HLTH_DOM'}) \
        .astype({'HLTH_DOM_PCMP': 'float64'}) \
        .reset_index()

    return health_dom_pct_df


# Generate dominant health percent composition for plot summaries
def species_dom_plot(tree_table, filter_statement):
    """Creates a dataframe with dominant species and percentage of total that species comprises
     for the plot level - these metrics are based on TPA for each species and the subset of trees defined
     by the filter statement.
     The function will accept and apply a filter to determine health prevalence for specific subsets of trees.

    Keyword Args:
        tree_table       -- dataframe: input tree_table, produced by the create_tree_table function
        filter_statement -- pandas method: filter statement to be used on the input dataframe, should be a full filter
                            statement i.e. dataframe.field.filter. If no filter is required, None should be supplied.

    Details: filter statement should not be a string, rather just the pandas dataframe filter statement:
    for live trees use: ~tree_table.TR_HLTH.isin(["D", "DEAD"])
    for dead trees use: tree_table.TR_HLTH.isin(["D", "DEAD"])
    if no filter is required, None should be passed in as the keyword argument.
    """
    # Create DF with filtered TPA at specified level, ignoring health categories
    # TPA from this step will be used to calculate the percent composition
    unfilt_tpa_df = tpa_ba_qmdbh_plot(
        tree_table=tree_table,
        filter_statement=filter_statement)

    unfilt_tpa_df = unfilt_tpa_df \
        .drop(
            columns=['index',
                     'tree_count',
                     'plot_count',
                     'BA',
                     'QM_DBH']) \
        .rename(columns={'TPA': 'OVERALL_TPA'}) \
        .set_index('PID')

    # Create DF with filtered TPA
    species_base_df = tpa_ba_qmdbh_plot_by_case_long(
        tree_table=tree_table,
        filter_statement=filter_statement,
        case_column='TR_SP')

    # Create DF with max TPA for each level
    species_max_df = species_base_df \
        .groupby('PID') \
        .agg(TPA=('TPA', 'max')) \
        .reset_index()

    # Join max df back to filtered base df on compound key level, TPA
    # The resulting dataframe contains health codes by max tpa, with some edge cases
    species_join_df = species_base_df \
        .merge(
            right=species_max_df,
            how='inner',
            left_on=['PID', 'TPA'],
            right_on=['PID', 'TPA']) \
        .reset_index()

    # Edge cases are where TPAs may be identical between species within a plot
    # i.e. plot 123 has ASCA2 with a TPA of 5 and BENI with a TPA of 5. To deal
    # with these cases the data frame will be sorted by plot and alphabetically
    # descending on species code. The first row for each level will be kept and the
    # other rows dropped. This results in a dataframe weighted toward species codes
    # that occur at the beginning of the alphabet, functionally this will weight the
    # results toward ASCA2 (silver maple)

    # Sort dataframe by numeric ranking codes
    species_dom_df = species_join_df \
        .sort_values(
            by=['PID', 'TR_SP'])

    # Drop duplicate rows, keeping the first row
    species_dom_df = species_dom_df \
        .drop_duplicates(
            subset='PID',
            keep='first')

    # Rename tpa column and prep for join
    species_dom_df = species_dom_df \
        .rename(columns={'TPA': 'SP_TPA'}) \
        .set_index('PID')

    # Join overall TPA to dominant health table to calculate percent composition
    species_dom_pct_df = species_dom_df \
        .join(
            other=unfilt_tpa_df,
            how='left')

    # Calculate percent composition column
    species_dom_pct_df['SP_DOM_PCMP'] = (species_dom_pct_df['SP_TPA'] / species_dom_pct_df['OVERALL_TPA']) * 100

    # Clean up dataframe for export
    species_dom_pct_df = species_dom_pct_df \
        .drop(columns=['level_0',
                       'index',
                       'tree_count',
                       'plot_count',
                       'BA',
                       'QM_DBH',
                       'SP_TPA',
                       'OVERALL_TPA']) \
        .rename(columns={'TR_SP': 'SP_DOM'}) \
        .reset_index()

    return species_dom_pct_df


# Generate dominant species percent composition for level summaries
def species_dom_level(tree_table, filter_statement, level):
    """Creates a dataframe with dominant species and percentage of total that species category comprises
     for specified level - these metrics are based on TPA for each species and the subset of trees defined
     by the filter statement.
     The function will accept and apply a filter to determine health prevalence for specific subsets of trees.

    Keyword Args:
        tree_table       -- dataframe: input tree_table, produced by the create_tree_table function
        filter_statement -- pandas method: filter statement to be used on the input dataframe, should be a full filter
                            statement i.e. dataframe.field.filter. If no filter is required, None should be supplied.
        level            -- string: field name for desired FMG level, i.e. SID, SITE, UNIT

    Details: filter statement should not be a string, rather just the pandas dataframe filter statement:
    for live trees use: ~tree_table.TR_HLTH.isin(["D", "DEAD"])
    for dead trees use: tree_table.TR_HLTH.isin(["D", "DEAD"])
    if no filter is required, None should be passed in as the keyword argument.
    """

    # Create DF with filtered TPA at specified level, ignoring species
    # TPA from this step will be used to calculate the dominance percent composition
    unfilt_tpa_df = tpa_ba_qmdbh_level(
        tree_table=tree_table,
        filter_statement=filter_statement,
        level=level)

    unfilt_tpa_df = unfilt_tpa_df \
        .drop(
            columns=['index',
                     'tree_count',
                     'stand_dens',
                     'plot_count',
                     'BA',
                     'QM_DBH']) \
        .rename(columns={'TPA': 'OVERALL_TPA'}) \
        .set_index(level)

    # Create DF with filtered TPA
    species_base_df = tpa_ba_qmdbh_level_by_case_long(
        tree_table=tree_table,
        filter_statement=filter_statement,
        case_column='TR_SP',
        level=level)

    # Create DF with max TPA for each level
    species_max_df = species_base_df \
        .groupby(level) \
        .agg(TPA=('TPA', 'max')) \
        .reset_index()

    # Join max df back to filtered base df on compound key level, TPA
    # The resulting dataframe contains species by max tpa, with some edge cases
    species_join_df = species_base_df \
        .merge(
            right=species_max_df,
            how='inner',
            left_on=[level, 'TPA'],
            right_on=[level, 'TPA']) \
        .reset_index()

    # Edge cases are where TPAs may be identical between species within a  level
    # i.e. level 123 has ASCA2 with a TPA of 5 and BENI with a TPA of 5. To deal
    # with these cases the data frame will be sorted by level and alphabetically
    # descending on species code. The first row for each level will be kept and the
    # other rows dropped. This results in a dataframe weighted toward species codes
    # that occur at the beginning of the alphabet, functionally this will weight the
    # results toward ASCA2 (silver maple)

    # Sort dataframe by level and species
    species_dom_df = species_join_df \
        .sort_values(
            by=[level, 'TR_SP'])

    # Drop duplicate rows, keeping the first row
    species_dom_df = species_dom_df \
        .drop_duplicates(
            subset=level,
            keep='first')

    # Rename tpa column and prep for join
    species_dom_df = species_dom_df \
        .rename(columns={'TPA': 'SP_TPA'}) \
        .set_index(level)

    # Join overall TPA to species dominance table to calculate percent composition
    species_dom_pct_df = species_dom_df \
        .join(
            other=unfilt_tpa_df,
            how='left')

    # Calculate percent composition column
    species_dom_pct_df['SP_DOM_PCMP'] = (species_dom_pct_df['SP_TPA'] / species_dom_pct_df['OVERALL_TPA']) * 100

    # Clean up dataframe for export
    species_dom_pct_df = species_dom_pct_df \
        .drop(columns=['level_0',
                       'index',
                       'tree_count',
                       'stand_dens',
                       'plot_count',
                       'BA',
                       'QM_DBH',
                       'OVERALL_TPA',
                       'SP_TPA']) \
        .rename(columns={'TR_SP': 'SP_DOM'}) \
        .reset_index()

    return species_dom_pct_df


# Determine top 5 overstory species and generate associated statistics for level summaries
def top5_ov_species_level(tree_table, level):
    """ Creates a dataframe with the top 5 overstory species and associated statistics (BA, TPA, QM DBH, Dom. Health,
    Dom. Health % Composition, Dom. Health TPA, and Dead TPA) for each of the top 5 species

    Keyword Args:
          tree_table -- dataframe: input tree_table, produced by create_tree_table function
          level      -- string: field name for desired FMG level, i.e. SID, SITE, UNIT

    Details: None
    """
    # Create table with TPA for each unique species per given level
    species_df = tpa_ba_qmdbh_level_by_case_long(tree_table=tree_table,
                                                 filter_statement=None,
                                                 case_column='TR_SP',
                                                 level=level)

    # Remove rows with a tree species of None or NoTree
    species_df = species_df[species_df.TR_SP != "NONE"]

    # Sort species_df by level and TPA
    species_df = species_df.sort_values(by=[level, 'TPA'], ascending=False)

    # Rank each species within a single level group, based on sort
    species_df['SP_RANK'] = species_df.groupby([level]).cumcount().add(1)

    # Filter on keep species rank where the value is less than or equal to 5
    species_df = species_df[species_df.SP_RANK <= 5]

    # Assign categorical variable for species rank to assist in pivot column naming
    species_df['OV_SP_RANK'] = species_df['SP_RANK'].map(overstory_sp_map)

    # Pivot variables based on sp rank field
    species_pivot_df2 = species_df.pivot(index=level, columns='OV_SP_RANK', values=['TR_SP', 'BA', 'TPA', 'QM_DBH'])

    # flatten multi index and rename columns
    species_pivot_df2.columns = ['_'.join(col) for col in species_pivot_df2.columns.values]

    # reset index
    species_pivot_df2 = species_pivot_df2\
        .reset_index()\
        .infer_objects()

    # Rename columns
    ov_species = species_pivot_df2 \
        .rename(columns={
                'TR_SP_OV_SP1': 'OV_SP1',
                'BA_OV_SP1': 'OV_SP1_BA',
                'TPA_OV_SP1': 'OV_SP1_TPA',
                'QM_DBH_OV_SP1': 'OV_SP1_QMDBH',
                'TR_SP_OV_SP2': 'OV_SP2',
                'BA_OV_SP2': 'OV_SP2_BA',
                'TPA_OV_SP2': 'OV_SP2_TPA',
                'QM_DBH_OV_SP2': 'OV_SP2_QMDBH',
                'TR_SP_OV_SP3': 'OV_SP3',
                'BA_OV_SP3': 'OV_SP3_BA',
                'TPA_OV_SP3': 'OV_SP3_TPA',
                'QM_DBH_OV_SP3': 'OV_SP3_QMDBH',
                'TR_SP_OV_SP4': 'OV_SP4',
                'BA_OV_SP4': 'OV_SP4_BA',
                'TPA_OV_SP4': 'OV_SP4_TPA',
                'QM_DBH_OV_SP4': 'OV_SP4_QMDBH',
                'TR_SP_OV_SP5': 'OV_SP5',
                'BA_OV_SP5': 'OV_SP5_BA',
                'TPA_OV_SP5': 'OV_SP5_TPA',
                'QM_DBH_OV_SP5': 'OV_SP5_QMDBH'})

    # Create iterator dict for sp 1-5
    species_columns = ['OV_SP1', 'OV_SP2', 'OV_SP3', 'OV_SP4', 'OV_SP5']
    iterator_lists = []
    for sp in species_columns:
        # filter out nan values
        ov_species_filtered = ov_species.dropna(subset=[sp])

        # Convert filtered df to a list of lists
        iterator = ov_species_filtered[[level, sp]].values.tolist()

        # Append list to the iterator list
        iterator_lists.append(iterator)

    # Convert iterator list to dict so lists can be accessed by species rank
    iterator_dict = dict(zip(species_columns, iterator_lists))

    # iterate through the dict doing a bunch of stuff
    for key, value in iterator_dict.items():

        # Create empty list to hold results of loop
        health_dom_list = []

        # Iterate through value list
        for item in value:

            # filter tree table to a single stand
            tree_table_level = tree_table.loc[tree_table[level] == item[0]]

            # Run health prev level function with single stand associated species
            health_dom_level_df = health_dom_level(tree_table=tree_table_level,
                                                   filter_statement=tree_table_level['TR_SP'] == item[1],
                                                   level=level)

            # Convert dataframe to list - contains level, dom health, % comp
            health_dom_level_list = health_dom_level_df.values.tolist()[0]

            # Calculate TPA for just dom health trees
            dom_hlth_tpa = tpa_ba_qmdbh_level(tree_table=tree_table_level,
                                              filter_statement=
                                              (tree_table_level['TR_HLTH'] == health_dom_level_list[1]) &
                                              (tree_table_level['TR_SP'] == item[1]),
                                              level=level)

            # Convert dom health tpa dataframe to list and insert into dom health list
            if len(dom_hlth_tpa.index) == 0:
                health_dom_level_list.insert(3, 0)
            else:
                dom_hlth_tpa_list = dom_hlth_tpa.values.tolist()[0]
                health_dom_level_list.insert(3, dom_hlth_tpa_list[5])

            # Calcualte TPA for just dead trees
            dead_hlth_tpa = tpa_ba_qmdbh_level(tree_table=tree_table_level,
                                               filter_statement=(tree_table_level['TR_HLTH'] == 'D') &
                                                                (tree_table_level['TR_SP'] == item[1]),
                                               level=level)

            # Convert dead health tpa dataframe to list
            if len(dead_hlth_tpa.index) == 0:
                health_dom_level_list.insert(4, 0)
            else:
                dead_hlth_tpa_list = dead_hlth_tpa.values.tolist()[0]
                health_dom_level_list.insert(4, dead_hlth_tpa_list[5])

            # Add health prev list to loop result list
            health_dom_list.append(health_dom_level_list)

        # convert loop result list to dataframe
        health_dom_ovsp = pd.DataFrame(health_dom_list, columns=[level,
                                                                 key+'_DOM_HLTH',
                                                                 key+'_DOM_HLTH_PCMP',
                                                                 key+'_DOM_HLTH_TPA',
                                                                 key+'_D_TPA'])

        # Join dataframe to OV_SPECIES dataframe
        ov_species = ov_species.set_index(level).join(health_dom_ovsp.set_index(level), how='left')
        ov_species = ov_species.reset_index()

    # Re order columns
    ov_species = ov_species.reindex([level,
                                     'OV_SP1', 'OV_SP1_BA', 'OV_SP1_TPA', 'OV_SP1_QMDBH',
                                     'OV_SP1_DOM_HLTH', 'OV_SP1_DOM_HLTH_PCMP', 'OV_SP1_DOM_HLTH_TPA', 'OV_SP1_D_TPA',
                                     'OV_SP2', 'OV_SP2_BA', 'OV_SP2_TPA', 'OV_SP2_QMDBH',
                                     'OV_SP2_DOM_HLTH', 'OV_SP2_DOM_HLTH_PCMP', 'OV_SP2_DOM_HLTH_TPA', 'OV_SP2_D_TPA',
                                     'OV_SP3', 'OV_SP3_BA', 'OV_SP3_TPA', 'OV_SP3_QMDBH',
                                     'OV_SP3_DOM_HLTH', 'OV_SP3_DOM_HLTH_PCMP', 'OV_SP3_DOM_HLTH_TPA', 'OV_SP3_D_TPA',
                                     'OV_SP4', 'OV_SP4_BA', 'OV_SP4_TPA', 'OV_SP4_QMDBH',
                                     'OV_SP4_DOM_HLTH', 'OV_SP4_DOM_HLTH_PCMP', 'OV_SP4_DOM_HLTH_TPA', 'OV_SP4_D_TPA',
                                     'OV_SP5', 'OV_SP5_BA', 'OV_SP5_TPA', 'OV_SP5_QMDBH',
                                     'OV_SP5_DOM_HLTH', 'OV_SP5_DOM_HLTH_PCMP', 'OV_SP5_DOM_HLTH_TPA', 'OV_SP5_D_TPA'],
                                    axis="columns")

    return ov_species


# Determine top 5 overstory species and generate associated statistics for plot summaries
def top5_ov_species_plot(tree_table):
    """ Creates a dataframe with the top 5 overstory species and associated statistics (BA, TPA, QM DBH, Dom. Health,
    Dom. Health % Composition, Dom. Health TPA, and Dead TPA) for each of the top 5 species

    Keyword Args:
          tree_table -- dataframe: input tree_table, produced by create_tree_table function
          level      -- string: field name for desired FMG level, i.e. SID, SITE, UNIT

    Details: None
    """
    # Create table with TPA for each unique species per given level
    species_df = tpa_ba_qmdbh_plot_by_case_long(tree_table=tree_table,
                                                filter_statement=None,
                                                case_column='TR_SP')

    # Remove rows with a tree species of None or NoTree
    species_df = species_df[species_df.TR_SP != "NONE"]

    # Sort species_df by plot and TPA
    species_df = species_df.sort_values(by=['PID', 'TPA'], ascending=False)

    # Rank each species within a single plot group, based on sort
    species_df['SP_RANK'] = species_df.groupby(['PID']).cumcount().add(1)

    # Filter on keep flag field where the value is less than or equal to 5
    species_df = species_df[species_df.SP_RANK <= 5]

    # Assign categorical variable for species rank to assist in pivot column naming
    species_df['OV_SP_RANK'] = species_df['SP_RANK'].map(overstory_sp_map)

    # Pivot variables based on sp rank field
    species_pivot_df2 = species_df.pivot(index='PID', columns='OV_SP_RANK', values=['TR_SP', 'BA', 'TPA', 'QM_DBH'])

    # flatten multi index and rename columns
    species_pivot_df2.columns = ['_'.join(col) for col in species_pivot_df2.columns.values]

    # reset index
    species_pivot_df2 = species_pivot_df2.reset_index()

    # Rename columns
    ov_species = species_pivot_df2 \
        .rename(columns={
                'TR_SP_OV_SP1': 'OV_SP1',
                'BA_OV_SP1': 'OV_SP1_BA',
                'TPA_OV_SP1': 'OV_SP1_TPA',
                'QM_DBH_OV_SP1': 'OV_SP1_QMDBH',
                'TR_SP_OV_SP2': 'OV_SP2',
                'BA_OV_SP2': 'OV_SP2_BA',
                'TPA_OV_SP2': 'OV_SP2_TPA',
                'QM_DBH_OV_SP2': 'OV_SP2_QMDBH',
                'TR_SP_OV_SP3': 'OV_SP3',
                'BA_OV_SP3': 'OV_SP3_BA',
                'TPA_OV_SP3': 'OV_SP3_TPA',
                'QM_DBH_OV_SP3': 'OV_SP3_QMDBH',
                'TR_SP_OV_SP4': 'OV_SP4',
                'BA_OV_SP4': 'OV_SP4_BA',
                'TPA_OV_SP4': 'OV_SP4_TPA',
                'QM_DBH_OV_SP4': 'OV_SP4_QMDBH',
                'TR_SP_OV_SP5': 'OV_SP5',
                'BA_OV_SP5': 'OV_SP5_BA',
                'TPA_OV_SP5': 'OV_SP5_TPA',
                'QM_DBH_OV_SP5': 'OV_SP5_QMDBH'})

    # Create iterator dict for sp 1-5
    species_columns = ['OV_SP1', 'OV_SP2', 'OV_SP3', 'OV_SP4', 'OV_SP5']
    iterator_lists = []
    for sp in species_columns:
        # filter out nan values
        ov_species_filtered = ov_species.dropna(subset=[sp])

        # Convert filtered df to a list of lists
        iterator = ov_species_filtered[['PID', sp]].values.tolist()

        # Append list to the iterator list
        iterator_lists.append(iterator)

    # Convert iterator list to dict so lists can be accessed by species rank
    iterator_dict = dict(zip(species_columns, iterator_lists))

    # iterate through the dict doing a bunch of stuff
    for key, value in iterator_dict.items():

        # Create empty list to hold results of loop
        health_dom_list = []

        # Iterate through value list
        for item in value:

            # filter tree table to a single stand
            tree_table_plot = tree_table.loc[tree_table['PID'] == item[0]]

            # Run health prev plot function with single stand associated species
            health_dom_plot_df = health_dom_plot(tree_table=tree_table_plot,
                                                 filter_statement=tree_table_plot['TR_SP'] == item[1])

            # Convert dataframe to list - contains pid, dom health, % comp
            health_dom_plot_list = health_dom_plot_df.values.tolist()[0]

            # Calculate TPA for just dom health trees
            dom_hlth_tpa = tpa_ba_qmdbh_plot(tree_table=tree_table_plot,
                                             filter_statement=
                                             (tree_table_plot['TR_HLTH'] == health_dom_plot_list[1]) &
                                             (tree_table_plot['TR_SP'] == item[1]))

            # Convert dom health tpa dataframe to list and insert into dom health list
            if len(dom_hlth_tpa.index) == 0:
                health_dom_plot_list.insert(3, 0)
            else:
                dom_hlth_tpa_list = dom_hlth_tpa.values.tolist()[0]
                health_dom_plot_list.insert(3, dom_hlth_tpa_list[5])

            # Calcualte TPA for just dead trees
            dead_hlth_tpa = tpa_ba_qmdbh_plot(tree_table=tree_table_plot,
                                              filter_statement=
                                              (tree_table_plot['TR_HLTH'] == 'D') &
                                              (tree_table_plot['TR_SP'] == item[1]))

            # Convert dead health tpa dataframe to list
            if len(dead_hlth_tpa.index) == 0:
                health_dom_plot_list.insert(4, 0)
            else:
                dead_hlth_tpa_list = dead_hlth_tpa.values.tolist()[0]
                health_dom_plot_list.insert(4, dead_hlth_tpa_list[5])

            # Add health prev list to loop result list
            health_dom_list.append(health_dom_plot_list)

        # convert loop result list to dataframe
        health_dom_ovsp = pd.DataFrame(health_dom_list, columns=['PID',
                                                                 key+'_HLTH_DOM',
                                                                 key+'_HLTH_DOM_PCMP',
                                                                 key+ '_HLTH_DOM_TPA',
                                                                 key+ '_D_TPA'])

        # Join dataframe to OV_SPECIES dataframe
        ov_species = ov_species.set_index('PID').join(health_dom_ovsp.set_index('PID'), how='left')
        ov_species = ov_species.reset_index()

    # Re order columns
    ov_species = ov_species.reindex(['PID',
                                     'OV_SP1', 'OV_SP1_BA', 'OV_SP1_TPA', 'OV_SP1_QMDBH',
                                     'OV_SP1_DOM_HLTH', 'OV_SP1_DOM_HLTH_PCMP', 'OV_SP1_DOM_HLTH_TPA', 'OV_SP1_D_TPA',
                                     'OV_SP2', 'OV_SP2_BA', 'OV_SP2_TPA', 'OV_SP2_QMDBH',
                                     'OV_SP2_DOM_HLTH', 'OV_SP2_DOM_HLTH_PCMP', 'OV_SP2_DOM_HLTH_TPA', 'OV_SP2_D_TPA',
                                     'OV_SP3', 'OV_SP3_BA', 'OV_SP3_TPA', 'OV_SP3_QMDBH',
                                     'OV_SP3_DOM_HLTH', 'OV_SP3_DOM_HLTH_PCMP', 'OV_SP3_DOM_HLTH_TPA', 'OV_SP3_D_TPA',
                                     'OV_SP4', 'OV_SP4_BA', 'OV_SP4_TPA', 'OV_SP4_QMDBH',
                                     'OV_SP4_DOM_HLTH', 'OV_SP4_DOM_HLTH_PCMP', 'OV_SP4_DOM_HLTH_TPA', 'OV_SP4_D_TPA',
                                     'OV_SP5', 'OV_SP5_BA', 'OV_SP5_TPA', 'OV_SP5_QMDBH',
                                     'OV_SP5_DOM_HLTH', 'OV_SP5_DOM_HLTH_PCMP', 'OV_SP5_DOM_HLTH_TPA', 'OV_SP5_D_TPA'],
                                    axis="columns")

    return ov_species


# Determine most common und and grnd species
def get_groupby_modes(source, keys, values, dropna=True, return_counts=False):
    """
    A function that groups a pandas dataframe by some of its columns (keys) and
    returns the most common value of each group for some of its columns (values).
    The output is sorted by the counts of the first column in values (because it
    uses pd.DataFrame.value_counts internally).
    An equivalent one-liner if values is a singleton list is:
    (
        source
        .value_counts(keys+values)
        .pipe(lambda x: x[~x.droplevel(values).index.duplicated()])
        .reset_index(name=f"{values[0]}_count")
    )
    If there are multiple modes for some group, it returns the value with the
    lowest Unicode value (because under the hood, it drops duplicate indexes in a
    sorted dataframe), unlike, e.g. df.groupby(keys)[values].agg(pd.Series.mode).
    Must have Pandas 1.1.0 or later for the function to work and must have
    Pandas 1.3.0 or later for the dropna parameter to work.
    -----------------------------------------------------------------------------
    Parameters:
    -----------
    source: pandas dataframe.
        A pandas dataframe with at least two columns.
    keys: list.
        A list of column names of the pandas dataframe passed as source. It is
        used to determine the groups for the groupby.
    values: list.
        A list of column names of the pandas dataframe passed as source.
        If it is a singleton list, the output contains the mode of each group
        for this column. If it is a list longer than 1, then the modes of each
        group for the additional columns are assigned as new columns.
    dropna: bool, default: True.
        Whether to count NaN values as the same or not. If True, NaN values are
        treated by their default property, NaN != NaN. If False, NaN values in
        each group are counted as the same values (NaN could potentially be a
        most common value).
    return_counts: bool, default: False.
        Whether to include the counts of each group's mode. If True, the output
        contains a column for the counts of each mode for every column in values.
        If False, the output only contains the modes of each group for each
        column in values.
    -----------------------------------------------------------------------------
    Returns:
    --------
    a pandas dataframe.
    -----------------------------------------------------------------------------
    Example:
    --------
    get_groupby_modes(source=df,
                      keys=df.columns[:2].tolist(),
                      values=df.columns[-2:].tolist(),
                      dropna=True,
                      return_counts=False)
    """

    def _get_counts(df, keys, v, dropna):
        c = df.value_counts(keys + v, dropna=dropna)
        return c[~c.droplevel(v).index.duplicated()]

    counts = _get_counts(source, keys, values[:1], dropna)

    if len(values) == 1:
        if return_counts:
            final = counts.reset_index(name=f"{values[0]}_count")
        else:
            final = counts.reset_index()[keys + values[:1]]
    else:
        final = counts.reset_index(name=f"{values[0]}_count", level=values[0])
        if not return_counts:
            final = final.drop(columns=f"{values[0]}_count")
        for v in values:
            counts = _get_counts(source, keys, [v], dropna).reset_index(level=v)
            if return_counts:
                final[[v, f"{v}_count"]] = counts
            else:
                final[v] = counts[v]
        final = final.reset_index()
    return final


# Create both species richness metrics
def create_sp_richness(tree_table, plot_table, level):
    # Create base df
    base_df = create_level_df(level, plot_table)

    # Filter Tree Table
    tree_table_live = tree_table[(tree_table['TR_HLTH'] != 'D') & (tree_table['TR_SP'] != 'NONE')]

    # Create Single Number Sp Rich (count of unique species
    sp_rich_ct = tree_table_live \
        .groupby(level) \
        .agg(SP_RICH=('TR_SP', 'nunique')) \
        .reset_index() \
        .set_index(level)

    # Create compound species richness: 3 digit 'number' = CT Uniq SP Hard Mast, CT Uniq SP Other, CT Uniq SP Typical
    # Count unique species for each SP richness category (Hard Mast, Other, Typical)
    comp_sp_rich_ct = tree_table_live \
        .groupby([level, 'SP_RICH_TYPE'], as_index=False) \
        .agg(COMP_SP_CT=('TR_SP', 'nunique'))

    # pivot count table to wide
    comp_sp_pivot = comp_sp_rich_ct \
        .pivot_table(index=level,
                     columns='SP_RICH_TYPE',
                     values=['COMP_SP_CT'],
                     fill_value=0) \
        .reset_index()

    # Flatten multiindex and rename columns
    comp_sp_pivot.columns = ["_".join(col) for col in comp_sp_pivot.columns.to_flat_index()]

    # set string dtypes
    level_col_name = level + '_'
    comp_sp_rich = comp_sp_pivot \
        .astype(dtype={'COMP_SP_CT_Hard': 'string',
                       'COMP_SP_CT_Other': 'string',
                       'COMP_SP_CT_Typical': 'string'}) \
        .rename(columns={level_col_name: level}) \
        .set_index(level)

    # Concatenate counts into 3 digit string
    comp_sp_rich['COMP_SP_RICH'] = comp_sp_rich.COMP_SP_CT_Hard.str.cat([comp_sp_rich.COMP_SP_CT_Other,
                                                                         comp_sp_rich.COMP_SP_CT_Typical])

    # Drop individual count cols from comp sp richness
    comp_sp_rich = comp_sp_rich \
        .drop(columns=['COMP_SP_CT_Hard', 'COMP_SP_CT_Other', 'COMP_SP_CT_Typical'])

    # Combine dfs into single df
    sp_richness = base_df.join(other=[sp_rich_ct, comp_sp_rich], how='left')
    sp_richness = sp_richness[['SP_RICH', 'COMP_SP_RICH']].reset_index()

    sp_richness = sp_richness.fillna(value={'SP_RICH': 0, 'COMP_SP_RICH': 'NONE'})

    return sp_richness


# Check for and correct ESRI Big Integer data type
def remove_esri_big_int(in_feature_class):
    arcpy.AddMessage('Begin on {}'.format(in_feature_class))
    # create field list
    field_list = arcpy.ListFields(dataset=in_feature_class,
                                  field_type='BIGINTEGER')
    arcpy.AddMessage('Created field list')

    # Loop through describe object doing stuff

    arcpy.AddMessage('Start field reformatting loop')

    if len(field_list) == 0:
        arcpy.AddMessage('No Big Int dtypes found')

    elif len(field_list) > 0:
        for field in field_list:
            # define some local variables
            new_name = str(field.name) + '_2'
            new_alias = str(field.aliasName)
            source_name = str(field.name)

            # add new field with correct data type
            arcpy.management.AddField(in_table=in_feature_class,
                                      field_name=new_name,
                                      field_type='LONG',
                                      field_alias=new_alias)
            arcpy.AddMessage('  Added field {}'.format(new_name))

            # calculate values for new field
            arcpy.management.CalculateField(in_table=in_feature_class,
                                            field=new_name,
                                            expression='!{}!'.format(source_name))

            arcpy.AddMessage('  Calculated field {}'.format(new_name))

            # delete old field
            arcpy.management.DeleteField(in_table=in_feature_class,
                                         drop_field=source_name)
            arcpy.AddMessage('  Deleted field {}'.format(source_name))

            # rename new field
            arcpy.management.AlterField(in_table=in_feature_class,
                                        field=new_name,
                                        new_field_name=source_name,
                                        new_field_alias=new_alias)
            arcpy.AddMessage('  Renamed field {} to {}'.format(new_name, source_name))

    return in_feature_class

    arcpy.AddMessage('Complete, check output')


# Create species importance values at plot level
def sp_importance_vals_plot(tree_table):

    # Create DF for level metrics
    iv_level_df = tpa_ba_qmdbh_plot(tree_table=tree_table,
                                    filter_statement=None)

    iv_level_df = iv_level_df\
        .rename(columns={'BA': 'Level_BA',
                         'TPA': 'Level_TPA'})\
        .drop(columns=['index', 'tree_count', 'plot_count', 'QM_DBH'],
              errors='ignore')\
        .set_index('PID')

    # Create DF for species metrics
    iv_species_df = tpa_ba_qmdbh_plot_by_case_long(tree_table=tree_table,
                                                   filter_statement=None,
                                                   case_column='TR_SP')

    iv_species_df = iv_species_df\
        .rename(columns={'BA': 'Species_BA',
                         'TPA': 'Species_TPA'})\
        .drop(columns=['index', 'plot_count', 'tree_count', 'QM_DBH'],
              errors='ignore')\
        .set_index('PID')

    # Join level metrics to species metrics DF by PID
    iv_df = iv_species_df\
        .join([iv_level_df],
              how='left')\
        .reset_index()

    # Add & populate relative BA col
    iv_df['Relative_BA'] = ((iv_df['Species_BA'] / iv_df['Level_BA']) * 100)

    # Add and populate relative TPA col
    iv_df['Relative_TPA'] = ((iv_df['Species_TPA'] / iv_df['Level_TPA']) * 100)

    # Add and populate Plot Importance Val Column
    iv_df['PLOT_IMPVAL'] = (iv_df['Relative_BA'] + iv_df['Relative_TPA'])

    # Tweak dtypes
    iv_df = iv_df.astype(dtype={'Level_TPA': 'float64', 'PLOT_IMPVAL': 'float64', 'Relative_TPA': 'float64',
                                'Species_TPA': 'float64'})

    # Fill NAs
    iv_df = iv_df.fillna(value={'Relative_BA': 0, 'Relative_TPA': 0, 'PLOT_IMPVAL': 0})

    return iv_df


# Create species importance values for non-plot levels
def sp_importance_vals_level(tree_table, level):

    # Create DF for level metrics
    iv_level_df = tpa_ba_qmdbh_level(tree_table=tree_table, filter_statement=None, level=level)

    iv_level_df = iv_level_df\
        .rename(columns={'BA': 'Level_BA',
                         'TPA': 'Level_TPA',
                         'plot_count': 'Level_PLT_CT'})\
        .drop(columns=['index', 'tree_count', 'QM_DBH', 'stand_dens'],
              errors='ignore')\
        .set_index(level)

    # Create DF for species BA & TPA metrics
    iv_species_ba_df = tpa_ba_qmdbh_level_by_case_long(tree_table=tree_table,
                                                       filter_statement=None,
                                                       case_column='TR_SP',
                                                       level=level)

    iv_species_ba_df = iv_species_ba_df\
        .rename(columns={'BA': 'Species_BA',
                         'TPA': 'Species_TPA'})\
        .drop(columns=['index', 'tree_count', 'stand_dens', 'plot_count', 'QM_DBH'],
              errors='ignore')\
        .set_index([level, 'TR_SP'])

    # Create Species plot count DF
    iv_species_pltct_df = tree_table\
        .groupby([level, 'TR_SP'], as_index=False)\
        .agg(Species_PLT_CT=('PID', agg_plot_count))\
        .set_index([level, 'TR_SP'])

    # Combine component species tables
    iv_species_df = iv_species_ba_df\
        .join([iv_species_pltct_df],
              how='left')\
        .reset_index()\
        .set_index(level)

    # Join level metrics to species metrics DF by level
    iv_df = iv_species_df\
        .join([iv_level_df],
              how='left')

    # Add & populate species frequency
    iv_df['Species_FREQ'] = (iv_df['Species_PLT_CT'] / iv_df['Level_PLT_CT'])

    # Create level frequency
    iv_level_freq = iv_df.groupby(level).agg(Level_FREQ=('Species_FREQ', 'sum'))

    # Join level freq to back to iv df
    iv_df = iv_df.join([iv_level_freq], how='left').reset_index()

    # Calc importance value
    iv_df['Relative_FREQ'] = ((iv_df['Species_FREQ'] / iv_df['Level_FREQ']) * 100)
    iv_df['Relative_BA'] = ((iv_df['Species_BA'] / iv_df['Level_BA']) * 100)
    iv_df['Relative_TPA'] = ((iv_df['Species_TPA'] / iv_df['Level_TPA']) * 100)
    iv_df['SP_IMP_VAL'] = (iv_df['Relative_FREQ'] + iv_df['Relative_BA'] + iv_df['Relative_TPA'])

    # Tweak dtypes
    iv_df = iv_df.astype(dtype={'Species_TPA': 'float64', 'Level_TPA': 'float64', 'Relative_TPA': 'float64',
                                'SP_IMP_VAL': 'float64', 'TR_SP': 'string'})

    return iv_df

