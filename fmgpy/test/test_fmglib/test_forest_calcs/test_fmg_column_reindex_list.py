import fmgpy.fmglib.forest_calcs as fc
def test_fmg_column_reindex_list():
    csv1 = './../../../resources/age_summary_cols.csv'
    csv2 = './../../../resources/health_summary_cols.csv'
    csv3 = './../../../resources/size_summary_cols.csv'

    assert fc.fmg_column_reindex_list('PID', csv1) == ['POOL', 'COMP', 'UNIT', 'SITE', 'SID', 'PID', 'AGE_ORIG',
                                                       'AGE_DBH', 'AGE_GRW', 'AGE_UND_COV', 'HM_ORIG', 'SM_ORIG',
                                                       'LM_ORIG']

    assert fc.fmg_column_reindex_list('SITE', csv2) == ['POOL', 'COMP', 'UNIT', 'SITE', 'DEAD_TPA', 'DEAD_BA',
                                                        'DEAD_QMDBH', 'DEAD_DOM_SP', 'DEAD_DOM_SP_PCMP', 'SD_TPA',
                                                        'SD_BA', 'SD_QMDBH', 'SD_DOM_SP', 'SD_DOM_SP_PCMP', 'STR_TPA',
                                                        'STR_BA', 'STR_QMDBH', 'STR_DOM_SP', 'STR_DOM_SP_PCMP',
                                                        'HLTH_TPA', 'HLTH_BA', 'HLTH_QMDBH', 'HLTH_DOM_SP',
                                                        'HLTH_DOM_SP_PCMP', 'LG_D_TPA', 'DOM_HLTH', 'DOM_HLTH_PCMP',
                                                        'DOM_SP', 'DOM_SP_PCMP', 'TYP_SP_DOM_HLTH',
                                                        'TYP_SP_DOM_HLTH_PCMP', 'TYP_DOM_SP', 'TYP_DOM_SP_PCMP',
                                                        'NTYP_SP_DOM_HLTH', 'NTYP_SP_DOM_HLTH_PCMP', 'NTYP_DOM_SP',
                                                        'NTYP_DOM_SP_PCMP']

    assert fc.fmg_column_reindex_list('POOL', csv3) == ['POOL', 'SAP_TPA', 'SAP_BA', 'SAP_QMDBH', 'SAP_DOM_HLTH',
                                                        'SAP_DOM_HLTH_PCMP', 'SAP_DOM_SP', 'SAP_DOM_SP_PCMP',
                                                        'SAP_D_TPA', 'SAP_D_BA', 'SAP_D_QMDBH', 'POL_TPA', 'POL_BA',
                                                        'POL_QMDBH', 'POL_DOM_HLTH', 'POL_DOM_HLTH_PCMP', 'POL_DOM_SP',
                                                        'POL_DOM_SP_PCMP', 'POL_D_TPA', 'POL_D_BA', 'POL_D_QMDBH',
                                                        'SAW_TPA', 'SAW_BA', 'SAW_QMDBH', 'SAW_DOM_HLTH',
                                                        'SAW_DOM_HLTH_PCMP', 'SAW_DOM_SP', 'SAW_DOM_SP_PCMP',
                                                        'SAW_D_TPA', 'SAW_D_BA', 'SAW_D_QMDBH', 'MAT_TPA', 'MAT_BA',
                                                        'MAT_QMDBH', 'MAT_DOM_HLTH', 'MAT_DOM_HLTH_PCMP', 'MAT_DOM_SP',
                                                        'MAT_DOM_SP_PCMP', 'MAT_D_TPA', 'MAT_D_BA', 'MAT_D_QMDBH',
                                                        'OVM_TPA', 'OVM_BA', 'OVM_QMDBH', 'OVM_DOM_HLTH',
                                                        'OVM_DOM_HLTH_PCMP', 'OVM_DOM_SP', 'OVM_DOM_SP_PCMP',
                                                        'OVM_D_TPA', 'OVM_D_BA', 'OVM_D_QMDBH', 'LWT_TPA', 'LWT_BA',
                                                        'LWT_QMDBH', 'LWT_DOM_HLTH', 'LWT_DOM_HLTH_PCMP', 'LWT_DOM_SP',
                                                        'LWT_DOM_SP_PCMP', 'LWT_D_TPA', 'LWT_D_BA', 'LWT_D_QMDBH']
