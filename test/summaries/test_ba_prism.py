import pytest
import os
import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import pandas as pd
import test_data
import fmgpy.summaries.forest_calcs


# Arrange
@pytest.fixture
def fmg_gdb():
    fmg_gdb = os.path.join(test_data.data_folder(), "fmg_qad_data.gdb")
    return fmg_gdb


@pytest.fixture
def prism_df(fmg_gdb):
    prism_fc_path = os.path.join(fmg_gdb, "Prism")
    prism_df = pd.DataFrame.spatial.from_featureclass(prism_fc_path)
    return prism_df


def test_fmg_gdb(fmg_gdb):
    assert isinstance(fmg_gdb, str)


def test_prism(prism_df):
    assert isinstance(prism_df, pd.DataFrame)


def test_ba_prism(prism_df):
    ba_0 = fmgpy.summaries.forest_calcs.ba(prism_df)
    assert isinstance(ba_0, float)