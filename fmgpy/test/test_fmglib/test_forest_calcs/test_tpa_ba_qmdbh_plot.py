import fmgpy.fmglib.forest_calcs as fcalc
import pandas as pd

def test_dataframe_size():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    filter_statement = None

    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)
    tbq_table = fcalc.tpa_ba_qmdbh_plot(tree_table, filter_statement)

    #TODO: Figure out how to test for correct row number. I believe the number of rows can vary depending on the filter
    # statement. Maybe create a couple tests with different filter statements where we know the correct number of rows
    # and assert those.

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