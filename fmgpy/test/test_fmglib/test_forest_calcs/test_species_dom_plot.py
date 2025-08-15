import fmgpy.fmglib.forest_calcs as fcalc
import pandas as pd
import pandas.testing as pdt

def test_itself():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)

    # Establish aliases for appropriate folders
    csv_folder_path = './dataframe_test_csvs/species_dom_plot/'
    none_csv = csv_folder_path + 'none.csv'
    vertComp_csv = csv_folder_path + 'vertComp.csv'

    # create dataframe with no filter
    filter_statement = None
    none_df = fcalc.species_dom_plot(tree_table, filter_statement)
    # none_df.to_csv(none_csv, index=False) # Uncomment to generate new csvs

    # create dataframe with filter on VERT_COMP
    filter_statement = tree_table.VERT_COMP == 'Midstory'
    vertComp_df = fcalc.species_dom_plot(tree_table, filter_statement)
    # vertComp_df.to_csv(vertComp_csv, index=False) # Uncomment to generate new csvs

    # Read dataframes from csvs
    none_csv_df = pd.read_csv(none_csv)
    vertComp_csv_df = pd.read_csv(vertComp_csv)

    # Make dataframes from csvs have correct datatypes
    none_csv_df = none_csv_df.astype({
        'PID': 'string[python]', 'SP_DOM': 'object', 'SP_DOM_PCMP': 'float64'
    })
    vertComp_csv_df = vertComp_csv_df.astype({
        'PID': 'string[python]', 'SP_DOM': 'object', 'SP_DOM_PCMP': 'float64'
    })

    # Compare function output stored in csv to current function behavior.
    pdt.assert_frame_equal(none_csv_df, none_df)
    pdt.assert_frame_equal(vertComp_csv_df, vertComp_df)


def test_dataframe_size():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    filter_statement = None

    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)
    sdp_table = fcalc.species_dom_plot(tree_table, filter_statement)

    #TODO: Write test for the correct number of rows. This could be converted to an end-to-end-test of the function,
    # testing the entire dataframe after several different filter statements.
def test_column_existence():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    filter_statement = None

    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)
    sdp_table = fcalc.species_dom_plot(tree_table, filter_statement)

    asserted_columns = ['PID', 'SP_DOM', 'SP_DOM_PCMP']

    assert set(asserted_columns).issubset(sdp_table.columns)
    assert len(asserted_columns) == len(sdp_table.columns)

def test_data_types():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    filter_statement = None

    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)
    sdp_table = fcalc.species_dom_plot(tree_table, filter_statement)

    asserted_dtypes = pd.Series({
        'PID': 'string[python]', 'SP_DOM': 'object', 'SP_DOM_PCMP': 'float64'
    })

    assert (asserted_dtypes.loc[sdp_table.dtypes.index] == sdp_table.dtypes).all()