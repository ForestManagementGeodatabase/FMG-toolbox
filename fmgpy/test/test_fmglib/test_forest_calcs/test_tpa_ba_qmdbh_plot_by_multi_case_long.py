import fmgpy.fmglib.forest_calcs as fcalc
import pandas as pd
import pandas.testing as pdt

def test_itself():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)

    # Establish aliases for appropriate folders
    csv_folder_path = './dataframe_test_csvs/tpa_ba_qmdbh_plot_by_multi_case_long/'
    tbq_csv_1 = csv_folder_path + 'tbq1.csv'
    tbq_csv_2 = csv_folder_path + 'tbq2.csv'
    tbq_csv_3 = csv_folder_path + 'tbq3.csv'

    # create dataframe with no filter and case of MAST_TYPE
    filter_statement = None
    case_column = ['MAST_TYPE']
    tbq_table_1 = fcalc.tpa_ba_qmdbh_plot_by_multi_case_long(tree_table, filter_statement, case_column)
    #tbq_table_1.to_csv(tbq_csv_1, index=False)

    # create dataframe with no filter and case of SP_TYPE
    filter_statement = None
    case_column = ['MAST_TYPE', 'SP_TYPE']
    tbq_table_2 = fcalc.tpa_ba_qmdbh_plot_by_multi_case_long(tree_table, filter_statement, case_column)
    #tbq_table_2.to_csv(tbq_csv_2, index=False)

    # create dataframe with filter of tree diameter above 10 and case of SP_TYPE
    filter_statement = tree_table.TR_DIA > 10
    case_column = ['MAST_TYPE', 'SP_TYPE']
    tbq_table_3 = fcalc.tpa_ba_qmdbh_plot_by_multi_case_long(tree_table, filter_statement, case_column)
    #tbq_table_3.to_csv(tbq_csv_3, index=False)


    # Read dataframes from csvs
    asserted_dataframe_1 = pd.read_csv(tbq_csv_1)
    asserted_dataframe_2 = pd.read_csv(tbq_csv_2)
    asserted_dataframe_3 = pd.read_csv(tbq_csv_3)

    # Modify dataframe blank/NA values for comparison
    tbq_table_1 = tbq_table_1.replace('', pd.NA)
    asserted_dataframe_1 = asserted_dataframe_1.replace('', pd.NA)
    tbq_table_2 = tbq_table_2.replace('', pd.NA)
    asserted_dataframe_2 = asserted_dataframe_2.replace('', pd.NA)
    tbq_table_3 = tbq_table_3.replace('', pd.NA)
    asserted_dataframe_3 = asserted_dataframe_3.replace('', pd.NA)

    # Make dataframe from csv have correct datatypes
    asserted_dataframe_1 = asserted_dataframe_1.astype({
        'PID': 'string[python]',
        'MAST_TYPE': 'string[python]',
        'Tree_Count': 'float64',
        'Plot_Count': 'float64',
        'TPA': 'float64',
        'BA': 'float64',
        'QM_DBH': 'float64'
    })

    # Make dataframe from csv have correct datatypes
    asserted_dataframe_2 = asserted_dataframe_2.astype({
        'PID': 'string[python]',
        'MAST_TYPE': 'string[python]',
        'SP_TYPE': 'object',
        'Tree_Count': 'float64',
        'Plot_Count': 'float64',
        'TPA': 'float64',
        'BA': 'float64',
        'QM_DBH': 'float64'
    })
    asserted_dataframe_3 = asserted_dataframe_3.astype({
        'PID': 'string[python]',
        'MAST_TYPE': 'string[python]',
        'SP_TYPE': 'object',
        'Tree_Count': 'float64',
        'Plot_Count': 'float64',
        'TPA': 'float64',
        'BA': 'float64',
        'QM_DBH': 'float64'
    })

    # Compare function output stored in csv to current function behavior.
    pdt.assert_frame_equal(tbq_table_1, asserted_dataframe_1)
    pdt.assert_frame_equal(tbq_table_2, asserted_dataframe_2)
    pdt.assert_frame_equal(tbq_table_3, asserted_dataframe_3)