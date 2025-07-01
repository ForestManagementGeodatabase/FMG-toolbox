import fmgpy.fmglib.forest_calcs as fc

def test_fmg_dtype_enforce():

    csv1 = './../../../resources/age_summary_cols.csv'
    csv2 = './../../../resources/management_summary_cols.csv'

    csv1_dict = {
        'AGE_ORIG' : 'int32',
        'AGE_DBH' : 'int32',
        'AGE_GRW' : 'int32',
        'AGE_UND_COV' : 'int32',
        'HM_ORIG' : 'int32',
        'SM_ORIG' : 'int32',
        'LM_ORIG' : 'int32'
    }

    csv2_dict = {
        'STOCK_PCT' : 'float64',
        'STOCK_PCT_HM' : 'float64',
        'COMP_SP_RICH' : 'string',
        'SP_RICH' : 'float64'
    }


    assert fc.fmg_dtype_enforce(csv1) == csv1_dict;
    assert fc.fmg_dtype_enforce(csv2) == csv2_dict;
