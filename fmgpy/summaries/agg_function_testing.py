# All tool chains should begin by taking in all three observation datasets, then running create_tree_table and
# create_plot_table from forest_calcs. Between these two tables and subsequent functions in forest_calcs the
# majority of summaries should be able to be produced

# Size Class TPA, BA, QM DBH function for plots
# Filter Tree Table for just live trees, calculate plot fields
import sys

import arcpy



def tpa_ba_qmdbh_plot(tree_table, filter_statement, group_column):
    # Example filter statement: ~tree_table.TR_HLTH.isin(["D", "DEAD"])

    # Ensure group_column parameter is supplied
    if group_column is not None:
        pass
    elif group_column is None:
        arcpy.AddMessage('Group column must be defined')
        sys.exit()

    # Test for filter statement and run script based on filter or no filter
    if filter_statement is not None:

        filtered_df = tree_table[filter_statement] \
            .groupby(['PID', group_column], as_index=False) \
            .agg(
                tree_count=('TR_SP', agg_tree_count),
                plot_count=('PID', agg_plot_count),
                tpa=('TR_DENS', sum),
                ba=('TR_BA', sum)
            )

        # Add and Calculate QM DBH
        filtered_df['qm_dbh'] = qm_dbh(filtered_df['ba'], filtered_df['tpa'])

        # Pivot sizes and metrics to columns
        out_dataframe = filtered_df\
            .pivot_table(
                index='PID',
                columns=group_column,
                values=['ba', 'tpa', 'qm_dbh'],
                fill_value=0)\
            .reset_index()

        # flatten column multi index
        out_dataframe.columns = list(map("_".join, out_dataframe.columns))

        return out_dataframe

    elif filter_statement is None:
        filtered_df = tree_table \
            .groupby(['PID', group_column], as_index=False) \
            .agg(
                tree_count=('TR_SP', agg_tree_count),
                plot_count=('PID', agg_plot_count),
                tpa=('TR_DENS', sum),
                ba=('TR_BA', sum)
            )

        # Add and Calculate QM DBH
        filtered_df['qm_dbh'] = qm_dbh(filtered_df['ba'], filtered_df['tpa'])

        # Pivot sizes and metrics to columns
        out_dataframe = filtered_df \
            .pivot_table(
                index='PID',
                columns=group_column,
                values=['ba', 'tpa', 'qm_dbh'],
                fill_value=0) \
            .reset_index()

        # flatten column multi index
        out_dataframe.columns = list(map("_".join, out_dataframe.columns))

        return out_dataframe


# Size Class TPA, BA, QM DBH function for levels
stand_live = tree_table[~tree_table.TR_HLTH.isin(["D", "DEAD"])] \
    .groupby(['SID', 'TR_SIZE'], as_index=False) \
    .agg(
    tree_count=('TR_SP', fcalc.agg_tree_count),
    plot_count=('PID', fcalc.agg_plot_count),
    stand_dens=('TR_DENS', sum),
    ba_temp=('TR_BA', sum),
    pool=('POOL', 'first'),
    comp=('COMP', 'first'),
    unit=('UNIT', 'first'),
    site=('SITE', 'first'),
)

# Add and calculate TPA, BA, QM_DBH
stand_live['TPA'] = stand_live['stand_dens'] / stand_live['plot_count']
stand_live['BA'] = (stand_live['tree_count'] * 10) / stand_live['plot_count']
stand_live['QM_DBH'] = fcalc.qm_dbh(stand_live['BA'], stand_live['TPA'])

# Pivot sizes and metrics to columns
stand_size = stand_live \
    .pivot_table(
    index='SID',
    columns='TR_SIZE',
    values=['BA', 'TPA', 'QM_DBH'],
    fill_value=0) \
    .reset_index()

# flatten column to multi index
stand_size.columns = list(map("_".join, stand_size.columns))
