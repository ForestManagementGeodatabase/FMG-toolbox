import fmgpy.fmglib.forest_calcs as fc


def test_fmg_level():
    assert fc.fmg_level("unit") == "UNIT"
    assert fc.fmg_level("site") == "SITE"
    assert fc.fmg_level("stand") == "SID"
    assert fc.fmg_level("plot") == "PID"
