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

# Determine top 5 overstory species and generate associated statistics
def top5_ov_species_plot(tree_table):
    """ Creates a dataframe with the top 5 overstory species and associated statistics (BA, TPA, QM DBH, Dom. Health,
    Dom. Health % Composition, Dom. Health TPA, and Dead TPA) for each of the top 5 species

    Keyword Args:
          tree_table -- dataframe: input tree_table, produced by create_tree_table function
          level      -- string: field name for desired FMG level, i.e. SID, SITE, UNIT

    Details: None
    """
    # Create table with TPA for each unique species per given level
    species_df = tpa_ba_qmdbh_plot_by_case_long(tree_table=tree_table,
                                                 filter_statement=None,
                                                 case_column='TR_SP')

    # Remove rows with a tree species of None or NoTree
    species_df = species_df[species_df.TR_SP != "NONE"]

    # Sort species_df by plot and TPA
    species_df = species_df.sort_values(by=['PID', 'TPA'], ascending=False)

    # Rank each species within a single plot group, based on sort
    species_df['SP_RANK'] = species_df.groupby(['PID']).cumcount().add(1)

    # Filter on keep flag field where the value is less than or equal to 5
    species_df = species_df[species_df.SP_RANK <= 5]

    # Assign categorical variable for species rank to assist in pivot column naming
    species_df['OV_SP_RANK'] = species_df['SP_RANK'].map(overstory_sp_map)

    # Pivot variables based on sp rank field
    species_pivot_df2 = species_df.pivot(index='PID', columns='OV_SP_RANK', values=['TR_SP', 'BA', 'TPA', 'QM_DBH'])

    # flatten multi index and rename columns
    species_pivot_df2.columns = ['_'.join(col) for col in species_pivot_df2.columns.values]

    # reset index
    species_pivot_df2 = species_pivot_df2.reset_index()

    # Rename columns
    ov_species = species_pivot_df2 \
        .rename(columns={
                'TR_SP_OV_SP1': 'OV_SP1',
                'BA_OV_SP1': 'OV_SP1_BA',
                'TPA_OV_SP1': 'OV_SP1_TPA',
                'QM_DBH_OV_SP1': 'OV_SP1_QMDBH',
                'TR_SP_OV_SP2': 'OV_SP2',
                'BA_OV_SP2': 'OV_SP2_BA',
                'TPA_OV_SP2': 'OV_SP2_TPA',
                'QM_DBH_OV_SP2': 'OV_SP2_QMDBH',
                'TR_SP_OV_SP3': 'OV_SP3',
                'BA_OV_SP3': 'OV_SP3_BA',
                'TPA_OV_SP3': 'OV_SP3_TPA',
                'QM_DBH_OV_SP3': 'OV_SP3_QMDBH',
                'TR_SP_OV_SP4': 'OV_SP4',
                'BA_OV_SP4': 'OV_SP4_BA',
                'TPA_OV_SP4': 'OV_SP4_TPA',
                'QM_DBH_OV_SP4': 'OV_SP4_QMDBH',
                'TR_SP_OV_SP5': 'OV_SP5',
                'BA_OV_SP5': 'OV_SP5_BA',
                'TPA_OV_SP5': 'OV_SP5_TPA',
                'QM_DBH_OV_SP5': 'OV_SP5_QMDBH'})

    # Create iterator dict for sp 1-5
    species_columns = ['OV_SP1', 'OV_SP2', 'OV_SP3', 'OV_SP4', 'OV_SP5']
    iterator_lists = []
    for sp in species_columns:
        # filter out nan values
        ov_species_filtered = ov_species.dropna(subset=[sp])

        # Convert filtered df to a list of lists
        iterator = ov_species_filtered[['PID', sp]].values.tolist()

        # Append list to the iterator list
        iterator_lists.append(iterator)

    # Convert iterator list to dict so lists can be accessed by species rank
    iterator_dict = dict(zip(species_columns, iterator_lists))

    # iterate through the dict doing a bunch of stuff
    for key, value in iterator_dict.items():

        # Create empty list to hold results of loop
        health_prev_list = []

        # Iterate through value list
        for item in value:

            # filter tree table to a single stand
            tree_table_plot = tree_table.loc[tree_table['PID'] == item[0]]

            # Run health prev plot function with single stand associated species
            health_prev_plot = health_prev_pct_plot(tree_table=tree_table_plot,
                                                      filter_statement=tree_table_plot['TR_SP'] == item[1])

            # Convert dataframe to list - contains pid, dom health, % comp
            health_prev_plot_list = health_prev_plot.values.tolist()[0]

            # Filter tree table to just dom health trees
            tree_table_dom_hlth = tree_table_plot[(tree_table_plot['TR_HLTH'] == health_prev_plot_list[1]) &
                                                   (tree_table_plot['TR_SP'] == item[1])]

            # Calculate TPA for just dom health trees
            dom_hlth_tpa = tpa_ba_qmdbh_plot(tree_table=tree_table_dom_hlth,
                                              filter_statement=None)

            # Convert dom health tpa dataframe to list and insert into dom health list
            if len(dom_hlth_tpa.index) == 0:
                health_prev_plot_list.insert(3, 0)
            else:
                dom_hlth_tpa_list = dom_hlth_tpa.values.tolist()[0]
                health_prev_plot_list.insert(3, dom_hlth_tpa_list[5])

            # Filter tree table to just dead trees
            tree_table_dead = tree_table_plot[(tree_table_plot['TR_HLTH'] == 'D') &
                                               (tree_table_plot['TR_SP'] == item[1])]

            # Calcualte TPA for just dead trees
            dead_hlth_tpa = tpa_ba_qmdbh_plot(tree_table=tree_table_dead,
                                               filter_statement=None)

            # Convert dead health tpa dataframe to list
            if len(dead_hlth_tpa.index) == 0:
                health_prev_plot_list.insert(4, 0)
            else:
                dead_hlth_tpa_list = dead_hlth_tpa.values.tolist()[0]
                health_prev_plot_list.insert(4, dead_hlth_tpa_list[5])

            # Add health prev list to loop result list
            health_prev_list.append(health_prev_plot_list)

        # convert loop result list to dataframe
        health_prev_ovsp = pd.DataFrame(health_prev_list, columns=[level,
                                                                   key+'_HLTH_PREV',
                                                                   key+'_HLTH_PREV_PCT',
                                                                   key+ '_HLTH_PREV_TPA',
                                                                   key+ '_D_TPA'])

        # Join dataframe to OV_SPECIES dataframe
        ov_species = ov_species.set_index('PID').join(health_prev_ovsp.set_index('PID'), how='left')
        ov_species = ov_species.reset_index()

    # Re order columns
    ov_species = ov_species.reindex([level,
                                     'OV_SP1', 'OV_SP1_BA', 'OV_SP1_TPA', 'OV_SP1_QMDBH',
                                     'OV_SP1_HLTH_PREV', 'OV_SP1_HLTH_PREV_PCT', 'OV_SP1_HLTH_PREV_TPA', 'OV_SP1_D_TPA',
                                     'OV_SP2', 'OV_SP2_BA', 'OV_SP2_TPA', 'OV_SP2_QMDBH',
                                     'OV_SP2_HLTH_PREV', 'OV_SP2_HLTH_PREV_PCT', 'OV_SP2_HLTH_PREV_TPA', 'OV_SP2_D_TPA',
                                     'OV_SP3','OV_SP3_BA', 'OV_SP3_TPA', 'OV_SP3_QMDBH',
                                     'OV_SP3_HLTH_PREV', 'OV_SP3_HLTH_PREV_PCT', 'OV_SP3_HLTH_PREV_TPA', 'OV_SP3_D_TPA',
                                     'OV_SP4', 'OV_SP4_BA', 'OV_SP4_TPA', 'OV_SP4_QMDBH',
                                     'OV_SP4_HLTH_PREV', 'OV_SP4_HLTH_PREV_PCT', 'OV_SP4_HLTH_PREV_TPA', 'OV_SP4_D_TPA',
                                     'OV_SP5', 'OV_SP5_BA', 'OV_SP5_TPA', 'OV_SP5_QMDBH',
                                     'OV_SP5_HLTH_PREV', 'OV_SP5_HLTH_PREV_PCT', 'OV_SP5_HLTH_PREV_TPA',
                                     'OV_SP5_D_TPA'],
                                    axis="columns")

    return ov_species

# Work out NAN Dtypes
# Import CSV defining tables
col_csv = 'fmgpy/summaries/resources/general_summary_cols_pid.csv'
col_list_df = pd.read_csv(col_csv)

# Create df for just string fill nans
col_list_str = col_list_df[col_list_df['REQ_NAN_STR_FILL'] == 'Yes']
str_dict = None
if len(col_list_str.index) > 0:
    str_cols = col_list_str['COL_NAME'].values.tolist()
    str_vals = col_list_str['VALUE_NAN_STR'].values.tolist()
    str_dict = dict(zip(str_cols, str_vals))


# Create df for just num fill nans
col_list_num = col_list_df[col_list_df['REQ_NAN_NUM_FILL'] == 'Yes']
num_dict = None
if len(col_list_num.index) > 0:
    num_cols = col_list_num['COL_NAME'].values.tolist()
    num_vals = col_list_num['VALUE_NAN_NUM'].values.tolist()
    num_dict = dict(zip(num_cols, num_vals))

if str_dict is None:
    out_dict = num_dict
elif num_dict is None:
    out_dict = str_dict
else:
    out_dict = num_dict | str_dict
