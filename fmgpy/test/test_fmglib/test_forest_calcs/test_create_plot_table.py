import fmgpy.fmglib.forest_calcs as fcalc
import pandas as pd

def test_create_plot_table():
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
