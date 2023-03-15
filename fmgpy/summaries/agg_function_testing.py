# All tool chains should begin by taking in all three observation datasets, then running create_tree_table and
# create_plot_table from forest_calcs. Between these two tables and subsequent functions in forest_calcs the
# majority of summaries should be able to be produced

# Filter Tree Table for just live trees
tree_live = tree_df[~tree_df.TR_HLTH.isin(["D", "DEAD"])]

# Calculate TPA for each size class
tree_live.groupby(['PID', 'TR_SIZE'], as_index=False).agg(
    tree_count = ('TR_SP', forest_calcs.agg_tree_count),
    plot_count = ('PID', forest_calcs.agg_plot_count),
    tpa = ('TR_DENS', sum)
    ba = ('TR_BA', sum)
)


