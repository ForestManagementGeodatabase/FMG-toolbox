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

# Health Prevalence filters - tree table
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
ovr_prevht_df = fcalc.health_prev_pct_level_pcttest(tree_table, None, level)


TR_SP = [Typical Species]
TR_SP = [Non Typical Species]



# Work on prevalency pattern - need for species, health
# return health code, species code and percent of whole
# filter format for param: tree_table['TR_SIZE'] == 'Mature'

# Generate health prevalence and prevalence percentage for level summaries
def health_prev_pct_plot(tree_table, filter_statement):
    """Creates a dataframe with most prevalent health and percentage of total that health category comprises
     for specified level - these metrics are based on TPA for each health category and the subset of trees defined
     by the filter statement.
     The function will accept and apply a filter to determine health prevalence for specific subsets of trees.

    Keyword Args:
        tree_table       -- dataframe: input tree_table, produced by the create_tree_table function
        filter_statement -- pandas method: filter statement to be used on the input dataframe, should be a full filter
                            statement i.e. dataframe.field.filter. If no filter is required, None should be supplied.
        level            -- string: field name for desired FMG level, i.e. SID, SITE, UNIT

    Details: filter statement should not be a string, rather just the pandas dataframe filter statement:
    for live trees use: ~tree_table.TR_HLTH.isin(["D", "DEAD"])
    for dead trees use: tree_table.TR_HLTH.isin(["D", "DEAD"])
    if no filter is required, None should be passed in as the keyword argument.
    """
    # Create DF with filtered TPA at specified level, ignoring health categories
    # TPA from this step will be used to calculate the prevalence percent
    unfilt_tpa_df = tpa_ba_qmdbh_plot(
        tree_table=tree_table,
        filter_statement=filter_statement)

    unfilt_tpa_df = unfilt_tpa_df \
        .drop(
            columns=['index',
                     'tree_count',
                     'plot_count',
                     'BA',
                     'QM_DBH']) \
        .rename(columns={'TPA': 'OVERALL_TPA'}) \
        .set_index('PID')

    # Create DF with filtered TPA
    health_base_df = tpa_ba_qmdbh_plot_by_case_long(
        tree_table=tree_table,
        filter_statement=filter_statement,
        case_column='TR_HLTH')

    # Create DF with max TPA for each level
    health_max_df = health_base_df \
        .groupby('PID') \
        .agg(TPA=('TPA', 'max')) \
        .reset_index()

    # Join max df back to filtered base df on compound key level, TPA
    # The resulting dataframe contains health codes by max tpa, with some edge cases
    health_join_df = health_base_df \
        .merge(
            right=health_max_df,
            how='inner',
            left_on=['PID', 'TPA'],
            right_on=['PID', 'TPA']) \
        .reset_index()

    # Edge cases are where TPAs may be identical between health ratings within a level
    # i.e. level 123 has a health rating of H with a TPA of 5 and S with a TPA of 5.
    # To deal with these cases  we assign a numeric code to each health category, sort the resulting
    # dataframe by those numeric codes then drop duplicate rows by level, keeping the first if duplicates
    # are present. This results in a data frame of most prevalent health, wighted toward the healthiest
    # switching the sort method would result in a data frame of most prevalent health, weighted toward
    # the least healthy

    # Assign numeric ranking codes to each health category
    conditions = [(health_join_df['TR_HLTH'] == 'H'),
                  (health_join_df['TR_HLTH'] == 'S'),
                  (health_join_df['TR_HLTH'] == 'SD'),
                  (health_join_df['TR_HLTH'] == 'D'),
                  (health_join_df['TR_HLTH'] == 'NT')]
    values = [1, 2, 3, 4, 5]
    health_join_df['TR_HLTH_NUM'] = np.select(conditions, values)

    # Sort dataframe by numeric ranking codes
    health_prev_df = health_join_df \
        .sort_values(
            by=['PID', 'TR_HLTH_NUM'])

    # Drop duplicate rows, keeping the first row
    health_prev_df = health_prev_df \
        .drop_duplicates(
            subset='PID',
            keep='first')

    # Rename tpa column and prep for join
    health_prev_df = health_prev_df \
        .rename(columns={'TPA': 'HLTH_TPA'}) \
        .set_index('PID')

    # Join overall TPA to health prevalence table to calculate prevalence percentage
    health_prev_pct_df = health_prev_df \
        .join(
            other=unfilt_tpa_df,
            how='left')

    # Calculate prevalence percentage column
    health_prev_pct_df['HLTH_PREV_PCT'] = (health_prev_pct_df['HLTH_TPA'] / health_prev_pct_df['OVERALL_TPA']) * 100

    # Clean up dataframe for export
    health_prev_pct_df = health_prev_pct_df \
        .drop(columns=['level_0',
                       'index',
                       'tree_count',
                       'stand_dens',
                       'plot_count',
                       'BA',
                       'QM_DBH',
                       'TR_HLTH_NUM',
                       'HLTH_TPA',
                       'OVERALL_TPA']) \
        .rename(columns={'TR_HLTH': 'HLTH_PREV'}) \
        .reset_index()

    return health_prev_pct_df

