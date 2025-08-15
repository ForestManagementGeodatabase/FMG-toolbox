import fmgpy.fmglib.forest_calcs as fcalc
import pandas as pd
import pandas.testing as pdt

def test_itself():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)

    # Establish aliases for appropriate folders
    csv_folder_path = './dataframe_test_csvs/species_dom_level/'
    none_pid_csv = csv_folder_path + 'none_pid.csv'
    vertComp_pool_csv = csv_folder_path + 'vertComp_pool.csv'

    # create dataframe with no filter
    filter_statement = None
    none_pid_df = fcalc.species_dom_level(tree_table, filter_statement, 'PID')
    #none_pid_df.to_csv(none_pid_csv, index=False) # Uncomment to generate new csvs

    # create dataframe with filter on VERT_COMP
    filter_statement = tree_table.VERT_COMP == 'Midstory'
    vertComp_pool_df = fcalc.species_dom_level(tree_table, filter_statement, 'POOL')
    #vertComp_pool_df.to_csv(vertComp_pool_csv, index=False) # Uncomment to generate new csvs

    # Read dataframes from csvs
    none_pid_csv_df = pd.read_csv(none_pid_csv)
    vertComp_pool_csv_df = pd.read_csv(vertComp_pool_csv)

    # Make dataframes from csvs have correct datatypes
    none_pid_csv_df = none_pid_csv_df.astype({
        'PID': 'string[python]', 'SP_DOM': 'object', 'SP_DOM_PCMP': 'float64'
    })
    vertComp_pool_csv_df = vertComp_pool_csv_df.astype({
        'POOL': 'string[python]', 'SP_DOM': 'object', 'SP_DOM_PCMP': 'float64'
    })

    none_pid_csv_df = none_pid_csv_df.replace('', pd.NA)
    none_pid_df = none_pid_df.replace('', pd.NA)
    vertComp_pool_csv_df = vertComp_pool_csv_df.replace('', pd.NA)
    vertComp_pool_df = vertComp_pool_df.replace('', pd.NA)

    # Compare function output stored in csv to current function behavior.
    pdt.assert_frame_equal(none_pid_csv_df, none_pid_df)
    pdt.assert_frame_equal(vertComp_pool_csv_df, vertComp_pool_df)
def test_dataframe_size():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    filter_statement = None
    level = 'SID'

    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)
    sdl_table = fcalc.species_dom_level(tree_table, filter_statement, level)

    #TODO: Write test for the correct number of rows. This could be converted to an end-to-end-test of the function,
    # testing the entire dataframe after several different filter statements.
def test_column_existence():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    filter_statement = None
    level = 'SID'

    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)
    sdl_table = fcalc.species_dom_level(tree_table, filter_statement, level)

    asserted_columns = ['SID', 'SP_DOM', 'SP_DOM_PCMP']

    assert set(asserted_columns).issubset(sdl_table.columns)
    assert len(asserted_columns) == len(sdl_table.columns)

def test_data_types():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    filter_statement = None
    level = 'SID'

    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)
    sdl_table = fcalc.species_dom_level(tree_table, filter_statement, level)

    asserted_dtypes = pd.Series({
        'SID': 'string[python]', 'SP_DOM': 'object', 'SP_DOM_PCMP': 'float64'
    })

    assert (asserted_dtypes.loc[sdl_table.dtypes.index] == sdl_table.dtypes).all()