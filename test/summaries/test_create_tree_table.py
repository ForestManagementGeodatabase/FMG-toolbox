import pytest
import os
import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import pandas as pd
import fmgpy.summaries.forest_calcs

# Arrange
@pytest.fixture
def fmg_gdb():
    fmg_gdb = os.path.join(test.test_data.data_folder(), "FMG_OracleSchema.gdb")
    return fmg_gdb


@pytest.fixture
def prism_df(fmg_gdb):
    prism_fc_path = os.path.join(fmg_gdb, "PRISM_PLOTS")
    prism_df = pd.DataFrame.spatial.from_featureclass(prism_fc_path)
    return prism_df
