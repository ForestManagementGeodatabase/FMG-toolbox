import fmgpy.fmglib.forest_calcs as fcalc
import pandas as pd


def test_size():
    # define test data location
    age = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Age_QA_20250513'
    fixed = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Fixed_QA_20250513'

    # create age, fixed, and prism dataframes from test data
    age_df = pd.DataFrame.spatial.from_featureclass(age)
    fixed_df = pd.DataFrame.spatial.from_featureclass(fixed)

    # create tree and plot tables from age, fixed, and prism dataframes
    plot_table = fcalc.create_plot_table(fixed_df, age_df)

    assert plot_table.shape[0] == fixed_df.shape[0] # test number of rows


def test_column_locations():
    # define test data location
    age = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Age_QA_20250513'
    fixed = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Fixed_QA_20250513'

    # create age, fixed, and prism dataframes from test data
    age_df = pd.DataFrame.spatial.from_featureclass(age)
    fixed_df = pd.DataFrame.spatial.from_featureclass(fixed)

    # create tree and plot tables from age, fixed, and prism dataframes
    plot_table = fcalc.create_plot_table(fixed_df, age_df)

    # PID column
    plot_subset_1 = plot_table.iloc[:, 0:1]
    fixed_subset_1 = fixed_df.iloc[:, 35:36]

    # FX_MISC / MISC column
    plot_subset_3 = plot_table.iloc[:, 1:3]
    fixed_subset_3 = fixed_df.iloc[:, 1:3]

    # Plot through NOT_SP5
    plot_subset_2 = plot_table.iloc[:, 1:17]
    fixed_subset_2 = fixed_df.iloc[:, 1:17]

    # COL_CREW through SID
    plot_subset_4 = plot_table.iloc[:, 18:35]
    fixed_subset_4 = fixed_df.iloc[:, 18:35]

    # VALID_SID through SHAPE
    plot_subset_5 = plot_table.iloc[:, 35:37]
    fixed_subset_5 = fixed_df.iloc[:, 36:38]

    # check for equal data
    pd.testing.assert_frame_equal(plot_subset_1, fixed_subset_1)
    pd.testing.assert_frame_equal(plot_subset_2, fixed_subset_2)
    assert plot_subset_3.equals(fixed_subset_3)
    pd.testing.assert_frame_equal(plot_subset_4, fixed_subset_4)
    pd.testing.assert_frame_equal(plot_subset_5, fixed_subset_5)

    # Check for age columns
    age_columns = ["POOL", "COMP", "UNIT", "SITE", "SID", "VALID_SID", "SHAPE", "AGE_SP", "AGE_DIA", "AGE_ORIG", "AGE_GRW", "AGE_MISC", "MAST_TYPE"]
    for col in age_columns:
        assert col in plot_table.columns



def test_data_types():
    # define test data location
    age = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Age_QA_20250513'
    fixed = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Fixed_QA_20250513'

    # create age, fixed, and prism dataframes from test data
    age_df = pd.DataFrame.spatial.from_featureclass(age)
    fixed_df = pd.DataFrame.spatial.from_featureclass(fixed)

    # create tree and plot tables from age, fixed, and prism dataframes
    plot_table = fcalc.create_plot_table(fixed_df, age_df)

    output_data_types = pd.Series({
        'PID': 'string[python]',
        'PLOT': 'Int32',
        'OV_CLSR': 'string[python]',
        'OV_HT': 'string[python]',
        'UND_HT': 'string[python]',
        'UND_COV': 'string[python]',
        'UND_SP1': 'string[python]',
        'UND_SP2': 'string[python]',
        'UND_SP3': 'string[python]',
        'GRD_SP1': 'string[python]',
        'GRD_SP2': 'string[python]',
        'GRD_SP3': 'string[python]',
        'NOT_SP1': 'string[python]',
        'NOT_SP2': 'string[python]',
        'NOT_SP3': 'string[python]',
        'NOT_SP4': 'string[python]',
        'NOT_SP5': 'string[python]',
        'FX_MISC': 'string[python]',
        'COL_CREW': 'string[python]',
        'COL_DATE': 'datetime64[us]',
        'FP_TIME': 'string[python]',
        'MIS_FIELDS': 'string[python]',
        'HAS_MIS_FIELD': 'string[python]',
        'UND_HT2': 'Float64',
        'VALID_PLOT_ID': 'string[python]',
        'METERS_FROM_PLOT_CENTER': 'Float64',
        'CORRECT_PLOT_ID': 'string[python]',
        'HAS_PRISM': 'string[python]',
        'DUPLICATE': 'string[python]',
        'PRISM_ID_MATCHES': 'string[python]',
        'POOL': 'string[python]',
        'COMP': 'string[python]',
        'UNIT': 'string[python]',
        'SITE': 'string[python]',
        'SID': 'string[python]',
        'VALID_SID': 'string[python]',
        'SHAPE': 'geometry',
        'AGE_SP': 'string[python]',
        'AGE_DIA': 'Float64',
        'AGE_ORIG': 'Int32',
        'AGE_GRW': 'Int32',
        'AGE_MISC': 'string[python]',
        'MAST_TYPE': 'string[python]',
        'INV_SP': 'string[python]',
        'INV_PRESENT': 'string[python]'
    })

    assert plot_table.dtypes.equals(output_data_types)
