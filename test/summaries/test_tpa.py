import pytest
import os
import arcpy
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import pandas as pd
import fmgpy.summaries.forest_calcs


def test_float():
    tpa_2 = pd.DataFrame({"PLOT": [1],
                          "TR_SP": ["ACSA2"],
                          "TR_DIA": [3]})
    # density = sum of BAF [10] / Tree Basal Area (.005454 x DBH^2) [0.05] / Plots [1] = 100
    tpa_float = fmgpy.summaries.forest_calcs.tpa(tpa_2)
    assert isinstance(tpa_float, float)


def test_tpa_0_plots_0_trees():
    tpa_0 = pd.DataFrame({"PLOT": [],
                          "TR_SP": [],
                          "TR_DIA": []})
    # density = sum of BAF [10] / Tree Basal Area (.005454 x DBH^2) [0.05] / Plots [1]
    assert fmgpy.summaries.forest_calcs.tpa(tpa_0) is None


def test_tpa_1_plots_0_trees():
    tpa_1 = pd.DataFrame({"PLOT": [1],
                          "TR_SP": [""],
                          "TR_DIA": [0]})
    # density = sum of BAF [10] / Tree Basal Area (.005454 x DBH^2) [0.05] / Plots [1]
    assert fmgpy.summaries.forest_calcs.tpa(tpa_1) == 0


def test_tpa_1_plot_1_trees():
    tpa_2 = pd.DataFrame({"PLOT": [1],
                          "TR_SP": ["ACSA2"],
                          "TR_DIA": [10]})
    # density = sum of BAF [10] / Tree Basal Area (.005454 x DBH^2) [0.05] / Plots [1]
    density = fmgpy.summaries.forest_calcs.tpa(tpa_2)
    assert round(density, 2) == 18.34


def test_tpa_1_plot_2_trees():
    tpa_3 = pd.DataFrame({"PLOT": [1, 1],
                          "TR_SP": ["ACSA2", "ACSA2"],
                          "TR_DIA": [5, 15]})
    # density = sum of BAF [10] / Tree Basal Area (.005454 x DBH^2) [0.05] / Plots [1]
    density = fmgpy.summaries.forest_calcs.tpa(tpa_3)
    assert round(density, 2) == 81.49


def test_tpa_2_plots_na_trees():
    tpa_4 = pd.DataFrame({"PLOT": [1, 2, 1],
                          "TR_SP": ["ACSA2", "", "ACSA2"],
                          "TR_DIA": [25, 0, 10]})
    # density = sum of BAF [10] / Tree Basal Area (.005454 x DBH^2) [0.05] / Plots [2]
    density = fmgpy.summaries.forest_calcs.tpa(tpa_4)
    assert round(density, 2) == 10.63


def test_tpa_2_plots_3_trees():
    tpa_5 = pd.DataFrame({"PLOT": [1, 2, 2],
                          "TR_SP": ["ACSA2", "ACSA2", "ACSA2"],
                          "TR_DIA": [5, 5, 30]})
    # density = sum of BAF [10] / Tree Basal Area (.005454 x DBH^2) [0.05] / Plots [2]
    density = fmgpy.summaries.forest_calcs.tpa(tpa_5)
    assert round(density, 2) == 175.20


def test_tpa_2_plots_2_trees():
    tpa_6 = pd.DataFrame({"PLOT": [1, 2],
                          "TR_SP": ["ACSA2", "ACSA2"],
                          "TR_DIA": [15, 10]})
    # density = sum of BAF [10] / Tree Basal Area (.005454 x DBH^2) [0.05] / Plots [2]
    density = fmgpy.summaries.forest_calcs.tpa(tpa_6)
    assert round(density, 2) == 13.24


def test_tpa_2_plots_3_trees():
    tpa_7 = pd.DataFrame({"PLOT": [1, 2, 2],
                          "TR_SP": ["ACSA2", "ACSA2", "ACSA2"],
                          "TR_DIA": [15, 15, 11]})
    # density = sum of BAF [10] / Tree Basal Area (.005454 x DBH^2) [0.05] / Plots [2]
    density = fmgpy.summaries.forest_calcs.tpa(tpa_7)
    assert round(density, 2) == 15.73


def test_tpa_2_plots_11_trees():
    tpa_8 = pd.DataFrame({"PLOT": [1, 1, 1, 1, 1, 1,
                                   2, 2, 2, 2, 2],
                          "TR_SP": ["ACSA2", "ACSA2", "ACSA2", "ACSA2", "ACSA2", "ACSA2",
                                    "ACSA2", "ACSA2", "ACSA2", "ACSA2", "ACSA2"],
                          "TR_DIA": [14.5, 11.2, 8.7, 10.4, 11.1, 7.1,
                                     9.9, 11.4, 13.8, 16.0, 7.9]})
    # density = sum of BAF [10] / Tree Basal Area (.005454 x DBH^2) [0.05] / Plots [2]
    density = fmgpy.summaries.forest_calcs.tpa(tpa_8)
    assert round(density, 2) == 97.38


def test_tpa_3_plots_3_trees():
    tpa_9 = pd.DataFrame({"PLOT": [1, 2, 3],
                          "TR_SP": ["ACSA2", "ACSA2", "ACSA2"],
                          "TR_DIA": [20, 30, 40]})
    # density = sum of BAF [10] / Tree Basal Area (.005454 x DBH^2) [0.05] / Plots [2]
    density = fmgpy.summaries.forest_calcs.tpa(tpa_9)
    assert round(density, 2) == 2.59
