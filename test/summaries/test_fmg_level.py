import pytest
import os
import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import pandas as pd
import fmgpy.summaries.forest_calcs


def test_fmg_level():
    assert fmgpy.summaries.forest_calcs.fmg_level("unit") == "UNIT"
    assert fmgpy.summaries.forest_calcs.fmg_level("site") == "SITE"
    assert fmgpy.summaries.forest_calcs.fmg_level("stand") == "SID"
    assert fmgpy.summaries.forest_calcs.fmg_level("plot") == "PID"
