import fmgpy.fmglib.forest_calcs as fc
def test_fmg_column_reindex_list():
    csv1 = './../../../resources/age_summary_cols.csv'

    assert fc.fmg_column_reindex_list('PID', csv1) == ['POOL', 'COMP', 'UNIT', 'SITE', 'SID', 'PID', 'AGE_ORIG',
                                                       'AGE_DBH', 'AGE_GRW', 'AGE_UND_COV', 'HM_ORIG', 'SM_ORIG',
                                                       'LM_ORIG']
