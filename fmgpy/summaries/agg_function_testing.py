# All tool chains should begin by taking in all three observation datasets, then running create_tree_table and
# create_plot_table from forest_calcs. Between these two tables and subsequent functions in forest_calcs the
# majority of summaries should be able to be produced

# Size Class TPA, BA, QM DBH function for plots
# Filter Tree Table for just live trees, calculate plot fields
import sys

import arcpy

# TPA, BA & QM DBH Function Runs for all levels
plot_size_live_tpabaqm = fcalc.tpa_ba_qmdbh_plot(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]), 'TR_SIZE')
stand_size_live_tpabaqm = fcalc.tpa_ba_qmdbh_level(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]), 'TR_SIZE', 'SID')
site_size_live_tpabaqm = fcalc.tpa_ba_qmdbh_level(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]), 'TR_SIZE', 'SITE')
unit_size_live_tpabaqm = fcalc.tpa_ba_qmdbh_level(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]), 'TR_SIZE', 'UNIT')
plot_size_dead_tpabaqm = fcalc.tpa_ba_qmdbh_plot(tree_table, tree_table.TR_HLTH.isin(["D", "DEAD"]), 'TR_SIZE')
stand_size_dead_tpabaqm = fcalc.tpa_ba_qmdbh_level(tree_table, tree_table.TR_HLTH.isin(["D", "DEAD"]), 'TR_SIZE', 'SID')
site_size_dead_tpabaqm = fcalc.tpa_ba_qmdbh_level(tree_table, tree_table.TR_HLTH.isin(["D", "DEAD"]), 'TR_SIZE', 'SITE')
unit_size_dead_tpabaqm = fcalc.tpa_ba_qmdbh_level(tree_table, tree_table.TR_HLTH.isin(["D", "DEAD"]), 'TR_SIZE', 'UNIT')

plot_health_tpabaqm = fcalc.tpa_ba_qmdbh_plot(tree_table, None, 'TR_HLTH')
stand_health_tpabaqm = fcalc.tpa_ba_qmdbh_level(tree_table, None, 'TR_HLTH', 'SID')
site_health_tpabaqm = fcalc.tpa_ba_qmdbh_level(tree_table, None, 'TR_HLTH', 'SITE')
unit_health_tpabaqm = fcalc.tpa_ba_qmdbh_level(tree_table, None, 'TR_HLTH', 'UNIT')

plot_mast_tpabaqm = fcalc.tpa_ba_qmdbh_plot(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]), 'MAST_TYPE')
stand_mast_tpabaqm = fcalc.tpa_ba_qmdbh_level(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]), 'MAST_TYPE', 'SID')
site_mast_tpabaqm = fcalc.tpa_ba_qmdbh_level(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]), 'MAST_TYPE', 'SITE')
unit_mast_tpabaqm = fcalc.tpa_ba_qmdbh_level(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]), 'MAST_TYPE', 'UNIT')

plot_vert_live_tpabaqm = fcalc.tpa_ba_qmdbh_plot(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]), 'VERT_COMP')
stand_vert_live_tpabaqm = fcalc.tpa_ba_qmdbh_level(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]), 'VERT_COMP', 'SID')
site_vert_live_tpabaqm = fcalc.tpa_ba_qmdbh_level(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]), 'VERT_COMP', 'SITE')
unit_vert_live_tpabaqm = fcalc.tpa_ba_qmdbh_level(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]), 'VERT_COMP', 'UNIT')
plot_vert_dead_tpabaqm = fcalc.tpa_ba_qmdbh_plot(tree_table, tree_table.TR_HLTH.isin(["D", "DEAD"]), 'VERT_COMP')
stand_vert_dead_tpabaqm = fcalc.tpa_ba_qmdbh_level(tree_table, tree_table.TR_HLTH.isin(["D", "DEAD"]), 'VERT_COMP', 'SID')
site_vert_dead_tpabaqm = fcalc.tpa_ba_qmdbh_level(tree_table, tree_table.TR_HLTH.isin(["D", "DEAD"]), 'VERT_COMP', 'SITE')
unit_vert_dead_tpabaqm = fcalc.tpa_ba_qmdbh_level(tree_table, tree_table.TR_HLTH.isin(["D", "DEAD"]), 'VERT_COMP', 'UNIT')


# general descriptive table function runs for all levels
plot_general_descriptive =

