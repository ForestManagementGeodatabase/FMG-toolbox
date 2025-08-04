import fmgpy.fmglib.forest_calcs as fcalc
import pandas as pd

def test_dataframe_size():
    prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
    filter_statement = None

    prism_df = pd.DataFrame.spatial.from_featureclass(prism)
    tree_table = fcalc.create_tree_table(prism_df)
    hdp_table = fcalc.health_dom_plot(tree_table, filter_statement)

    #TODO: Write test for the correct number of rows. This could be converted to an end-to-end-test of the function,
    # testing the entire dataframe after several different filter statements.
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