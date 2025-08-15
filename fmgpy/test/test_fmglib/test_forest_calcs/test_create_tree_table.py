# Do Some Imports
import pandas as pd
import fmgpy.fmglib.forest_calcs as fcalc
import pandas.testing as pdt

def test_itself():
    # Define appropriate folder paths
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    csv_folder_path = './dataframe_test_csvs/create_tree_table/'
    saved_copy_path = csv_folder_path + 'tree_table.csv'

    # Create necessary dataframes
    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)

    # Read stored behavior from csv into dataframe
    asserted_dataframe = pd.read_csv(saved_copy_path)

    # Drop shape columns simply because it is hard to compare. We currently don't have checking for this column.
    tree_table = tree_table.drop('SHAPE', axis=1)
    asserted_dataframe = asserted_dataframe.drop('SHAPE', axis=1)

    # Clean up empty/NaN values for easier checking
    tree_table = tree_table.replace('', pd.NA)
    asserted_dataframe = asserted_dataframe.replace('', pd.NA)

    # Give data types to csv from the dataframe.
    asserted_dataframe = asserted_dataframe.astype({
        'OBJECTID': 'Int64', 'PLOT': 'Int32', 'TR_SP': 'object', 'TR_DIA': 'Int32', 'TR_CL': 'string[python]',
        'TR_HLTH': 'string[python]', 'TR_UNUS': 'string[python]', 'TR_BDWK': 'string[python]', 'MISC': 'string[python]',
        'COL_CREW': 'string[python]', 'COL_DATE': 'datetime64[us]', 'TR_TIME': 'string[python]',
        'MIS_FIELDS': 'string[python]', 'HAS_MIS_FIELD': 'string[python]', 'CANOPY_DBH_FLAG': 'string[python]',
        'VALID_PLOT_ID': 'string[python]', 'HAS_FIXED': 'string[python]', 'METERS_FROM_FIXED_PLOT': 'Float64',
        'CORRECT_PLOT_ID': 'string[python]', 'DUPLICATE': 'string[python]', 'MAST_TYPE': 'string[python]',
        'POOL': 'string[python]', 'COMP': 'string[python]', 'UNIT': 'string[python]', 'SITE': 'string[python]',
        'SID': 'string[python]', 'PID': 'string[python]', 'VALID_SID': 'string[python]',
        'TR_SIZE': 'object', 'VERT_COMP': 'object', 'TR_TYPE': 'object', 'TR_BA': 'float64', 'TR_DENS': 'float64',
        'SP_TYPE': 'object', 'SP_RICH_TYPE': 'object'
    })

    pdt.assert_frame_equal(tree_table, asserted_dataframe)
def test_column_existence():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'

    # Create necessary dataframes
    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)

    asserted_columns = ['OBJECTID', 'PLOT', 'TR_SP', 'TR_DIA', 'TR_CL', 'TR_HLTH', 'TR_UNUS', 'TR_BDWK', 'MISC',
                        'COL_CREW', 'COL_DATE', 'TR_TIME', 'MIS_FIELDS', 'HAS_MIS_FIELD', 'CANOPY_DBH_FLAG',
                        'VALID_PLOT_ID', 'HAS_FIXED', 'METERS_FROM_FIXED_PLOT', 'CORRECT_PLOT_ID', 'DUPLICATE',
                        'MAST_TYPE', 'POOL', 'COMP', 'UNIT', 'SITE', 'SID', 'PID', 'VALID_SID', 'SHAPE', 'TR_SIZE',
                        'VERT_COMP', 'TR_TYPE', 'TR_BA', 'TR_DENS', 'SP_TYPE', 'SP_RICH_TYPE']

    assert set(asserted_columns).issubset(tree_table.columns)
    assert len(asserted_columns) == len(tree_table.columns)

def test_data_types():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'

    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)

    asserted_dtypes = pd.Series({
        'OBJECTID': 'Int64', 'PLOT': 'Int32', 'TR_SP': 'object', 'TR_DIA': 'Int32', 'TR_CL': 'string[python]',
        'TR_HLTH': 'string[python]', 'TR_UNUS': 'string[python]', 'TR_BDWK': 'string[python]', 'MISC': 'string[python]',
        'COL_CREW': 'string[python]', 'COL_DATE': 'datetime64[us]', 'TR_TIME': 'string[python]',
        'MIS_FIELDS': 'string[python]', 'HAS_MIS_FIELD': 'string[python]', 'CANOPY_DBH_FLAG': 'string[python]',
        'VALID_PLOT_ID': 'string[python]', 'HAS_FIXED': 'string[python]', 'METERS_FROM_FIXED_PLOT': 'Float64',
        'CORRECT_PLOT_ID': 'string[python]', 'DUPLICATE': 'string[python]', 'MAST_TYPE': 'string[python]',
        'POOL': 'string[python]', 'COMP': 'string[python]', 'UNIT': 'string[python]', 'SITE': 'string[python]',
        'SID': 'string[python]', 'PID': 'string[python]', 'VALID_SID': 'string[python]', 'SHAPE': 'geometry',
        'TR_SIZE': 'object', 'VERT_COMP': 'object', 'TR_TYPE': 'object', 'TR_BA': 'float64', 'TR_DENS': 'float64',
        'SP_TYPE': 'object', 'SP_RICH_TYPE': 'object'
    })

    tree_table_dtypes = tree_table.dtypes

    assert (asserted_dtypes.loc[tree_table_dtypes.index] == tree_table_dtypes).all()

def test_value_correctness():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'

    # Create necessary dataframes
    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)

    # Grab columns from tree_table and store as lists
    TR_SIZE = tree_table["TR_SIZE"]
    VERT_COMP = tree_table["VERT_COMP"]
    TR_TYPE = tree_table["TR_TYPE"]
    TR_BA = tree_table["TR_BA"]
    TR_DENS = tree_table["TR_DENS"]
    SP_TYPE = tree_table["SP_TYPE"].fillna("NAN")            # String versions of NaN are used because of
    SP_RICH_TYPE = tree_table["SP_RICH_TYPE"].fillna("NAN")  # restrictions on comparing NaN values

    # Define acceptable values for the pulled columns above.
    TR_SIZE_acceptable_values = pd.Series(["Saw", "Pole", "Mature", "Sapling", "Over Mature", None])
    VERT_COMP_acceptable_values = pd.Series(["Canopy", "Midstory", None])
    TR_TYPE_acceptable_values = pd.Series(["Wildlife", "None", None])
    TR_BA_acceptable_values = pd.Series([10, 0.0])
    TR_DENS_low, TR_DENS_high = 0, 1834
    SP_TYPE_acceptable_values = pd.Series(["Common", "Uncommon", "NAN"]) # String versions of NaN are used because of
    SP_RICH_TYPE_acceptable_values = pd.Series(["Typical", "Other", "Hard", "NAN"]) # restrictions on comparing NaN

    # Compare values in lists to acceptable values
    invalid_vals = [val for val in TR_SIZE if val not in TR_SIZE_acceptable_values.values]
    assert not invalid_vals, f"Invalid values found in TR_SIZE: {invalid_vals}"

    invalid_vals = [val for val in VERT_COMP if val not in VERT_COMP_acceptable_values.values]
    assert not invalid_vals, f"Invalid values found in VERT_COMP: {invalid_vals}"

    invalid_vals = [val for val in TR_TYPE if val not in TR_TYPE_acceptable_values.values]
    assert not invalid_vals, f"Invalid values found in TR_TYPE: {invalid_vals}"

    invalid_vals = [val for val in TR_BA if val not in TR_BA_acceptable_values.values]
    assert not invalid_vals, f"Invalid values found in TR_BA: {invalid_vals}"

    invalid_vals = [val for val in TR_DENS if not(TR_DENS_low <= val <= TR_DENS_high)]
    assert not invalid_vals, f"Invalid values found in TR_DENS: {invalid_vals}"

    invalid_vals = [val for val in SP_TYPE if val not in SP_TYPE_acceptable_values.values]
    assert not invalid_vals, f"Invalid values found in SP_TYPE: {invalid_vals}"

    invalid_vals = [val for val in SP_RICH_TYPE if val not in SP_RICH_TYPE_acceptable_values.values]
    assert not invalid_vals, f"Invalid values found in SP_RICH_TYPE: {invalid_vals}"
