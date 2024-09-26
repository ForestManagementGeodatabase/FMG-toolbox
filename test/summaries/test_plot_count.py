import pytest
import os
import pandas as pd
import fmgpy.fmglib.forest_calcs
import test.test_data

# Arrange
@pytest.fixture
def fmg_gdb():
    fmg_gdb = os.path.join(test.test_data.data_folder(), "FMG_OracleSchema.gdb")
    return fmg_gdb


@pytest.fixture
def fixed_df(fmg_gdb):
    fixed_fc_path = os.path.join(fmg_gdb, "FIXED_PLOTS")
    fixed_df = pd.DataFrame.spatial.from_featureclass(fixed_fc_path)
    return fixed_df


def test_plot_count(fixed_df):
    plots = fmgpy.fmglib.forest_calcs.plot_count(fixed_df)
    assert isinstance(plots, int)
