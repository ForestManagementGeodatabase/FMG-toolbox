import fmgpy.fmglib.forest_calcs as fcalc
import pandas as pd
import pandas.testing as pdt


def test_itself():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)

    csv_folder_path = './dataframe_test_csvs/health_dom_plot/'
    none = csv_folder_path + 'none.csv'
    mastType_hard = csv_folder_path + 'mastType_hard.csv'


    filter_statement = None
    health_dom_table_none = fcalc.tpa_ba_qmdbh_plot(tree_table, filter_statement)

    filter_statement = tree_table.MAST_TYPE == 'Hard'
    health_dom_table_mastType_hard = fcalc.tpa_ba_qmdbh_plot(tree_table, filter_statement)

    asserted_dataframe_none = pd.read_csv(none)
    asserted_dataframe_mastType_hard = pd.read_csv(mastType_hard)

    health_dom_table_none = health_dom_table_none.replace('', pd.NA)
    asserted_dataframe_none = asserted_dataframe_none.replace('', pd.NA)

    health_dom_table_mastType_hard = health_dom_table_mastType_hard.replace('', pd.NA)
    asserted_dataframe_mastType_hard = asserted_dataframe_mastType_hard.replace('', pd.NA)

    asserted_dataframe_none = asserted_dataframe_none.astype({
        'index': 'int64',
        'PID': 'string[python]',
        'tree_count': 'float64',
        'plot_count': 'float64',
        'TPA': 'float64',
        'BA': 'float64',
        'QM_DBH': 'float64'
    })
    asserted_dataframe_mastType_hard = asserted_dataframe_mastType_hard.astype({
        'index': 'int64',
        'PID': 'string[python]',
        'tree_count': 'float64',
        'plot_count': 'float64',
        'TPA': 'float64',
        'BA': 'float64',
        'QM_DBH': 'float64'
    })

    pdt.assert_frame_equal(health_dom_table_none, asserted_dataframe_none)
    pdt.assert_frame_equal(health_dom_table_mastType_hard, asserted_dataframe_mastType_hard)
def test_column_existence():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    filter_statement = None

    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)
    hdp_table = fcalc.health_dom_plot(tree_table, filter_statement)

    asserted_columns = ['PID', 'HLTH_DOM', 'HLTH_DOM_PCMP']

    assert set(asserted_columns).issubset(hdp_table.columns)
    assert len(asserted_columns) == len(hdp_table.columns)

def test_data_types():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    filter_statement = None

    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)
    hdp_table = fcalc.health_dom_plot(tree_table, filter_statement)

    asserted_dtypes = pd.Series({
        'PID': 'string[python]', 'HLTH_DOM': 'string[python]', 'HLTH_DOM_PCMP': 'float64'
    })

    assert (asserted_dtypes.loc[hdp_table.dtypes.index] == hdp_table.dtypes).all()