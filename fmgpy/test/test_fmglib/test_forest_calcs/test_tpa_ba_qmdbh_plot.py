import fmgpy.fmglib.forest_calcs as fcalc
import pandas as pd
import pandas.testing as pdt


def test_itself():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)

    # Establish aliases for appropriate folders
    csv_folder_path = './dataframe_test_csvs/tpa_ba_qmdbh_plot/'
    none = csv_folder_path + 'none.csv'
    mastType_hard = csv_folder_path + 'mastType_hard.csv'

    # create dataframe with no filter
    filter_statement = None
    tbq_table_none = fcalc.tpa_ba_qmdbh_plot(tree_table, filter_statement)

    # create dataframe with filter on MAST_TYPE
    filter_statement = tree_table.MAST_TYPE == 'Hard'
    tbq_table_mastType_hard = fcalc.tpa_ba_qmdbh_plot(tree_table, filter_statement)

    # Read dataframes from csvs
    asserted_dataframe_none = pd.read_csv(none)
    asserted_dataframe_mastType_hard = pd.read_csv(mastType_hard)

    # Apply modifications to dataframes to make comparisons feasible
    tbq_table_none = tbq_table_none.replace('', pd.NA)
    asserted_dataframe_none = asserted_dataframe_none.replace('', pd.NA)
    tbq_table_mastType_hard = tbq_table_mastType_hard.replace('', pd.NA)
    asserted_dataframe_mastType_hard = asserted_dataframe_mastType_hard.replace('', pd.NA)

    # Make dataframe from csv have correct datatypes
    asserted_dataframe_none = asserted_dataframe_none.astype({
        'index': 'int64',
        'PID': 'string[python]',
        'tree_count': 'float64',
        'plot_count': 'float64',
        'TPA': 'float64',
        'BA': 'float64',
        'QM_DBH': 'float64'
    })

    # Make dataframe from csv have correct datatypes
    asserted_dataframe_mastType_hard = asserted_dataframe_mastType_hard.astype({
        'index': 'int64',
        'PID': 'string[python]',
        'tree_count': 'float64',
        'plot_count': 'float64',
        'TPA': 'float64',
        'BA': 'float64',
        'QM_DBH': 'float64'
    })

    # Compare function output stored in csv to current function behavior.
    pdt.assert_frame_equal(tbq_table_none, asserted_dataframe_none)
    pdt.assert_frame_equal(tbq_table_mastType_hard, asserted_dataframe_mastType_hard)

def test_column_existence():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    filter_statement = None

    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)
    tbq_table = fcalc.tpa_ba_qmdbh_plot(tree_table, filter_statement)

    asserted_columns = ['index', 'PID', 'tree_count', 'plot_count', 'TPA', 'BA', 'QM_DBH']

    assert set(asserted_columns).issubset(tbq_table.columns)
    assert len(asserted_columns) == len(tbq_table.columns)


def test_data_types():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    filter_statement = None

    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)
    tbq_table = fcalc.tpa_ba_qmdbh_plot(tree_table, filter_statement)

    asserted_dtypes = pd.Series({
        'index': 'int64',
        'PID': 'string[python]',
        'tree_count': 'float64',
        'plot_count': 'float64',
        'TPA': 'float64',
        'BA': 'float64',
        'QM_DBH': 'float64'
    })

    assert tbq_table.dtypes.equals(asserted_dtypes)
# create a piece of small, toy data where the transformations are obvious and/or trivial given the size, and
#   compare function output to that.

#
# #--------------------------------------SCRATCHPAD VVVVV---------------------------------------------------
#
# import fmgpy.fmglib.forest_calcs as fcalc
# import pandas as pd
#
# # define test data location
# age = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Age_QA_20250513'
# fixed = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Fixed_QA_20250513'
# prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
# filter_statement = None
#
# age_df = pd.DataFrame.spatial.from_featureclass(age)
# fixed_df = pd.DataFrame.spatial.from_featureclass(fixed)
# prism_df = pd.DataFrame.spatial.from_featureclass(prism)
#
# plot_table = fcalc.create_plot_table(fixed_df, age_df)
#
# tree_table = fcalc.create_tree_table(prism_df)
#
# tbq_table = fcalc.tpa_ba_qmdbh_plot(tree_table, filter_statement)