# All tool chains should begin by taking in all three observation datasets, then running create_tree_table and
# create_plot_table from forest_calcs. Between these two tables and subsequent functions in forest_calcs the
# majority of summaries should be able to be produced

# Size Class TPA, BA, QM DBH function for plots
# Filter Tree Table for just live trees, calculate plot fields
import sys

import arcpy

# TPA, BA & QM DBH Function Runs for all levels
plot_size_live_tpabaqm = fcalc.tpa_ba_qmdbh_plot_by_case(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]), 'TR_SIZE')
stand_size_live_tpabaqm = fcalc.tpa_ba_qmdbh_level_by_case(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]), 'TR_SIZE', 'SID')
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

# Work on prevalency pattern - need for species, health
# return health code, species code and percent of whole

#Base DF for health
health_df_base = fcalc.tpa_ba_qmdbh_level_by_case_long(tree_table=tree_table,
                                                 filter_statement= None,
                                                 case_column='TR_HLTH',
                                                 level='SID')

# Get Max TPAs
health_df_max = health_df_base.groupby('SID')['TPA'].max().reset_index()

# Join back to base df
health_df_join = health_df_base.merge(health_df_max,
                                      how='inner',
                                      left_on=['SID', 'TPA'],
                                      right_on=['SID', 'TPA'])\
                                .reset_index()

# Add rankings for health codes
conditions = [(health_df_join['TR_HLTH'] == 'H'),(health_df_join['TR_HLTH'] == 'S'),(health_df_join['TR_HLTH'] == 'SD'),(health_df_join['TR_HLTH'] == 'D')]
values = [1, 2, 3, 4]
health_df_join['TR_HLTH_NUM'] = numpy.select(conditions, values)

# sort and drop
health_df_mp = health_df_join.sort_values(by=['SID', 'TR_HLTH_NUM'])
health_df_mp = health_df_mp.drop_duplicates(subset='SID', keep='first')

# rename
health_df_mp = health_df_mp.rename(columns={'TPA': 'HLTH_TPA'})

# Calc overall TPA
overall_tap = fcalc.tpa_ba_qmdbh_level(tree_table=tree_table,
                                       filter_statement=None,
                                       level='SID')

# Drop fields
overall_tap = overall_tap.drop(columns=['tree_count',
                                        'stand_dens',
                                        'plot_count',
                                        'BA',
                                        'QM_DBH',
                                        'index'])

# Set indexes
overall_tap = overall_tap.set_index('SID')
health_df_mp = health_df_mp.set_index('SID')

# Join overall tpa to health table
health_df_mp_pct = health_df_mp.join(overall_tap, how='left')

# Calc Prevalency Percentage field
health_df_mp_pct['HLT_TPA_PCT'] = (health_df_mp_pct['HLTH_TPA'] / health_df_mp_pct['TPA']) * 100


