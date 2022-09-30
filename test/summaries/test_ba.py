import pytest
import os
import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import pandas as pd
import test_data
import fmgpy.summaries.forest_calcs


def test_float():
    ba_2 = pd.DataFrame({"PLOT": [1], "TR_SP": ["ACSA2"]})
    ba_float = fmgpy.summaries.forest_calcs.ba(ba_2)
    assert isinstance(ba_float, float)


def test_ba_0_plots_0_trees():
    ba_0 = pd.DataFrame({"PLOT": [], "TR_SP": []})
    # basal area = (tree count = 0 * baf = 10) / plot count = 0 = nan
    assert fmgpy.summaries.forest_calcs.ba(ba_0) == 0


def test_ba_1_plots_0_trees():
    ba_1 = pd.DataFrame({"PLOT": [1], "TR_SP": [""]})
    # basal area = (tree count = 0 * baf = 10) / plot count = 1 = 0
    assert fmgpy.summaries.forest_calcs.ba(ba_1) == 0


def test_ba_1_plot_1_trees():
    ba_2 = pd.DataFrame({"PLOT": [1], "TR_SP": ["ACSA2"]})
    # basal area = (tree count = 1 * baf = 10) / plot count = 1 = 10
    assert fmgpy.summaries.forest_calcs.ba(ba_2) == 10


def test_ba_1_plot_2_trees():
    ba_3 = pd.DataFrame({"PLOT": [1, 1], "TR_SP": ["ACSA2", "ACSA2"]})
    # basal area = (tree count = 2 * baf = 10) / plot count = 1 = 10
    assert fmgpy.summaries.forest_calcs.ba(ba_3) == 20


def test_ba_1_plot_3_trees():
    ba_4 = pd.DataFrame({"PLOT": [1, 1, 1],
                         "TR_SP": ["ACSA2", "ACSA2", "ACSA2"]})
    # basal area = (tree count = 3 * baf = 10) / plot count = 1 = 30
    assert fmgpy.summaries.forest_calcs.ba(ba_4) == 30


def test_ba_2_plots_2_trees():
    ba_5 = pd.DataFrame({"PLOT": [1, 2], "TR_SP": ["ACSA2", "ACSA2"]})
    # basal area = (tree count = 2 * baf = 10) / plot count = 2 = 10
    assert fmgpy.summaries.forest_calcs.ba(ba_5) == 10


def test_ba_2_plots_3_trees():
    ba_6 = pd.DataFrame({"PLOT": [1, 2, 2],
                         "TR_SP": ["ACSA2", "ACSA2", "ACSA2"]})
    # basal area = (tree count = 3 * baf = 10) / plot count = 2 = 15
    assert fmgpy.summaries.forest_calcs.ba(ba_6) == 15


def test_ba_3_plots_3_trees():
    ba_7 = pd.DataFrame({"PLOT": [1, 2, 3],
                         "TR_SP": ["ACSA2", "ACSA2", "ACSA2"]})
    # basal area = (tree count = 3 * baf = 10) / plot count = 3 = 10
    assert fmgpy.summaries.forest_calcs.ba(ba_7) == 10
