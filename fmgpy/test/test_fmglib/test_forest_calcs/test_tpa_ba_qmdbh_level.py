import fmgpy.fmglib.forest_calcs as fcalc
import pandas as pd
import pandas.testing as pdt

def test_itself():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)

    csv_folder_path = './dataframe_test_csvs/tpa_ba_qmdbh_level/'
    none_pid = csv_folder_path + 'none.csv'
    mastType_hard_pool = csv_folder_path + 'mastType_hard.csv'


    filter_statement = None
    tbq_table_none = fcalc.tpa_ba_qmdbh_level(tree_table, filter_statement, 'SID')

    filter_statement = tree_table.MAST_TYPE == 'Hard'
    tbq_table_mastType_hard = fcalc.tpa_ba_qmdbh_level(tree_table, filter_statement, 'POOL')

    asserted_dataframe_none = pd.read_csv(none_pid)
    asserted_dataframe_mastType_hard = pd.read_csv(mastType_hard_pool)

    asserted_dataframe_none = asserted_dataframe_none.astype({
        'index': 'int64',
        'SID': 'string[python]',
        'tree_count': 'float64',
        'stand_dens': 'float64',
        'plot_count': 'float64',
        'TPA': 'float64',
        'BA': 'float64',
        'QM_DBH': 'float64'
    })
    asserted_dataframe_mastType_hard = asserted_dataframe_mastType_hard.astype({
        'index': 'int64',
        'POOL': 'string[python]',
        'tree_count': 'float64',
        'stand_dens': 'float64',
        'plot_count': 'float64',
        'TPA': 'float64',
        'BA': 'float64',
        'QM_DBH': 'float64'
    })

    tbq_table_none = tbq_table_none.replace('', pd.NA)
    asserted_dataframe_none = asserted_dataframe_none.replace('', pd.NA)
    tbq_table_mastType_hard = tbq_table_mastType_hard.replace('', pd.NA)
    asserted_dataframe_mastType_hard = asserted_dataframe_mastType_hard.replace('', pd.NA)

    pdt.assert_frame_equal(tbq_table_none, asserted_dataframe_none)
    pdt.assert_frame_equal(tbq_table_mastType_hard, asserted_dataframe_mastType_hard)

def test_column_existence():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    filter_statement = None
    level = 'PID'

    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)
    tbq_table = fcalc.tpa_ba_qmdbh_level(tree_table, filter_statement, level)

    asserted_columns = ['index', 'PID', 'tree_count', 'stand_dens', 'plot_count', 'TPA', 'BA', 'QM_DBH']

    assert set(asserted_columns).issubset(tbq_table.columns)
    assert len(asserted_columns) == len(tbq_table.columns)

def test_data_types():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    filter_statement = None
    level = 'PID'

    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)
    tbq_table = fcalc.tpa_ba_qmdbh_level(tree_table, filter_statement, level)

    asserted_dtypes = pd.Series({
        'index': 'int64',
        'PID': 'string[python]',
        'tree_count': 'float64',
        'stand_dens': 'float64',
        'plot_count': 'float64',
        'TPA': 'float64',
        'BA': 'float64',
        'QM_DBH': 'float64'
    })


    assert tbq_table.dtypes.equals(asserted_dtypes)
