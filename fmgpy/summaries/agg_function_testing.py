# All tool chains should begin by taking in all three observation datasets, then running create_tree_table and
# create_plot_table from forest_calcs. Between these two tables and subsequent functions in forest_calcs the
# majority of summaries should be able to be produced

# Size Class TPA, BA, QM DBH function for plots
# Filter Tree Table for just live trees, calculate plot fields
import sys

import arcpy

# TPA, BA & QM DBH Function Runs for all levels
import pandas as pd

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

# Health Prevalence filters - tree table - still need typical and non-typical runs
sap_prevh_df = fcalc.health_prev_pct_level(tree_table, tree_table['TR_SIZE'] == 'Sapling', level)
pole_prevh_df = fcalc.health_prev_pct_level(tree_table, tree_table['TR_SIZE'] == 'Pole', level)
saw_prevh_df = fcalc.health_prev_pct_level(tree_table, tree_table['TR_SIZE'] == 'Saw', level)
mat_prevh_df = fcalc.health_prev_pct_level(tree_table, tree_table['TR_SIZE'] == 'Mature', level)
ovmat_prevh_df = fcalc.health_prev_pct_level(tree_table, tree_table['TR_SIZE'] == 'Over Mature', level)
wildt_prevh_df = fcalc.health_prev_pct_level(tree_table, tree_table['TR_TYPE'] == 'Wildlife', level)
masth_prevh_df = fcalc.health_prev_pct_level(tree_table, tree_table['MAST_TYPE'] == 'Hard', level)
masts_prevh_df = fcalc.health_prev_pct_level(tree_table, tree_table['MAST_TYPE'] == 'Soft', level)
mastl_prevh_df = fcalc.health_prev_pct_level(tree_table, tree_table['MAST_TYPE'] == 'Lightseed', level)
can_prevh_df = fcalc.health_prev_pct_level(tree_table, tree_table['VERT_COMP'] == 'Canopy', level)
mid_prevh_df = fcalc.health_prev_pct_level(tree_table, tree_table['VERT_COMP'] == 'Midstory', level)
int_prevh_df = fcalc.health_prev_pct_level(tree_table, tree_table['TR_CL'] == 'I', level)
ovr_prevht_df = fcalc.health_prev_pct_level(tree_table, None, level)

pl_sap_prevh_df = fcalc.health_prev_pct_plot(tree_table, tree_table['TR_SIZE'] == 'Sapling')
pl_pole_prevh_df = fcalc.health_prev_pct_plot(tree_table, tree_table['TR_SIZE'] == 'Pole')
pl_saw_prevh_df = fcalc.health_prev_pct_plot(tree_table, tree_table['TR_SIZE'] == 'Saw')
pl_mat_prevh_df = fcalc.health_prev_pct_plot(tree_table, tree_table['TR_SIZE'] == 'Mature')
pl_ovmat_prevh_df = fcalc.health_prev_pct_plot(tree_table, tree_table['TR_SIZE'] == 'Over Mature')
pl_wildt_prevh_df = fcalc.health_prev_pct_plot(tree_table, tree_table['TR_TYPE'] == 'Wildlife')
pl_masth_prevh_df = fcalc.health_prev_pct_plot(tree_table, tree_table['MAST_TYPE'] == 'Hard')
pl_masts_prevh_df = fcalc.health_prev_pct_plot(tree_table, tree_table['MAST_TYPE'] == 'Soft')
pl_mastl_prevh_df = fcalc.health_prev_pct_plot(tree_table, tree_table['MAST_TYPE'] == 'Lightseed')
pl_can_prevh_df = fcalc.health_prev_pct_plot(tree_table, tree_table['VERT_COMP'] == 'Canopy')
pl_mid_prevh_df = fcalc.health_prev_pct_plot(tree_table, tree_table['VERT_COMP'] == 'Midstory')
pl_int_prevh_df = fcalc.health_prev_pct_plot(tree_table, tree_table['TR_CL'] == 'I')
pl_ovr_prevht_df = fcalc.health_prev_pct_plot(tree_table, None, level)

# Species prevalence filters - tree table - still need Typical and Non-Typical runs
sap_prevs_df = fcalc.species_prev_pct_level(tree_table, tree_table['TR_SIZE'] == 'Sapling', level)
pole_prevs_df = fcalc.species_prev_pct_level(tree_table, tree_table['TR_SIZE'] == 'Pole', level)
saw_prevs_df = fcalc.species_prev_pct_level(tree_table, tree_table['TR_SIZE'] == 'Saw', level)
mat_prevs_df = fcalc.species_prev_pct_level(tree_table, tree_table['TR_SIZE'] == 'Mature', level)
ovmat_prevs_df = fcalc.species_prev_pct_level(tree_table, tree_table['TR_SIZE'] == 'Over Mature', level)
wildt_prevs_df = fcalc.species_prev_pct_level(tree_table, tree_table['TR_TYPE'] == 'Wildlife', level)
hlthdead_prevs_df = fcalc.species_prev_pct_level(tree_table, tree_table['TR_HLTH'] == 'D', level)
hlthsd_prevs_df = fcalc.species_prev_pct_level(tree_table, tree_table['TR_HLTH'] == 'SD', level)
hlths_prevs_df = fcalc.species_prev_pct_level(tree_table, tree_table['TR_HLTH'] == 'S', level)
hlthh_prevs_df = fcalc.species_prev_pct_level(tree_table, tree_table['TR_HLTH'] == 'H', level)
masth_prevs_df = fcalc.species_prev_pct_level(tree_table, tree_table['MAST_TYPE'] == 'Hard', level)
masts_prevs_df = fcalc.species_prev_pct_level(tree_table, tree_table['MAST_TYPE'] == 'Soft', level)
mastl_prevs_df = fcalc.species_prev_pct_level(tree_table, tree_table['MAST_TYPE'] == 'Lightseed', level)
can_prevs_df = fcalc.species_prev_pct_level(tree_table, tree_table['VERT_COMP'] == 'Canopy', level)
mid_prevs_df = fcalc.species_prev_pct_level(tree_table, tree_table['VERT_COMP'] == 'Midstory', level)
int_prevs_df = fcalc.species_prev_pct_level(tree_table, tree_table['TR_CL'] == 'I', level)
ovr_prevs_df = fcalc.species_prev_pct_level(tree_table, None, level)

pl_sap_prevs_df = fcalc.species_prev_pct_plot(tree_table, tree_table['TR_SIZE'] == 'Sapling')
pl_pole_prevs_df = fcalc.species_prev_pct_plot(tree_table, tree_table['TR_SIZE'] == 'Pole')
pl_saw_prevs_df = fcalc.species_prev_pct_plot(tree_table, tree_table['TR_SIZE'] == 'Saw')
pl_mat_prevs_df = fcalc.species_prev_pct_plot(tree_table, tree_table['TR_SIZE'] == 'Mature')
pl_ovmat_prevs_df = fcalc.species_prev_pct_plot(tree_table, tree_table['TR_SIZE'] == 'Over Mature')
pl_wildt_prevs_df = fcalc.species_prev_pct_plot(tree_table, tree_table['TR_TYPE'] == 'Wildlife')
pl_hlthdead_prevs_df = fcalc.species_prev_pct_plot(tree_table, tree_table['TR_HLTH'] == 'D')
pl_hlthsd_prevs_df = fcalc.species_prev_pct_plot(tree_table, tree_table['TR_HLTH'] == 'SD')
pl_hlths_prevs_df = fcalc.species_prev_pct_plot(tree_table, tree_table['TR_HLTH'] == 'S')
pl_hlthh_prevs_df = fcalc.species_prev_pct_plot(tree_table, tree_table['TR_HLTH'] == 'H')
pl_masth_prevs_df = fcalc.species_prev_pct_plot(tree_table, tree_table['MAST_TYPE'] == 'Hard')
pl_masts_prevs_df = fcalc.species_prev_pct_plot(tree_table, tree_table['MAST_TYPE'] == 'Soft')
pl_mastl_prevs_df = fcalc.species_prev_pct_plot(tree_table, tree_table['MAST_TYPE'] == 'Lightseed')
pl_can_prevs_df = fcalc.species_prev_pct_plot(tree_table, tree_table['VERT_COMP'] == 'Canopy')
pl_mid_prevs_df = fcalc.species_prev_pct_plot(tree_table, tree_table['VERT_COMP'] == 'Midstory')
pl_int_prevs_df = fcalc.species_prev_pct_plot(tree_table, tree_table['TR_CL'] == 'I')
pl_ovr_prevs_df = fcalc.species_prev_pct_plot(tree_table, None)

TR_SP = [Typical Species]
TR_SP = [Non Typical Species]

# Species Richness working
# inputs : tree_table, plot_table level

# Generate TPA, BA, QM DBH given a case field at non-PID level (no pivot, stays long)
def tpa_ba_qmdbh_level_by_multi_case_long(tree_table, filter_statement, case_columns, level):
    """Creates a dataframe with BA, TPA and QM DBH columns at a specified level. The function does not pivot
    on the case field, instead leaving it in long form. Each row of the resulting dataframe will be a single
    instance of a level and case, with just 3 columns for TPA, BA and QMDBH

    Keyword Args:
        tree_table       -- dataframe: input tree_table, produced by the create_tree_table function
        filter_statement -- pandas method: filter statement to be used on the input dataframe, should be a full filter
                            statement i.e. dataframe.field.filter. If no filter is required, None should be supplied.
        case_column      -- string: field name for groupby  method, ba, tpa and qm dbh will be
                            calculated for each category in this field
        level            -- string: field name for desired FMG level, i.e. SID, SITE, UNIT

    Details: filter statement should not be a string, rather just the pandas dataframe filter statement:
    for live trees use: ~tree_table.TR_HLTH.isin(["D", "DEAD"])
    for dead trees use: tree_table.TR_HLTH.isin(["D", "DEAD"])
    if no filter is required, None should be passed in as the keyword argument.
    """

    # Check input parameters are valid
    assert isinstance(tree_table, pd.DataFrame), "must be a pandas DataFrame"
    assert tree_table.columns.isin([case_column]).any(), "df must contain column specified as group column param"
    assert tree_table.columns.isin([level]).any(), "df must contain column specified as level param"

    # Create data frame that preserves unfiltered count of plots by level
    plotcount_df = tree_table \
        .groupby(level, as_index=False) \
        .agg(Plot_Count=('PID', agg_plot_count)) \
        .set_index(level)

    # Add level to case columns
    case_columns.insert(0, level)

    # Test for filter statement and run script based on filter or no filter
    if filter_statement is not None:

        # Filter, group and sum tree table, add unfiltered plot count field
        filtered_df = tree_table[filter_statement] \
            .groupby(by=case_columns, as_index=False) \
            .agg(
                Tree_Count=('TR_SP', agg_tree_count),
                Stand_Dens=('TR_DENS', sum)
            ) \
            .set_index(level) \
            .merge(right=plotcount_df,
                   how='left',
                   on=level) \
            .reset_index()

        # Add and calculate TPA, BA, QM_DBH
        baf = 10
        filtered_df['TPA'] = filtered_df['Stand_Dens'] / filtered_df['Plot_Count']
        filtered_df['BA'] = (filtered_df['Tree_Count'] * baf) / filtered_df['Plot_Count']
        filtered_df['QM_DBH'] = qm_dbh(filtered_df['BA'], filtered_df['TPA'])

        # Join results back to full set of level polygons
        out_df = plotcount_df \
            .merge(right=filtered_df,
                   how='inner',
                   on=level) \
            .reset_index()

        return out_df

    elif filter_statement is None:

        # Group and sum tree table
        filtered_df = tree_table \
            .groupby(by=case_columns, as_index=False) \
            .agg(
                Tree_Count=('TR_SP', agg_tree_count),
                Stand_Dens=('TR_DENS', sum),
            ) \
            .set_index(level) \
            .merge(right=plotcount_df,
                   how='left',
                   on=level) \
            .reset_index()

        # Add and calculate TPA, BA, QM_DBH
        baf = 10
        filtered_df['TPA'] = filtered_df['Stand_Dens'] / filtered_df['Plot_Count']
        filtered_df['BA'] = (filtered_df['Tree_Count'] * baf) / filtered_df['Plot_Count']
        filtered_df['QM_DBH'] = qm_dbh(filtered_df['BA'], filtered_df['TPA'])

        # Join results back to full set of level polygons and fill nan with 0
        out_df = plotcount_df \
            .merge(right=filtered_df,
                   how='left',
                   on=level) \
            .reset_index()

        return out_df











