import fmgpy.fmglib.forest_calcs as fcalc
import pandas as pd
import pandas.testing as pdt

def test_itself():
    # define test data location
    age = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Age_QA_20250513'
    fixed = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Fixed_QA_20250513'

    age_df = pd.DataFrame.spatial.from_featureclass(age)
    fixed_df = pd.DataFrame.spatial.from_featureclass(fixed)

    plot_table = fcalc.create_plot_table(fixed_df, age_df)

    csv_folder_path = './dataframe_test_csvs/create_plot_table/'
    saved_copy_path = csv_folder_path + 'plot_table.csv'

    asserted_dataframe = pd.read_csv(saved_copy_path)

    plot_table = plot_table.drop('SHAPE', axis=1)
    asserted_dataframe = asserted_dataframe.drop('SHAPE', axis=1)

    plot_table = plot_table.replace('', pd.NA)
    asserted_dataframe = asserted_dataframe.replace('', pd.NA)


    asserted_dataframe = asserted_dataframe.astype({
        'PID': 'string[python]', 'PLOT': 'Int32', 'OV_CLSR': 'string[python]', 'OV_HT': 'string[python]',
        'UND_HT': 'string[python]', 'UND_COV': 'string[python]', 'UND_SP1': 'string[python]',
        'UND_SP2': 'string[python]', 'UND_SP3': 'string[python]', 'GRD_SP1': 'string[python]',
        'GRD_SP2': 'string[python]', 'GRD_SP3': 'string[python]', 'NOT_SP1': 'string[python]',
        'NOT_SP2': 'string[python]', 'NOT_SP3': 'string[python]', 'NOT_SP4': 'string[python]',
        'NOT_SP5': 'string[python]', 'FX_MISC': 'string[python]', 'COL_CREW': 'string[python]',
        'COL_DATE': 'datetime64[us]', 'FP_TIME': 'string[python]', 'MIS_FIELDS': 'string[python]',
        'HAS_MIS_FIELD': 'string[python]', 'UND_HT2': 'Float64', 'VALID_PLOT_ID': 'string[python]',
        'METERS_FROM_PLOT_CENTER': 'Float64', 'CORRECT_PLOT_ID': 'string[python]', 'HAS_PRISM': 'string[python]',
        'DUPLICATE': 'string[python]', 'PRISM_ID_MATCHES': 'string[python]', 'POOL': 'string[python]',
        'COMP': 'string[python]', 'UNIT': 'string[python]', 'SITE': 'string[python]', 'SID': 'string[python]',
        'VALID_SID': 'string[python]', 'AGE_SP': 'string[python]', 'AGE_DIA': 'Float64',
        'AGE_ORIG': 'Int32', 'AGE_GRW': 'Int32', 'AGE_MISC': 'string[python]', 'MAST_TYPE': 'string[python]',
        'INV_SP': 'string[python]', 'INV_PRESENT': 'string[python]'
    })

    pdt.assert_frame_equal(plot_table, asserted_dataframe)

def test_dataframe_size():
    # define test data location
    age = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Age_QA_20250513'
    fixed = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Fixed_QA_20250513'

    age_df = pd.DataFrame.spatial.from_featureclass(age)
    fixed_df = pd.DataFrame.spatial.from_featureclass(fixed)

    plot_table = fcalc.create_plot_table(fixed_df, age_df)

    assert plot_table.shape[0] == fixed_df.shape[0] # test number of rows

def test_column_existence():
    age = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Age_QA_20250513'
    fixed = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Fixed_QA_20250513'

    age_df = pd.DataFrame.spatial.from_featureclass(age)
    fixed_df = pd.DataFrame.spatial.from_featureclass(fixed)

    plot_table = fcalc.create_plot_table(fixed_df, age_df)

    asserted_columns = ['PID', 'PLOT', 'OV_CLSR', 'OV_HT', 'UND_HT', 'UND_COV', 'UND_SP1', 'UND_SP2', 'UND_SP3',
                        'GRD_SP1', 'GRD_SP2', 'GRD_SP3', 'NOT_SP1', 'NOT_SP2', 'NOT_SP3', 'NOT_SP4', 'NOT_SP5',
                        'FX_MISC', 'COL_CREW', 'COL_DATE', 'FP_TIME', 'MIS_FIELDS', 'HAS_MIS_FIELD', 'UND_HT2',
                        'VALID_PLOT_ID', 'METERS_FROM_PLOT_CENTER', 'CORRECT_PLOT_ID', 'HAS_PRISM', 'DUPLICATE',
                        'PRISM_ID_MATCHES', 'POOL', 'COMP', 'UNIT', 'SITE', 'SID', 'VALID_SID', 'SHAPE', 'AGE_SP',
                        'AGE_DIA', 'AGE_ORIG', 'AGE_GRW', 'AGE_MISC', 'MAST_TYPE', 'INV_SP', 'INV_PRESENT']

    assert set(asserted_columns).issubset(plot_table.columns)
    assert len(asserted_columns) == len(plot_table.columns)

def test_data_types():
    # define test data location
    age = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Age_QA_20250513'
    fixed = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Fixed_QA_20250513'

    # create age, fixed, and prism dataframes from test data
    age_df = pd.DataFrame.spatial.from_featureclass(age)
    fixed_df = pd.DataFrame.spatial.from_featureclass(fixed)

    # create tree and plot tables from age, fixed, and prism dataframes
    plot_table = fcalc.create_plot_table(fixed_df, age_df)

    asserted_dtypes = pd.Series({
        'PID': 'string[python]', 'PLOT': 'Int32', 'OV_CLSR': 'string[python]', 'OV_HT': 'string[python]',
        'UND_HT': 'string[python]', 'UND_COV': 'string[python]', 'UND_SP1': 'string[python]',
        'UND_SP2': 'string[python]', 'UND_SP3': 'string[python]', 'GRD_SP1': 'string[python]',
        'GRD_SP2': 'string[python]', 'GRD_SP3': 'string[python]', 'NOT_SP1': 'string[python]',
        'NOT_SP2': 'string[python]', 'NOT_SP3': 'string[python]', 'NOT_SP4': 'string[python]',
        'NOT_SP5': 'string[python]', 'FX_MISC': 'string[python]', 'COL_CREW': 'string[python]',
        'COL_DATE': 'datetime64[us]', 'FP_TIME': 'string[python]', 'MIS_FIELDS': 'string[python]',
        'HAS_MIS_FIELD': 'string[python]', 'UND_HT2': 'Float64', 'VALID_PLOT_ID': 'string[python]',
        'METERS_FROM_PLOT_CENTER': 'Float64', 'CORRECT_PLOT_ID': 'string[python]', 'HAS_PRISM': 'string[python]',
        'DUPLICATE': 'string[python]', 'PRISM_ID_MATCHES': 'string[python]', 'POOL': 'string[python]',
        'COMP': 'string[python]', 'UNIT': 'string[python]', 'SITE': 'string[python]', 'SID': 'string[python]',
        'VALID_SID': 'string[python]', 'SHAPE': 'geometry', 'AGE_SP': 'string[python]', 'AGE_DIA': 'Float64',
        'AGE_ORIG': 'Int32', 'AGE_GRW': 'Int32', 'AGE_MISC': 'string[python]', 'MAST_TYPE': 'string[python]',
        'INV_SP': 'string[python]', 'INV_PRESENT': 'string[python]'
    })
    plot_table_dtypes = plot_table.dtypes

    assert (asserted_dtypes.loc[plot_table_dtypes.index] == plot_table_dtypes).all()