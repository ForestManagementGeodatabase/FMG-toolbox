import pytest
import os
import pandas as pd
import fmgpy.test.test_data
import fmgpy.fmglib.forest_calcs


# Arrange
@pytest.fixture
def fmg_gdb():
    fmg_gdb = os.path.join(fmgpy.test.test_data.data_folder(), "Pool12.gdb")
    return fmg_gdb


@pytest.fixture
def fixed_df(fmg_gdb):
    fixed_fc_path = os.path.join(fmg_gdb, "Fixed")
    fixed_df = pd.DataFrame.spatial.from_featureclass(fixed_fc_path)
    return fixed_df


def test_cover_pct(fixed_df):
    cover_pct_df = fmgpy.fmglib.forest_calcs.cover_pct(fixed_df, "site")
    assert isinstance(cover_pct_df, pd.DataFrame)
