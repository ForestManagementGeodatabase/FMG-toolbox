import fmgpy.fmglib.forest_calcs as fcalc
import pandas as pd
import pandas.testing as pdt


def test_itself():
    # Define folder paths
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    csv_folder_path = './dataframe_test_csvs/health_dom_level/'
    df_1_csv = csv_folder_path + 'df_1.csv'
    df_2_csv = csv_folder_path + 'df_2.csv'

    # Create necessary dataframes
    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)

    # Create first dataframe
    filter_statement = None
    df_1 = fcalc.tpa_ba_qmdbh_level(tree_table, filter_statement, 'SID')
    #df_1.to_csv(df_1_csv, index=False) # Uncomment to generate new csvs

    # Create second dataframe
    filter_statement = tree_table.MAST_TYPE == 'Hard'
    df_2 = fcalc.tpa_ba_qmdbh_level(tree_table, filter_statement, 'POOL')
    #df_2.to_csv(df_2_csv, index=False) # Uncomment to generate new csvs

    # Import dataframes from csvs
    asserted_dataframe_1 = pd.read_csv(df_1_csv)
    asserted_dataframe_2 = pd.read_csv(df_2_csv)

    # Clean up empty spaces/NaN values for easier comparison
    df_1 = df_1.replace('', pd.NA)
    df_2 = df_2.replace('', pd.NA)

    asserted_dataframe_1 = asserted_dataframe_1.astype({
        'index': 'int64',
        'SID': 'string[python]',
        'tree_count': 'float64',
        'stand_dens': 'float64',
        'plot_count': 'float64',
        'TPA': 'float64',
        'BA': 'float64',
        'QM_DBH': 'float64'
    })
    asserted_dataframe_2 = asserted_dataframe_2.astype({
        'index': 'int64',
        'POOL': 'string[python]',
        'tree_count': 'float64',
        'stand_dens': 'float64',
        'plot_count': 'float64',
        'TPA': 'float64',
        'BA': 'float64',
        'QM_DBH': 'float64'
    })

    pdt.assert_frame_equal(df_1, asserted_dataframe_1)
    pdt.assert_frame_equal(df_2, asserted_dataframe_2)


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