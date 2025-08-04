import fmgpy.fmglib.forest_calcs as fcalc
import pandas as pd

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