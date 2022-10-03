import pytest
import os
import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import pandas as pd
import test.test_data
import fmgpy.summaries.forest_calcs


# Arrange
@pytest.fixture
def fmg_gdb():
    fmg_gdb = os.path.join(test.test_data.data_folder(), "fmg_qad_data.gdb")
    return fmg_gdb


@pytest.fixture
def prism_df(fmg_gdb):
    prism_fc_path = os.path.join(fmg_gdb, "Prism")
    prism_df = pd.DataFrame.spatial.from_featureclass(prism_fc_path)
    return prism_df


def test_ba_prism(prism_df):
    plots = fmgpy.summaries.forest_calcs.plot_count(prism_df)
    ba_0 = fmgpy.summaries.forest_calcs.ba(prism_df, plots)
    assert isinstance(ba_0, float)
