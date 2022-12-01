import pytest
import os
import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import pandas as pd
import fmgpy.summaries.forest_calcs


def test_float():
    tpa_2 = pd.DataFrame({"PLOT": [1], "TR_SP": ["ACSA2"], "TR_DIA": [3]})
    # density = (baf [10] / (0.00545 * df_prism['TR_DIA'].mean() [3] ** 2))
    tpa_float = fmgpy.summaries.forest_calcs.tpa(tpa_2)
    assert isinstance(tpa_float, float)


def test_ba_0_plots_0_trees():
    tpa_0 = pd.DataFrame({"PLOT": [], "TR_SP": [], "TR_DIA": []})
    # density = (baf [10] / (0.00545 * df_prism['TR_DIA'].mean() [3] ** 2))
    assert fmgpy.summaries.forest_calcs.tpa(tpa_0) == None


def test_ba_1_plots_0_trees():
    tpa_1 = pd.DataFrame({"PLOT": [1], "TR_SP": [""], "TR_DIA": [0]})
    # density = (baf [10] / (0.00545 * df_prism['TR_DIA'].mean() [3] ** 2))
    assert fmgpy.summaries.forest_calcs.tpa(tpa_1) == 0


def test_ba_1_plot_1_trees():
    tpa_2 = pd.DataFrame({"PLOT": [1], "TR_SP": ["ACSA2"], "TR_DIA": [10]})
    # density = (baf [10] / (0.00545 * df_prism['TR_DIA'].mean() [10] ** 2))
    assert fmgpy.summaries.forest_calcs.tpa(tpa_2) == 10


def test_ba_1_plot_2_trees():
    tpa_3 = pd.DataFrame({"PLOT": [1, 1], "TR_SP": ["ACSA2", "ACSA2"], "TR_DIA": [5, 15]})
    # density = (baf [10] / (0.00545 * df_prism['TR_DIA'].mean() [10] ** 2))
    assert fmgpy.summaries.forest_calcs.tpa(tpa_3) == 20


def test_ba_1_plot_3_trees():
    tpa_4 = pd.DataFrame({"PLOT": [1, 1, 1],
                         "TR_SP": ["ACSA2", "ACSA2", "ACSA2"],
                         "TR_DIA": [5, 15, 10]})
    # density = (baf [10] / (0.00545 * df_prism['TR_DIA'].mean() [10] ** 2))
    assert fmgpy.summaries.forest_calcs.tpa(tpa_4) == 30


def test_ba_2_plots_1_tree():
    tpa_7 = pd.DataFrame({"PLOT": [1, 2, 2],
                         "TR_SP": ["ACSA2", "NONE", ""],
                         "TR_DIA": [5, 15, 10]})
    # density = (baf [10] / (0.00545 * df_prism['TR_DIA'].mean() [3] ** 2))
    assert fmgpy.summaries.forest_calcs.tpa(tpa_7) == 5


def test_ba_2_plots_2_trees():
    tpa_5 = pd.DataFrame({"PLOT": [1, 2], "TR_SP": ["ACSA2", "ACSA2"], "TR_DIA": [15, 10]})
    # density = (baf [10] / (0.00545 * df_prism['TR_DIA'].mean() [3] ** 2))
    assert fmgpy.summaries.forest_calcs.tpa(tpa_5) == 10


def test_ba_2_plots_3_trees():
    tpa_6 = pd.DataFrame({"PLOT": [1, 2, 2],
                         "TR_SP": ["ACSA2", "ACSA2", "ACSA2"],
                         "TR_DIA": [5, 15, 10]})
    # density = (baf [10] / (0.00545 * df_prism['TR_DIA'].mean() [3] ** 2))
    assert fmgpy.summaries.forest_calcs.tpa(tpa_6) == 15


def test_ba_3_plots_3_trees():
    tpa_7 = pd.DataFrame({"PLOT": [1, 2, 3],
                         "TR_SP": ["ACSA2", "ACSA2", "ACSA2"],
                         "TR_DIA": [5, 15, 10]})
    # density = (baf [10] / (0.00545 * df_prism['TR_DIA'].mean() [3] ** 2))
    assert fmgpy.summaries.forest_calcs.tpa(tpa_7) == 10