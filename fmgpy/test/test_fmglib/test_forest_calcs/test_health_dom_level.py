import fmgpy.fmglib.forest_calcs as fcalc
import pandas as pd
import pandas.testing as pdt


def test_itself():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)

    csv_folder_path = './dataframe_test_csvs/health_dom_level/'
    none_pid = csv_folder_path + 'none_pid.csv'
    mastType_hard_pool = csv_folder_path + 'mastType_hard_pool.csv'

    filter_statement = None
    health_dom_level_none_pid = fcalc.tpa_ba_qmdbh_level(tree_table, filter_statement, 'SID')
    #health_dom_level_none_pid.to_csv('./dataframe_test_csvs/health_dom_level/none_pid.csv', index=False)

    filter_statement = tree_table.MAST_TYPE == 'Hard'
    health_dom_level_mastType_hard_pool = fcalc.tpa_ba_qmdbh_level(tree_table, filter_statement, 'POOL')
    #health_dom_level_mastType_hard_pool.to_csv('./dataframe_test_csvs/health_dom_level/mastType_hard_pool.csv', index=False)

    asserted_dataframe_none_pid = pd.read_csv(none_pid)
    asserted_dataframe_mastType_hard_pool = pd.read_csv(mastType_hard_pool)

    health_dom_level_none_pid = health_dom_level_none_pid.replace('', pd.NA)
    asserted_dataframe_none_pid = asserted_dataframe_none_pid.replace('', pd.NA)

    health_dom_level_mastType_hard_pool = health_dom_level_mastType_hard_pool.replace('', pd.NA)
    asserted_dataframe_mastType_hard_pool = asserted_dataframe_mastType_hard_pool.replace('', pd.NA)

    asserted_dataframe_none_pid = asserted_dataframe_none_pid.astype({
        'index': 'int64',
        'SID': 'string[python]',
        'tree_count': 'float64',
        'stand_dens': 'float64',
        'plot_count': 'float64',
        'TPA': 'float64',
        'BA': 'float64',
        'QM_DBH': 'float64'
    })
    asserted_dataframe_mastType_hard_pool = asserted_dataframe_mastType_hard_pool.astype({
        'index': 'int64',
        'POOL': 'string[python]',
        'tree_count': 'float64',
        'stand_dens': 'float64',
        'plot_count': 'float64',
        'TPA': 'float64',
        'BA': 'float64',
        'QM_DBH': 'float64'
    })

    pdt.assert_frame_equal(health_dom_level_none_pid, asserted_dataframe_none_pid)
    pdt.assert_frame_equal(health_dom_level_mastType_hard_pool, asserted_dataframe_mastType_hard_pool)


def test_dataframe_size():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    filter_statement = None
    level = 'SID'

    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)
    hdl_table = fcalc.health_dom_level(tree_table, filter_statement, level)

    #TODO: Write test for the correct number of rows. This could be converted to an end-to-end-test of the function,
    # testing the entire dataframe after several different filter statements.
def test_column_existence():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    filter_statement = None
    level = 'SID'

    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)
    hdl_table = fcalc.health_dom_level(tree_table, filter_statement, level)

    asserted_columns = ['SID', 'HLTH_DOM', 'HLTH_DOM_PCMP']

    assert set(asserted_columns).issubset(hdl_table.columns)
    assert len(asserted_columns) == len(hdl_table.columns)

def test_data_types():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    filter_statement = None
    level = 'SID'

    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)
    hdl_table = fcalc.health_dom_level(tree_table, filter_statement, level)

    asserted_dtypes = pd.Series({
        'SID': 'string[python]', 'HLTH_DOM': 'string[python]', 'HLTH_DOM_PCMP': 'float64'
    })

    assert (asserted_dtypes.loc[hdl_table.dtypes.index] == hdl_table.dtypes).all()