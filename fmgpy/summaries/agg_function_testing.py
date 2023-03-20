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
def tpa_ba_qmdbh_level(tree_table, filter_statement, group_column, level):

    # Check input parameters are valid
    assert isinstance(tree_table, pd.DataFrame), "must be a pandas DataFrame"
    assert tree_table.columns.isin([group_column]).any(), "df must contain column specified as group column param"
    assert tree_table.columns.isin([level]).any(), "df must contain column specified as level param"

    # Test for filter statement and run script based on filter or no filter
    if filter_statement is not None:

        # Filter, group and sum tree table
        filtered_df = tree_table[filter_statement] \
            .groupby([level, group_column], as_index=False) \
            .agg(
                tree_count=('TR_SP', agg_tree_count),
                plot_count=('PID', agg_plot_count),
                stand_dens=('TR_DENS', sum)
            )

        # Add and calculate TPA, BA, QM_DBH
        baf = 10
        filtered_df['TPA'] = filtered_df['stand_dens'] / filtered_df['plot_count']
        filtered_df['BA'] = (filtered_df['tree_count'] * baf) / filtered_df['plot_count']
        filtered_df['QM_DBH'] = qm_dbh(filtered_df['BA'], filtered_df['TPA'])

        # Pivot sizes and metrics to columns
        out_dataframe = filtered_df \
            .pivot_table(
                index=level,
                columns=group_column,
                values=['BA', 'TPA', 'QM_DBH'],
                fill_value=0) \
            .reset_index()

        # flatten column to multi index
        out_dataframe.columns = list(map("_".join, out_dataframe.columns))

        return out_dataframe

    elif filter_statement is None:

        # Group and sum tree table
        filtered_df = tree_table \
            .groupby([level, 'TR_SIZE'], as_index=False) \
            .agg(
                tree_count=('TR_SP', agg_tree_count),
                plot_count=('PID', agg_plot_count),
                stand_dens=('TR_DENS', sum),
            )

        # Add and calculate TPA, BA, QM_DBH
        baf = 10
        filtered_df['TPA'] = filtered_df['stand_dens'] / filtered_df['plot_count']
        filtered_df['BA'] = (filtered_df['tree_count'] * baf) / filtered_df['plot_count']
        filtered_df['QM_DBH'] = qm_dbh(filtered_df['BA'], filtered_df['TPA'])

        # Pivot sizes and metrics to columns
        out_dataframe = filtered_df \
            .pivot_table(
                index=level,
                columns=group_column,
                values=['BA', 'TPA', 'QM_DBH'],
                fill_value=0) \
            .reset_index()

        # flatten column to multi index
        out_dataframe.columns = list(map("_".join, out_dataframe.columns))

        return out_dataframe

