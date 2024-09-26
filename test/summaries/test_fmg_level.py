import fmgpy.fmglib.forest_calcs


def test_fmg_level():
    assert fmgpy.fmglib.forest_calcs.fmg_level("unit") == "UNIT"
    assert fmgpy.fmglib.forest_calcs.fmg_level("site") == "SITE"
    assert fmgpy.fmglib.forest_calcs.fmg_level("stand") == "SID"
    assert fmgpy.fmglib.forest_calcs.fmg_level("plot") == "PID"
