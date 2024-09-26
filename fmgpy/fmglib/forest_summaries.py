# Do some imports
import os
import arcpy
import pandas as pd
from fmgpy.fmglib import forest_calcs as fcalc


def general_summary(plot_table, tree_table, out_gdb, level):
    arcpy.AddMessage('--Execute General Description Summary on {0}--'.format(level))
    if level != 'PID':

        # Create base table
        base_df = fcalc.create_level_df(level, plot_table)
        arcpy.AddMessage("    Base DF Created")

        # create total num age trees, total num plots, mean overstory closure, overstory closure std,
        # mean overstory height, overstory height std, mean understory cover, understory cover std,
        # mean understory height, understory height std, invasive species present, invasive species
        # list -- source: plot table
        gendesc = plot_table \
            .groupby([level]) \
            .agg(
                PLOT_CT=('PID', fcalc.agg_plot_count),
                TR_AGE_CT=('AGE_SP', 'count'),
                OV_CLSR_MEAN=('OV_CLSR', 'mean'),
                OV_CLSR_STD=('OV_CLSR', 'std'),
                OV_HT_MEAN=('OV_HT', 'mean'),
                OV_HT_STD=('OV_HT', 'std'),
                UND_COV_MEAN=('UND_COV', 'mean'),
                UND_COV_STD=('UND_COV', 'std'),
                UND_HT_MEAN=('UND_HT2', 'mean'),
                UND_HT_STD=('UND_HT2', 'std'),
                INV_PRESENT=('INV_PRESENT', fcalc.agg_inv_present),
                INV_SP=('INV_SP', fcalc.agg_inv_sp),
                NUM_FIX_NOTES=('FX_MISC', fcalc.agg_count_notes),
                NUM_AGE_NOTES=('AGE_MISC', fcalc.agg_count_notes)
            ) \
            .reset_index() \
            .set_index([level])

        # Add mean under story height category values -- source: plot table
        gendesc['UND_HT_RG'] = gendesc['UND_HT_MEAN'].map(fcalc.und_height_range_map)
        arcpy.AddMessage("    General DF Created")

        #  Calculate TPA & BA for live trees
        tpa_ba_live = fcalc.tpa_ba_qmdbh_level(tree_table=tree_table,
                                               filter_statement=~tree_table.TR_HLTH.isin(["D", "DEAD"]),
                                               level=level)

        # Clean up TPA & BA for live tree dataframe
        tpa_ba_live_df = tpa_ba_live\
            .drop(columns=['tree_count', 'stand_dens', 'plot_count']) \
            .rename(columns={'TPA': 'LIVE_TPA', 'BA': 'LIVE_BA', 'QM_DBH': 'LIVE_QMDBH'}) \
            .set_index(level)
        arcpy.AddMessage("    TPA & BA Live Tree DF Created")

        # Calculate total num trees (all, no filter) -- source: tree table
        tr_all = tree_table \
            .groupby([level]) \
            .apply(fcalc.tree_count)

        # Convert tot num trees series to dataframe
        tr_all_df = pd.DataFrame({level: tr_all.index, 'TR_CT': tr_all.values}).set_index([level])
        arcpy.AddMessage("    Total Tree Count DF Created")

        # Calculate total num live trees -- source: tree table
        tr_live = tree_table[~tree_table.TR_HLTH.isin(["D", "DEAD"])] \
            .groupby([level]) \
            .apply(fcalc.tree_count)

        # Convert tot num live trees series to dataframe
        tr_live_df = pd.DataFrame({level: tr_live.index, 'TR_LV_CT': tr_live.values}).set_index([level])
        arcpy.AddMessage("    Total Live Tree Count DF Created")

        # Calculate total num dead trees -- source: tree table
        tr_dead = tree_table[tree_table.TR_HLTH.isin(["D", "DEAD"])] \
            .groupby([level]) \
            .apply(fcalc.tree_count)

        # Convert total num dead trees series to dataframe
        tr_dead_df = pd.DataFrame({level: tr_dead.index, 'TR_D_CT': tr_dead.values}).set_index([level])
        arcpy.AddMessage("    Total Dead Tree Count DF Created")

        # Average Mean Diameter live trees - tree table
        # Calculate Max DBH and Mean Diameter live trees -- source: tree table
        diam_df = tree_table[~tree_table.TR_HLTH.isin(["D", "DEAD"])] \
            .groupby([level]) \
            .agg(
                LIVE_AMD=('TR_DIA', 'mean'),
                LIVE_MAX_DBH=('TR_DIA', 'max')
            ) \
            .reset_index() \
            .set_index([level])
        arcpy.AddMessage("    AMD and Max DBH for Live Trees DF Created")

        # Calculate collection date
        date_df = tree_table\
            .groupby([level], as_index=False) \
            .agg(
                min_date=('COL_DATE', 'min'),
                max_date=('COL_DATE', 'max')
                )
        date_df['min_year'] = date_df['min_date'].dt.year
        date_df['max_year'] = date_df['max_date'].dt.year
        date_df["INVT_YEAR"] = date_df.apply(lambda x: fcalc.date_range(x["min_year"], x["max_year"]), axis=1)

        # Clean up collection date dataframe
        date_df = date_df.drop(columns=['min_date', 'max_date', 'min_year', 'max_year']).set_index(level)
        arcpy.AddMessage("    Collection Date DF Created")

        # Merge component dataframes onto the base dataframe
        out_df = base_df \
            .join(other=[gendesc,
                         tpa_ba_live_df,
                         tr_all_df,
                         tr_live_df,
                         tr_dead_df,
                         diam_df,
                         date_df],
                  how='left')\
            .reset_index()
        arcpy.AddMessage("    All Component DFs Merged")

        # Reindex output dataframe
        general_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                             col_csv='resources/general_summary_cols.csv')
        out_df = out_df.reindex(labels=general_reindex_cols,
                                axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Handle NaN values appropriately
        nan_fill_dict_level = fcalc.fmg_nan_fill(col_csv='resources/general_summary_cols.csv')

        out_df = out_df\
            .fillna(value=nan_fill_dict_level)\
            .drop(columns=['index'], errors='ignore')\
            .replace({'INV_SP': {"": 'NONE', " ": 'NONE', None: 'NONE'},
                      'INV_PRESENT': {"": 'No', " ": 'No', None: 'No'}})
        arcpy.AddMessage("    Nan Values Filled")

        # Enforce ESRI compatible Dtypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/general_summary_cols.csv')
        out_df = out_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Export to gdb table
        table_name = level + "_General_Summary"
        table_path = os.path.join(out_gdb, table_name)
        out_df.spatial.to_table(location=table_path, sanitize_columns=False)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    elif level == 'PID':

        # Drop unecessary plot table columns
        plot_metrics = plot_table.drop(columns=
                                       ['UND_SP1', 'UND_SP2', 'UND_SP3',
                                        'GRD_SP1', 'GRD_SP2', 'GRD_SP3',
                                        'NOT_SP1', 'NOT_SP2', 'NOT_SP3',
                                        'NOT_SP4', 'NOT_SP5',
                                        'COL_CREW', 'AGENCY', 'DISTRICT',
                                        'ITERATION', 'SHAPE'],
                                       errors='ignore')

        # Rename Columns
        plot_metrics = plot_metrics.rename(columns={'AGE_MISC': 'AGE_NOTE',
                                                    'FX_MISC': 'FIXED_NOTE',
                                                    'UND_HT': 'UND_HT_RG',
                                                    'UND_HT2': 'UND_HT_MEAN',
                                                    'MAST_TYPE': 'AGE_MAST_TYPE'})

        # Create and populate inventory year column
        plot_metrics['INVT_YEAR'] = plot_metrics['COL_DATE'].dt.year
        plot_metrics = plot_metrics.set_index('PID')

        # Create BA, TPA, QM DBH
        plot_ba_tpa = fcalc.tpa_ba_qmdbh_plot(tree_table=tree_table,
                                              filter_statement=~tree_table.TR_HLTH.isin(["D", "DEAD"]))

        # Clean up TPA & BA for live tree dataframe
        plot_tpa_ba_live_df = plot_ba_tpa\
            .drop(columns=['tree_count', 'stand_dens', 'plot_count'], errors='ignore') \
            .rename(columns={'TPA': 'LIVE_TPA', 'BA': 'LIVE_BA',
                             'QM_DBH': 'LIVE_QMDBH', 'plot_count': 'PLOT_CT'}) \
            .set_index('PID')
        arcpy.AddMessage("    TPA & BA Live Tree DF Created")

        # Calculate total num trees (all, no filter) -- source: tree table
        plot_tr_all = tree_table \
            .groupby('PID') \
            .apply(fcalc.tree_count)

        # Convert tot num trees series to dataframe
        plot_tr_all_df = pd.DataFrame({'PID': plot_tr_all.index, 'TR_CT': plot_tr_all.values}).set_index('PID')
        arcpy.AddMessage("    Total Tree Count DF Created")

        # Calculate total num live trees -- source: tree table
        plot_tr_live = tree_table[~tree_table.TR_HLTH.isin(["D", "DEAD"])] \
            .groupby('PID') \
            .apply(fcalc.tree_count)

        # Convert tot num live trees series to dataframe
        plot_tr_live_df = pd.DataFrame({'PID': plot_tr_live.index, 'TR_LV_CT': plot_tr_live.values}).set_index('PID')
        arcpy.AddMessage("    Total Live Tree Count DF Created")

        # Calculate total num dead trees -- source: tree table
        plot_tr_dead = tree_table[tree_table.TR_HLTH.isin(["D", "DEAD"])] \
            .groupby('PID') \
            .apply(fcalc.tree_count)

        # Convert total num dead trees series to dataframe
        plot_tr_dead_df = pd.DataFrame({'PID': plot_tr_dead.index, 'TR_D_CT': plot_tr_dead.values}).set_index('PID')
        arcpy.AddMessage("    Total Dead Tree Count DF Created")

        # Average Mean Diameter live trees - tree table
        # Calculate Max DBH and Mean Diameter live trees -- source: tree table
        plot_diam_df = tree_table[~tree_table.TR_HLTH.isin(["D", "DEAD"])] \
            .groupby('PID') \
            .agg(
            LIVE_AMD=('TR_DIA', 'mean'),
            LIVE_MAX_DBH=('TR_DIA', 'max')
            ) \
            .reset_index() \
            .set_index('PID')
        arcpy.AddMessage("    AMD and Max DBH for Live Trees DF Created")

        # Merge component dataframes onto the base dataframe
        out_df = plot_metrics \
            .join([plot_tpa_ba_live_df,
                   plot_tr_all_df,
                   plot_tr_live_df,
                   plot_tr_dead_df,
                   plot_diam_df],
                  how='left') \
            .reset_index()
        arcpy.AddMessage("    All Component DFs Merged")

        # reindex output dataframe
        general_reindex_cols = \
            fcalc.fmg_column_reindex_list(level=level,
                                          col_csv='resources/general_summary_cols_pid.csv')
        out_df = out_df.reindex(labels=general_reindex_cols,
                                axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Handle NaN values appropriately
        nan_fill_dict_pid = fcalc.fmg_nan_fill(col_csv='resources/general_summary_cols_pid.csv')

        out_df = out_df\
            .fillna(value=nan_fill_dict_pid) \
            .replace({'AGE_NOTE': {None: "", " ": ""},
                      'INV_SP': {"": 'NONE', " ": 'NONE', None: 'NONE'}})\
            .drop(columns=['index'], errors='ignore')
        arcpy.AddMessage("    Nan Values Filled")

        # Enforce ESRI compatible DTypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/general_summary_cols_pid.csv')
        out_df = out_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Export to gdb table
        table_name = "PID_General_Summary"
        table_path = os.path.join(out_gdb, table_name)
        out_df.spatial.to_table(location=table_path, sanitize_columns=False)
        arcpy.AddMessage('    DataFrame exported to {0}'.format(table_path))

    arcpy.AddMessage('    Complete')
    return table_path


def age_summary(plot_table, out_gdb, level):
    arcpy.AddMessage('--Execute Age Summary on {0}--'.format(level))

    # Create Base DF
    base_df = fcalc.create_level_df(level=level,
                                    plot_table=plot_table)
    arcpy.AddMessage('    Base df created')

    # Filter plot table to just records with age trees
    age_plots = plot_table.query("AGE_ORIG==AGE_ORIG")
    arcpy.AddMessage('    Age table created')

    # Calculate unfiltered metrics group by agg:
    # Avg level Age (mean AGE_ORIG)
    # Avg level Dia (mean AGE_DIA)
    # Age Growth Rate (mean AGE_GRW)
    # Age Regen Rate or Avg Understory Cover (mean UND_COV decimal truncated)
    unfiltered_metrics = age_plots\
        .groupby([level])\
        .agg(
            AGE_ORIG=('AGE_ORIG', 'mean'),
            AGE_DBH=('AGE_DIA', 'mean'),
            AGE_GRW=('AGE_GRW', 'mean'),
            AGE_UND_COV=('UND_COV', 'mean')
            )\
        .reset_index()
    arcpy.AddMessage('    Unfiltered df created')

    # Adjust data types & set index
    unfiltered_metrics = unfiltered_metrics.astype({'AGE_ORIG': 'int', 'AGE_UND_COV': 'int'})
    unfiltered_metrics = unfiltered_metrics.set_index(level)

    # Calculate filtered metrics
    # Avg Age Hard Mast
    hm_age = age_plots[age_plots.MAST_TYPE.isin(["H", "Hard"])]\
        .groupby([level])\
        .agg(HM_ORIG=('AGE_ORIG', 'mean'))\
        .reset_index()
    arcpy.AddMessage('    Hard mast df created')

    # Avg Age Soft Mast
    sm_age = age_plots[age_plots.MAST_TYPE.isin(["S", "Soft"])]\
        .groupby([level]) \
        .agg(SM_ORIG=('AGE_ORIG', 'mean')) \
        .reset_index()
    arcpy.AddMessage('    Soft Mast df created')

    # Avg Age Lightseed
    lm_age = age_plots[age_plots.MAST_TYPE.isin(["L", "Lightseed"])]\
        .groupby([level]) \
        .agg(LM_ORIG=('AGE_ORIG', 'mean'))\
        .reset_index()
    arcpy.AddMessage('    Lightseed df created')

    # Adjust data types
    hm_age['HM_ORIG'] = hm_age['HM_ORIG'].astype(int)
    sm_age['SM_ORIG'] = sm_age['SM_ORIG'].astype(int)
    lm_age['LM_ORIG'] = lm_age['LM_ORIG'].astype(int)

    # Set indexes
    hm_age = hm_age.set_index(level)
    sm_age = sm_age.set_index(level)
    lm_age = lm_age.set_index(level)

    # Merge
    out_df = base_df \
        .join([unfiltered_metrics,
               hm_age,
               sm_age,
               lm_age])\
        .reset_index()
    arcpy.AddMessage('    dfs merged')

    # Reindex output dataframe
    age_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                     col_csv="resources/age_summary_cols.csv")
    out_df = out_df.reindex(labels=age_reindex_cols,
                            axis='columns')
    arcpy.AddMessage("    Columns reordered")

    # Handle Nan values
    nan_fill_dict = fcalc.fmg_nan_fill(col_csv='resources/age_summary_cols.csv')
    out_df = out_df.fillna(value=nan_fill_dict)
    arcpy.AddMessage("    No data/nan values set")

    # Enforce ESRI compatible DTypes
    dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/age_summary_cols.csv')
    out_df = out_df.astype(dtype=dtype_dict, copy=False)
    arcpy.AddMessage("    Dtypes Enforced")

    # Export to gdb table
    table_name = level + "_Age_Summary"
    table_path = os.path.join(out_gdb, table_name)
    out_df.spatial.to_table(location=table_path, sanitize_columns=False)
    arcpy.AddMessage('    merged df exported to {0}'.format(table_path))

    arcpy.AddMessage("    Complete")
    return table_path


def health_summary(plot_table, tree_table, out_gdb, level):
    arcpy.AddMessage('--Execute Health Summaryon {0}--'.format(level))
    if level != 'PID':

        # Create Base DF
        base_df = fcalc.create_level_df(level, plot_table)
        arcpy.AddMessage("    Base DF Created")

        # Create TPA, BA, QMDBH for each health class
        tpa_ba_qmdbh_base_df = fcalc.tpa_ba_qmdbh_level_by_case(tree_table=tree_table,
                                                                filter_statement=None,
                                                                case_column='TR_HLTH',
                                                                level=level)
        tpa_ba_qmdbh_base_df = tpa_ba_qmdbh_base_df.set_index(level)
        arcpy.AddMessage("    TPA, BA, QMDBH by health class created")

        # Create Species Dom where Health = D
        sp_dom_d_df = fcalc.species_dom_level(tree_table=tree_table,
                                              filter_statement=tree_table['TR_HLTH'] == 'D',
                                              level=level)
        sp_dom_d_df = sp_dom_d_df\
            .rename(columns={'SP_DOM': 'DEAD_DOM_SP', 'SP_DOM_PCMP': 'DEAD_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Dominant dead species created")

        # Create Species Dom where Health = SD
        sp_dom_sd_df = fcalc.species_dom_level(tree_table=tree_table,
                                               filter_statement=tree_table['TR_HLTH'] == 'SD',
                                               level=level)
        sp_dom_sd_df = sp_dom_sd_df\
            .rename(columns={'SP_DOM': 'SD_DOM_SP', 'SP_DOM_PCMP': 'SD_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Dominant sig dec species created")

        # Create Species Dom where Health = S
        sp_dom_s_df = fcalc.species_dom_level(tree_table=tree_table,
                                              filter_statement=tree_table['TR_HLTH'] == 'S',
                                              level=level)
        sp_dom_s_df = sp_dom_s_df\
            .rename(columns={'SP_DOM': 'STR_DOM_SP', 'SP_DOM_PCMP': 'STR_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Dominant stressed species created")

        # Create Species Dom where Health = H
        sp_dom_h_df = fcalc.species_dom_level(tree_table=tree_table,
                                              filter_statement=tree_table['TR_HLTH'] == 'H',
                                              level=level)
        sp_dom_h_df = sp_dom_h_df\
            .rename(columns={'SP_DOM': 'HLTH_DOM_SP', 'SP_DOM_PCMP': 'HLTH_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Dominant healthy species created")

        # Create overall dominant health
        dom_health_df = fcalc.health_dom_level(tree_table=tree_table,
                                               filter_statement=None,
                                               level=level)
        dom_health_df = dom_health_df\
            .rename(columns={'HLTH_DOM': 'DOM_HLTH', 'HLTH_DOM_PCMP': 'DOM_HLTH_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Dominant health created")

        # Create overall dominant species
        dom_species_df = fcalc.species_dom_level(tree_table=tree_table,
                                                 filter_statement=None,
                                                 level=level)

        dom_species_df = dom_species_df\
            .rename(columns={'SP_DOM': 'DOM_SP', 'SP_DOM_PCMP': 'DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Dominant species created")

        # Large Dead Tree TPA
        lg_dead_tr_raw_df = fcalc.tpa_ba_qmdbh_level(tree_table=tree_table,
                                                     filter_statement=
                                                     (tree_table['TR_HLTH'] == 'D') &
                                                     (tree_table['TR_DIA'] > 20),
                                                     level=level)

        lg_dead_tr_df = lg_dead_tr_raw_df.filter(items=[level, 'TPA'])

        lg_dead_tr_df = lg_dead_tr_df.rename(columns={'TPA': 'LG_D_TPA'}).set_index(level)
        arcpy.AddMessage("    Lg dead tree TPA created")

        # Create Typical species dominant health
        typ_dom_hlth_df = fcalc.health_dom_level(tree_table=tree_table,
                                                 filter_statement=tree_table['SP_TYPE'] == 'Common',
                                                 level=level)
        typ_dom_hlth_df = typ_dom_hlth_df\
            .rename(columns={'HLTH_DOM': 'TYP_SP_DOM_HLTH', 'HLTH_DOM_PCMP': 'TYP_SP_DOM_HLTH_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Typ Sp Dom health created")

        # Create Typical Species dominant species
        typ_dom_sp_df = fcalc.species_dom_level(tree_table=tree_table,
                                                filter_statement=tree_table['SP_TYPE'] == 'Common',
                                                level=level)
        typ_dom_sp_df = typ_dom_sp_df\
            .rename(columns={'SP_DOM': 'TYP_DOM_SP', 'SP_DOM_PCMP': 'TYP_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Typ Sp Dom species created")

        # Create Non-Typical species dominant health
        ntyp_dom_hlth_df = fcalc.health_dom_level(tree_table=tree_table,
                                                  filter_statement=tree_table['SP_TYPE'] == 'Uncommon',
                                                  level=level)
        ntyp_dom_hlth_df = ntyp_dom_hlth_df\
            .rename(columns={'HLTH_DOM': 'NTYP_SP_DOM_HLTH', 'HLTH_DOM_PCMP': 'NTYP_SP_DOM_HLTH_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Non-Typ Sp Dom health created")

        # Create Non-Typical species dominant species
        ntyp_dom_sp_df = fcalc.species_dom_level(tree_table=tree_table,
                                                 filter_statement=tree_table['SP_TYPE'] == 'Uncommon',
                                                 level=level)
        ntyp_dom_sp_df = ntyp_dom_sp_df\
            .rename(columns={'SP_DOM': 'NTYP_DOM_SP', 'SP_DOM_PCMP': 'NTYP_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Non-Typ Sp Dom species created")

        # Merge Component Dataframes onto base df
        health_summary_df = base_df\
            .join(other=[tpa_ba_qmdbh_base_df,
                         sp_dom_d_df,
                         sp_dom_sd_df,
                         sp_dom_s_df,
                         sp_dom_h_df,
                         dom_health_df,
                         dom_species_df,
                         lg_dead_tr_df,
                         typ_dom_hlth_df,
                         typ_dom_sp_df,
                         ntyp_dom_hlth_df,
                         ntyp_dom_sp_df],
                  how='left')\
            .reset_index()
        arcpy.AddMessage("    All Component DFs Merged")

        # Rename columns
        health_summary_df = health_summary_df\
            .rename(columns={'BA_TR_HLTH_D': 'DEAD_BA',
                             'BA_TR_HLTH_H': 'HLTH_BA',
                             'BA_TR_HLTH_S': 'STR_BA',
                             'BA_TR_HLTH_SD': 'SD_BA',
                             'QM_DBH_TR_HLTH_D': 'DEAD_QMDBH',
                             'QM_DBH_TR_HLTH_H': 'HLTH_QMDBH',
                             'QM_DBH_TR_HLTH_S': 'STR_QMDBH',
                             'QM_DBH_TR_HLTH_SD': 'SD_QMDBH',
                             'TPA_TR_HLTH_D': 'DEAD_TPA',
                             'TPA_TR_HLTH_H': 'HLTH_TPA',
                             'TPA_TR_HLTH_S': 'STR_TPA',
                             'TPA_TR_HLTH_SD': 'SD_TPA'})
        arcpy.AddMessage("    Columns renamed")

        # Reindex output dataframe
        health_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                            col_csv="resources/health_summary_cols.csv")
        health_summary_df = health_summary_df.reindex(labels=health_reindex_cols,
                                                      axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Handle NAN values for output
        nan_fill_dict = fcalc.fmg_nan_fill(col_csv='resources/health_summary_cols.csv')
        health_summary_df = health_summary_df.fillna(value=nan_fill_dict)
        arcpy.AddMessage("    No data/nan values set")

        # Enforce ESRI compatible DTypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/health_summary_cols.csv')
        health_summary_df = health_summary_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Export to GDB Table
        table_name = level + '_Health_Summary'
        table_path = os.path.join(out_gdb, table_name)
        health_summary_df.spatial.to_table(location=table_path, sanitize_columns=False)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    elif level == 'PID':

        # Create Base DF
        base_df = fcalc.create_level_df(level, plot_table)
        arcpy.AddMessage("    Base DF Created")

        # Create TPA, BA, QMDBH for each health class
        tpa_ba_qmdbh_base_df = fcalc.tpa_ba_qmdbh_plot_by_case(tree_table=tree_table,
                                                               filter_statement=None,
                                                               case_column='TR_HLTH')
        tpa_ba_qmdbh_base_df = tpa_ba_qmdbh_base_df.set_index(level)
        arcpy.AddMessage("    TPA, BA, QMDBH by health class created")

        # Create Species Dom where Health = D
        sp_dom_d_df = fcalc.species_dom_plot(tree_table=tree_table,
                                             filter_statement=tree_table['TR_HLTH'] == 'D')
        sp_dom_d_df = sp_dom_d_df \
            .rename(columns={'SP_DOM': 'DEAD_DOM_SP', 'SP_DOM_PCMP': 'DEAD_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Dom dead species created")

        # Create Species Dom where Health = SD
        sp_dom_sd_df = fcalc.species_dom_plot(tree_table=tree_table,
                                              filter_statement=tree_table['TR_HLTH'] == 'SD')
        sp_dom_sd_df = sp_dom_sd_df \
            .rename(columns={'SP_DOM': 'SD_DOM_SP', 'SP_DOM_PCMP': 'SD_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Dom sig dec species created")

        # Create Species Dom where Health = S
        sp_dom_s_df = fcalc.species_dom_plot(tree_table=tree_table,
                                             filter_statement=tree_table['TR_HLTH'] == 'S')
        sp_dom_s_df = sp_dom_s_df \
            .rename(columns={'SP_DOM': 'STR_DOM_SP', 'SP_DOM_PCMP': 'STR_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Dom stressed species created")

        # Create Species Dom where Health = H
        sp_dom_h_df = fcalc.species_dom_plot(tree_table=tree_table,
                                             filter_statement=tree_table['TR_HLTH'] == 'H')
        sp_dom_h_df = sp_dom_h_df \
            .rename(columns={'SP_DOM': 'HLTH_DOM_SP', 'SP_DOM_PCMP': 'HLTH_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Dom healthy species created")

        # Create overall dominant health
        dom_health_df = fcalc.health_dom_plot(tree_table=tree_table,
                                              filter_statement=None)
        dom_health_df = dom_health_df\
            .rename(columns={'HLTH_DOM': 'DOM_HLTH', 'HLTH_DOM_PCMP': 'DOM_HLTH_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Dominant health created")

        # Create overall dominant species
        dom_species_df = fcalc.species_dom_plot(tree_table=tree_table,
                                                filter_statement=None)
        dom_species_df = dom_species_df \
            .rename(columns={'SP_DOM': 'DOM_SP', 'SP_DOM_PCMP': 'DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Dominant species created")

        # Large Dead Tree TPA
        lg_dead_tr_raw_df = fcalc.tpa_ba_qmdbh_plot(tree_table=tree_table,
                                                    filter_statement=
                                                    (tree_table['TR_HLTH'] == 'D') &
                                                    (tree_table['TR_DIA'] > 20))

        lg_dead_tr_df = lg_dead_tr_raw_df.filter(items=[level, 'TPA'])

        lg_dead_tr_df = lg_dead_tr_df.rename(columns={'TPA': 'LG_D_TPA'}).set_index(level)
        arcpy.AddMessage("    Lg dead tree TPA created")

        # Create Typical species dominant health
        typ_dom_hlth_df = fcalc.health_dom_plot(tree_table=tree_table,
                                                filter_statement=tree_table['SP_TYPE'] == 'Common')
        typ_dom_hlth_df = typ_dom_hlth_df \
            .rename(columns={'HLTH_DOM': 'TYP_SP_DOM_HLTH', 'HLTH_DOM_PCMP': 'TYP_SP_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Typ Sp Dom health created")

        # Create Typical Species dominant species
        typ_dom_sp_df = fcalc.species_dom_plot(tree_table=tree_table,
                                               filter_statement=tree_table['SP_TYPE'] == 'Common')
        typ_dom_sp_df = typ_dom_sp_df \
            .rename(columns={'SP_DOM': 'TYP_DOM_SP', 'SP_DOM_PCMP': 'TYP_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Typ Sp Dom species created")

        # Create Non-Typical species dominant health
        ntyp_dom_hlth_df = fcalc.health_dom_plot(tree_table=tree_table,
                                                 filter_statement=tree_table['SP_TYPE'] == 'Uncommon')
        ntyp_dom_hlth_df = ntyp_dom_hlth_df \
            .rename(columns={'HLTH_DOM': 'NTYP_SP_DOM_HLTH', 'HLTH_DOM_PCMP': 'NTYP_SP_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Non-Typ Sp Dom health created")

        # Create Non-Typical species dominant species
        ntyp_dom_sp_df = fcalc.species_dom_plot(tree_table=tree_table,
                                                filter_statement=tree_table['SP_TYPE'] == 'Uncommon')
        ntyp_dom_sp_df = ntyp_dom_sp_df \
            .rename(columns={'SP_DOM': 'NTYP_DOM_SP', 'SP_DOM_PCMP': 'NTYP_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Non-Typ Sp Dom species created")

        # Merge Component Dataframes onto base df
        health_summary_df = base_df \
            .join(other=[tpa_ba_qmdbh_base_df,
                         sp_dom_d_df,
                         sp_dom_sd_df,
                         sp_dom_s_df,
                         sp_dom_h_df,
                         dom_health_df,
                         dom_species_df,
                         lg_dead_tr_df,
                         typ_dom_hlth_df,
                         typ_dom_sp_df,
                         ntyp_dom_hlth_df,
                         ntyp_dom_sp_df],
                  how='left') \
            .reset_index()
        arcpy.AddMessage("    All Component DFs Merged")

        # Rename columns
        health_summary_df = health_summary_df \
            .rename(columns={'BA_TR_HLTH_D': 'DEAD_BA',
                             'BA_TR_HLTH_H': 'HLTH_BA',
                             'BA_TR_HLTH_S': 'STR_BA',
                             'BA_TR_HLTH_SD': 'SD_BA',
                             'QM_DBH_TR_HLTH_D': 'DEAD_QMDBH',
                             'QM_DBH_TR_HLTH_H': 'HLTH_QMDBH',
                             'QM_DBH_TR_HLTH_S': 'STR_QMDBH',
                             'QM_DBH_TR_HLTH_SD': 'SD_QMDBH',
                             'TPA_TR_HLTH_D': 'DEAD_TPA',
                             'TPA_TR_HLTH_H': 'HLTH_TPA',
                             'TPA_TR_HLTH_S': 'STR_TPA',
                             'TPA_TR_HLTH_SD': 'SD_TPA'})
        arcpy.AddMessage("    Columns renamed")

        # Reindex output dataframe
        health_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                            col_csv="resources/health_summary_cols.csv")

        health_summary_df = health_summary_df.reindex(labels=health_reindex_cols,
                                                      axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Handle NAN values for output
        nan_fill_dict = fcalc.fmg_nan_fill(col_csv='resources/health_summary_cols.csv')
        health_summary_df = health_summary_df.fillna(value=nan_fill_dict)
        arcpy.AddMessage("    No data/nan values set")

        # Enforce ESRI compatible DTypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/health_summary_cols.csv')
        health_summary_df = health_summary_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Export to GDB Table
        table_name = level + '_Health_Summary'
        table_path = os.path.join(out_gdb, table_name)
        health_summary_df.spatial.to_table(location=table_path, sanitize_columns=False)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    arcpy.AddMessage('    Complete')
    return table_path


def mast_summary(plot_table, tree_table, out_gdb, level):
    arcpy.AddMessage('--Execute Mast Summary on {0}--'.format(level))
    if level != 'PID':

        # Create Base DF
        base_df = fcalc.create_level_df(level, plot_table)
        arcpy.AddMessage("    Base DF Created")

        # Create TPA, BA, QMDBH for each mast class
        tpa_ba_qmdbh_base_df = fcalc.tpa_ba_qmdbh_level_by_case(tree_table=tree_table,
                                                                filter_statement=
                                                                ~tree_table.TR_HLTH.isin(["D", "DEAD"]),
                                                                case_column='MAST_TYPE',
                                                                level=level)
        tpa_ba_qmdbh_base_df = tpa_ba_qmdbh_base_df.set_index(level)
        arcpy.AddMessage("    TPA, BA, QMDBH by health class created")

        # Create Health Dom where Mast = Hard
        hm_dom_hlth_df = fcalc.health_dom_level(tree_table=tree_table,
                                                filter_statement=tree_table['MAST_TYPE'] == 'Hard',
                                                level=level)
        hm_dom_hlth_df = hm_dom_hlth_df\
            .rename(columns={'HLTH_DOM': 'HM_DOM_HLTH', 'HLTH_DOM_PCMP': 'HM_DOM_HLTH_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Hard mast dominant health created")

        # Create Species Dom where Mast = Hard
        hm_dom_sp_df = fcalc.species_dom_level(tree_table=tree_table,
                                               filter_statement=tree_table['MAST_TYPE'] == 'Hard',
                                               level=level)
        hm_dom_sp_df = hm_dom_sp_df\
            .rename(columns={'SP_DOM': 'HM_DOM_SP', 'SP_DOM_PCMP': 'HM_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Hard mast dominant species created")

        # Create Health Dom where Mast = Soft
        sm_dom_hlth_df = fcalc.health_dom_level(tree_table=tree_table,
                                                filter_statement=tree_table['MAST_TYPE'] == 'Soft',
                                                level=level)
        sm_dom_hlth_df = sm_dom_hlth_df \
            .rename(columns={'HLTH_DOM': 'SM_DOM_HLTH', 'HLTH_DOM_PCMP': 'SM_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Soft mast dominant health created")

        # Create Species Dom where Mast = Soft
        sm_dom_sp_df = fcalc.species_dom_level(tree_table=tree_table,
                                               filter_statement=tree_table['MAST_TYPE'] == 'Soft',
                                               level=level)
        sm_dom_sp_df = sm_dom_sp_df\
            .rename(columns={'SP_DOM': 'SM_DOM_SP', 'SP_DOM_PCMP': 'SM_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Soft mast dominant species created")

        # Create Health Dom where Mast = Lightseed
        lm_dom_hlth_df = fcalc.health_dom_level(tree_table=tree_table,
                                                filter_statement=tree_table['MAST_TYPE'] == 'Lightseed',
                                                level=level)
        lm_dom_hlth_df = lm_dom_hlth_df \
            .rename(columns={'HLTH_DOM': 'LM_DOM_HLTH', 'HLTH_DOM_PCMP': 'LM_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Lightseed mast dominant health created")

        # Create Species Dom where Mast = Lightseed
        lm_dom_sp_df = fcalc.species_dom_level(tree_table=tree_table,
                                               filter_statement=tree_table['MAST_TYPE'] == 'Lightseed',
                                               level=level)
        lm_dom_sp_df = lm_dom_sp_df\
            .rename(columns={'SP_DOM': 'LM_DOM_SP', 'SP_DOM_PCMP': 'LM_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Lightseed mast dominant species created")

        # Merge Component Dataframes onto base df
        mast_summary_df = base_df\
            .join(other=[tpa_ba_qmdbh_base_df,
                         hm_dom_hlth_df,
                         hm_dom_sp_df,
                         sm_dom_hlth_df,
                         sm_dom_sp_df,
                         lm_dom_hlth_df,
                         lm_dom_sp_df],
                  how='left')\
            .reset_index()
        arcpy.AddMessage("    All Component DFs Merged")

        # Rename columns
        mast_summary_df = mast_summary_df\
            .rename(columns={'BA_MAST_TYPE_Hard': 'HM_BA',
                             'BA_MAST_TYPE_Soft': 'SM_BA',
                             'BA_MAST_TYPE_Lightseed': 'LM_BA',
                             'TPA_MAST_TYPE_Hard': 'HM_TPA',
                             'TPA_MAST_TYPE_Soft': 'SM_TPA',
                             'TPA_MAST_TYPE_Lightseed': 'LM_TPA',
                             'QM_DBH_MAST_TYPE_Hard': 'HM_QMDBH',
                             'QM_DBH_MAST_TYPE_Soft': 'SM_QMDBH',
                             'QM_DBH_MAST_TYPE_Lightseed': 'LM_QMDBH'})
        arcpy.AddMessage("    Columns renamed")

        # Reindex output dataframe
        mast_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                          col_csv='resources/mast_summary_cols.csv')

        mast_summary_df = mast_summary_df.reindex(labels=mast_reindex_cols,
                                                  axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Handle NAN values for output
        nan_fill_dict = fcalc.fmg_nan_fill(col_csv='resources/mast_summary_cols.csv')
        mast_summary_df = mast_summary_df.fillna(value=nan_fill_dict)
        arcpy.AddMessage("    No data/nan values set")

        # Enforce ESRI compatible DTypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/mast_summary_cols.csv')
        mast_summary_df = mast_summary_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Export to GDB Table
        table_name = level + '_Mast_Summary'
        table_path = os.path.join(out_gdb, table_name)
        mast_summary_df.spatial.to_table(location=table_path, sanitize_columns=False)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    elif level == 'PID':

        # Create Base DF
        base_df = fcalc.create_level_df(level, plot_table)
        arcpy.AddMessage("    Base DF Created")

        # Create TPA, BA, QMDBH for each mast class
        tpa_ba_qmdbh_base_df = fcalc.tpa_ba_qmdbh_plot_by_case(tree_table=tree_table,
                                                               filter_statement=~tree_table.TR_HLTH.isin(["D", "DEAD"]),
                                                               case_column='MAST_TYPE')
        tpa_ba_qmdbh_base_df = tpa_ba_qmdbh_base_df.set_index(level)
        arcpy.AddMessage("    TPA, BA, QMDBH by health class created")

        # Create Health Dom where Mast = Hard
        hm_dom_hlth_df = fcalc.health_dom_plot(tree_table=tree_table,
                                               filter_statement=tree_table['MAST_TYPE'] == 'Hard')
        hm_dom_hlth_df = hm_dom_hlth_df\
            .rename(columns={'HLTH_DOM': 'HM_DOM_HLTH', 'HLTH_DOM_PCMP': 'HM_DOM_HLTH_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Hard mast dominant health created")

        # Create Species Dom where Mast = Hard
        hm_dom_sp_df = fcalc.species_dom_plot(tree_table=tree_table,
                                              filter_statement=tree_table['MAST_TYPE'] == 'Hard')
        hm_dom_sp_df = hm_dom_sp_df\
            .rename(columns={'SP_DOM': 'HM_DOM_SP', 'SP_DOM_PCMP': 'HM_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Hard mast dominant species created")

        # Create Health Dom where Mast = Soft
        sm_dom_hlth_df = fcalc.health_dom_plot(tree_table=tree_table,
                                               filter_statement=tree_table['MAST_TYPE'] == 'Soft')
        sm_dom_hlth_df = sm_dom_hlth_df \
            .rename(columns={'HLTH_DOM': 'SM_DOM_HLTH', 'HLTH_DOM_PCMP': 'SM_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Soft mast dominant health created")

        # Create Species Dom where Mast = Soft
        sm_dom_sp_df = fcalc.species_dom_plot(tree_table=tree_table,
                                              filter_statement=tree_table['MAST_TYPE'] == 'Soft')
        sm_dom_sp_df = sm_dom_sp_df\
            .rename(columns={'SP_DOM': 'SM_DOM_SP', 'SP_DOM_PCMP': 'SM_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Soft mast dominant species created")

        # Create Health Dom where Mast = Lightseed
        lm_dom_hlth_df = fcalc.health_dom_plot(tree_table=tree_table,
                                               filter_statement=tree_table['MAST_TYPE'] == 'Lightseed')
        lm_dom_hlth_df = lm_dom_hlth_df \
            .rename(columns={'HLTH_DOM': 'LM_DOM_HLTH', 'HLTH_DOM_PCMP': 'LM_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Lightseed mast dominant health created")

        # Create Species Dom where Mast = Lightseed
        lm_dom_sp_df = fcalc.species_dom_plot(tree_table=tree_table,
                                              filter_statement=tree_table['MAST_TYPE'] == 'Lightseed')
        lm_dom_sp_df = lm_dom_sp_df\
            .rename(columns={'SP_DOM': 'LM_DOM_SP', 'SP_DOM_PCMP': 'LM_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Lightseed mast dominant species created")

        # Merge Component Dataframes onto base df
        mast_summary_df = base_df\
            .join(other=[tpa_ba_qmdbh_base_df,
                         hm_dom_hlth_df,
                         hm_dom_sp_df,
                         sm_dom_hlth_df,
                         sm_dom_sp_df,
                         lm_dom_hlth_df,
                         lm_dom_sp_df],
                  how='left')\
            .reset_index()
        arcpy.AddMessage("    All Component DFs Merged")

        # Rename columns
        mast_summary_df = mast_summary_df\
            .rename(columns={'BA_MAST_TYPE_Hard': 'HM_BA',
                             'BA_MAST_TYPE_Soft': 'SM_BA',
                             'BA_MAST_TYPE_Lightseed': 'LM_BA',
                             'TPA_MAST_TYPE_Hard': 'HM_TPA',
                             'TPA_MAST_TYPE_Soft': 'SM_TPA',
                             'TPA_MAST_TYPE_Lightseed': 'LM_TPA',
                             'QM_DBH_MAST_TYPE_Hard': 'HM_QMDBH',
                             'QM_DBH_MAST_TYPE_Soft': 'SM_QMDBH',
                             'QM_DBH_MAST_TYPE_Lightseed': 'LM_QMDBH'})
        arcpy.AddMessage("    Columns renamed")

        # Reindex output dataframe
        mast_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                          col_csv='resources/mast_summary_cols.csv')

        mast_summary_df = mast_summary_df.reindex(labels=mast_reindex_cols,
                                                  axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Handle NAN values for output
        nan_fill_dict = fcalc.fmg_nan_fill(col_csv='resources/mast_summary_cols.csv')
        mast_summary_df = mast_summary_df.fillna(value=nan_fill_dict)
        arcpy.AddMessage("    No data/nan values set")

        # Enforce ESRI compatible DTypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/mast_summary_cols.csv')
        mast_summary_df = mast_summary_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Export to GDB Table
        table_name = level + '_Mast_Summary'
        table_path = os.path.join(out_gdb, table_name)
        mast_summary_df.spatial.to_table(location=table_path, sanitize_columns=False)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    arcpy.AddMessage('    Complete')
    return table_path


def size_summary(plot_table, tree_table, out_gdb, level):
    arcpy.AddMessage('--Execute Size Summary on {0}--'.format(level))
    if level != 'PID':

        # Create Base DF
        base_df = fcalc.create_level_df(level, plot_table)
        arcpy.AddMessage("    Base DF Created")

        # Create tpa, ba, qmdbh for live trees by size class
        tpa_ba_qmdbh_live_df = fcalc.tpa_ba_qmdbh_level_by_case(tree_table=tree_table,
                                                                filter_statement=
                                                                ~tree_table.TR_HLTH.isin(["D", "DEAD"]),
                                                                case_column='TR_SIZE',
                                                                level=level)

        # Rename columns and set index
        tpa_ba_qmdbh_live_df = tpa_ba_qmdbh_live_df\
            .rename(columns={'BA_TR_SIZE_Mature': 'MAT_BA',
                             'BA_TR_SIZE_Over Mature': 'OVM_BA',
                             'BA_TR_SIZE_Saw': 'SAW_BA',
                             'BA_TR_SIZE_Pole': 'POL_BA',
                             'BA_TR_SIZE_Sapling': 'SAP_BA',
                             'TPA_TR_SIZE_Mature': 'MAT_TPA',
                             'TPA_TR_SIZE_Over Mature': 'OVM_TPA',
                             'TPA_TR_SIZE_Saw': 'SAW_TPA',
                             'TPA_TR_SIZE_Pole': 'POL_TPA',
                             'TPA_TR_SIZE_Sapling': 'SAP_TPA',
                             'QM_DBH_TR_SIZE_Mature': 'MAT_QMDBH',
                             'QM_DBH_TR_SIZE_Over Mature': 'OVM_QMDBH',
                             'QM_DBH_TR_SIZE_Saw': 'SAW_QMDBH',
                             'QM_DBH_TR_SIZE_Pole': 'POL_QMDBH',
                             'QM_DBH_TR_SIZE_Sapling': 'SAP_QMDBH'})\
            .set_index(level)
        arcpy.AddMessage("    TPA, BA, QMDBH Created for live trees by Size Class")

        # Create tpa, ba, qmdbh for dead trees by size class
        tpa_ba_qmdbh_dead_df = fcalc.tpa_ba_qmdbh_level_by_case(tree_table=tree_table,
                                                                filter_statement=
                                                                tree_table.TR_HLTH.isin(["D", "DEAD"]),
                                                                case_column='TR_SIZE',
                                                                level=level)

        # Rename columns and set index
        tpa_ba_qmdbh_dead_df = tpa_ba_qmdbh_dead_df\
            .rename(columns={'BA_TR_SIZE_Mature': 'MAT_D_BA',
                             'BA_TR_SIZE_Over Mature': 'OVM_D_BA',
                             'BA_TR_SIZE_Saw': 'SAW_D_BA',
                             'BA_TR_SIZE_Pole': 'POL_D_BA',
                             'BA_TR_SIZE_Sapling': 'SAP_D_BA',
                             'TPA_TR_SIZE_Mature': 'MAT_D_TPA',
                             'TPA_TR_SIZE_Over Mature': 'OVM_D_TPA',
                             'TPA_TR_SIZE_Saw': 'SAW_D_TPA',
                             'TPA_TR_SIZE_Pole': 'POL_D_TPA',
                             'TPA_TR_SIZE_Sapling': 'SAP_D_TPA',
                             'QM_DBH_TR_SIZE_Mature': 'MAT_D_QMDBH',
                             'QM_DBH_TR_SIZE_Over Mature': 'OVM_D_QMDBH',
                             'QM_DBH_TR_SIZE_Saw': 'SAW_D_QMDBH',
                             'QM_DBH_TR_SIZE_Pole': 'POL_D_QMDBH',
                             'QM_DBH_TR_SIZE_Sapling': 'SAP_D_QMDBH'})\
            .set_index(level)
        arcpy.AddMessage("    TPA, BA, QMDBH Created for dead trees by Size Class")

        # Create Dominant Health where tree size = sapling
        sap_dom_hlth = fcalc.health_dom_level(tree_table=tree_table,
                                              filter_statement=tree_table['TR_SIZE'] == 'Sapling',
                                              level=level)
        sap_dom_hlth = sap_dom_hlth\
            .rename(columns={'HLTH_DOM': 'SAP_DOM_HLTH', 'HLTH_DOM_PCMP': 'SAP_DOM_HLTH_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Sapling dominant health created")

        # Create Dominant Species where tree size = sapling
        sap_dom_sp = fcalc.species_dom_level(tree_table=tree_table,
                                             filter_statement=tree_table['TR_SIZE'] == 'Sapling',
                                             level=level)
        sap_dom_sp = sap_dom_sp\
            .rename(columns={'SP_DOM': 'SAP_DOM_SP', 'SP_DOM_PCMP': 'SAP_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Sapling dominant species created")

        # Create Dominant Health where tree size = pole
        pol_dom_hlth = fcalc.health_dom_level(tree_table=tree_table,
                                              filter_statement=tree_table['TR_SIZE'] == 'Pole',
                                              level=level)
        pol_dom_hlth = pol_dom_hlth \
            .rename(columns={'HLTH_DOM': 'POL_DOM_HLTH', 'HLTH_DOM_PCMP': 'POL_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Pole Timber dominant health created")

        # Create Dominant Species where tree size = pole
        pol_dom_sp = fcalc.species_dom_level(tree_table=tree_table,
                                             filter_statement=tree_table['TR_SIZE'] == 'Pole',
                                             level=level)
        pol_dom_sp = pol_dom_sp \
            .rename(columns={'SP_DOM': 'POL_DOM_SP', 'SP_DOM_PCMP': 'POL_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Pole Timber dominant species created")

        # Create Dominant Health where tree size = saw
        saw_dom_hlth = fcalc.health_dom_level(tree_table=tree_table,
                                              filter_statement=tree_table['TR_SIZE'] == 'Saw',
                                              level=level)
        saw_dom_hlth = saw_dom_hlth \
            .rename(columns={'HLTH_DOM': 'SAW_DOM_HLTH', 'HLTH_DOM_PCMP': 'SAW_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Saw Timber dominant health created")

        # Create Dominant Species where tree size = saw
        saw_dom_sp = fcalc.species_dom_level(tree_table=tree_table,
                                             filter_statement=tree_table['TR_SIZE'] == 'Saw',
                                             level=level)
        saw_dom_sp = saw_dom_sp \
            .rename(columns={'SP_DOM': 'SAW_DOM_SP', 'SP_DOM_PCMP': 'SAW_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Saw Timber dominant species created")

        # Create Dominant Health where tree size = mature
        mat_dom_hlth = fcalc.health_dom_level(tree_table=tree_table,
                                              filter_statement=tree_table['TR_SIZE'] == 'Mature',
                                              level=level)
        mat_dom_hlth = mat_dom_hlth \
            .rename(columns={'HLTH_DOM': 'MAT_DOM_HLTH', 'HLTH_DOM_PCMP': 'MAT_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Mature Timber dominant health created")

        # Create Dominant Species where tree size = mature
        mat_dom_sp = fcalc.species_dom_level(tree_table=tree_table,
                                             filter_statement=tree_table['TR_SIZE'] == 'Mature',
                                             level=level)
        mat_dom_sp = mat_dom_sp \
            .rename(columns={'SP_DOM': 'MAT_DOM_SP', 'SP_DOM_PCMP': 'MAT_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Mature Timber dominant species created")

        # Create Dominant Health where tree size = over mature
        ovm_dom_hlth = fcalc.health_dom_level(tree_table=tree_table,
                                              filter_statement=tree_table['TR_SIZE'] == 'Over Mature',
                                              level=level)
        ovm_dom_hlth = ovm_dom_hlth \
            .rename(columns={'HLTH_DOM': 'OVM_DOM_HLTH', 'HLTH_DOM_PCMP': 'OVM_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Over Mature Timber dominant health created")

        # Create Dominant Species where tree size = over mature
        ovm_dom_sp = fcalc.species_dom_level(tree_table=tree_table,
                                             filter_statement=tree_table['TR_SIZE'] == 'Over Mature',
                                             level=level)
        ovm_dom_sp = ovm_dom_sp \
            .rename(columns={'SP_DOM': 'OVM_DOM_SP', 'SP_DOM_PCMP': 'OVM_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Over Mature Timber dominant species created")

        # Create BA, TPA, QMDBH for live large wildlife trees and rename columns
        tpa_ba_qmdbh_lwt = fcalc.tpa_ba_qmdbh_level(tree_table=tree_table,
                                                    filter_statement=
                                                    (tree_table['TR_TYPE'] == 'Wildlife') &
                                                    (~tree_table.TR_HLTH.isin(["D", "DEAD"])),
                                                    level=level)

        tpa_ba_qmdbh_lwt = tpa_ba_qmdbh_lwt\
            .rename(columns={'BA': 'LWT_BA',
                             'TPA': 'LWT_TPA',
                             'QM_DBH': 'LWT_QMDBH'})\
            .drop(columns=['index', 'tree_count', 'stand_dens', 'plot_count'])\
            .set_index(level)
        arcpy.AddMessage("    TPA, BA, QMDBH Created for live large wildlife trees")

        # Create BA, TPA, QMDBH for dead large wildlife trees and rename columns
        tpa_ba_qmdbh_lwt_d = fcalc.tpa_ba_qmdbh_level(tree_table=tree_table,
                                                      filter_statement=
                                                      (tree_table['TR_TYPE'] == 'Wildlife') &
                                                      (tree_table.TR_HLTH.isin(["D", "DEAD"])),
                                                      level=level)

        tpa_ba_qmdbh_lwt_d = tpa_ba_qmdbh_lwt_d\
            .rename(columns={'BA': 'LWT_D_BA',
                             'TPA': 'LWT_D_TPA',
                             'QM_DBH': 'LWT_D_QMDBH'})\
            .drop(columns=['index', 'tree_count', 'stand_dens', 'plot_count']) \
            .set_index(level)
        arcpy.AddMessage("    TPA, BA, QMDBH Created for dead large wildlife trees")

        # Create Dominant Health for large wildlife trees
        lwt_dom_hlth = fcalc.health_dom_level(tree_table=tree_table,
                                              filter_statement=tree_table['TR_TYPE'] == 'Wildlife',
                                              level=level)
        lwt_dom_hlth = lwt_dom_hlth \
            .rename(columns={'HLTH_DOM': 'LWT_DOM_HLTH', 'HLTH_DOM_PCMP': 'LWT_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Large Wildlife Tree dominant health created")

        # Create Dominant Species for large wildlife trees
        lwt_dom_sp = fcalc.species_dom_level(tree_table=tree_table,
                                             filter_statement=tree_table['TR_TYPE'] == 'Wildlife',
                                             level=level)
        lwt_dom_sp = lwt_dom_sp \
            .rename(columns={'SP_DOM': 'LWT_DOM_SP', 'SP_DOM_PCMP': 'LWT_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Large Wildlife Tree dominant species created")

        # Merge component dataframes
        size_summary_df = base_df\
            .join(other=[tpa_ba_qmdbh_live_df,
                         tpa_ba_qmdbh_dead_df,
                         sap_dom_hlth,
                         sap_dom_sp,
                         pol_dom_hlth,
                         pol_dom_sp,
                         saw_dom_hlth,
                         saw_dom_sp,
                         mat_dom_hlth,
                         mat_dom_sp,
                         ovm_dom_hlth,
                         ovm_dom_sp,
                         tpa_ba_qmdbh_lwt,
                         tpa_ba_qmdbh_lwt_d,
                         lwt_dom_hlth,
                         lwt_dom_sp],
                  how='left')\
            .reset_index()
        arcpy.AddMessage("    All Component DFs Merged")

        # Reindex output dataframe
        size_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                          col_csv='resources/size_summary_cols.csv')
        size_summary_df = size_summary_df.reindex(labels=size_reindex_cols,
                                                  axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Handle NAN values for output
        nan_fill_dict = fcalc.fmg_nan_fill(col_csv='resources/size_summary_cols.csv')
        size_summary_df = size_summary_df.fillna(value=nan_fill_dict)
        arcpy.AddMessage("    No data/nan values set")

        # Enforce ESRI compatible DTypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/size_summary_cols.csv')
        size_summary_df = size_summary_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Export to GDB Table
        table_name = level + '_Size_Summary'
        table_path = os.path.join(out_gdb, table_name)
        size_summary_df.spatial.to_table(location=table_path, sanitize_columns=False)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    elif level == 'PID':

        # Create Base DF
        base_df = fcalc.create_level_df(level, plot_table)
        arcpy.AddMessage("    Base DF Created")

        # Create tpa, ba, qmdbh for live trees by size class
        tpa_ba_qmdbh_live_df = fcalc.tpa_ba_qmdbh_plot_by_case(tree_table=tree_table,
                                                               filter_statement=
                                                               ~tree_table.TR_HLTH.isin(["D", "DEAD"]),
                                                               case_column='TR_SIZE')

        # Rename columns and set index
        tpa_ba_qmdbh_live_df = tpa_ba_qmdbh_live_df\
            .rename(columns={'BA_TR_SIZE_Mature': 'MAT_BA',
                             'BA_TR_SIZE_Over Mature': 'OVM_BA',
                             'BA_TR_SIZE_Saw': 'SAW_BA',
                             'BA_TR_SIZE_Pole': 'POL_BA',
                             'BA_TR_SIZE_Sapling': 'SAP_BA',
                             'TPA_TR_SIZE_Mature': 'MAT_TPA',
                             'TPA_TR_SIZE_Over Mature': 'OVM_TPA',
                             'TPA_TR_SIZE_Saw': 'SAW_TPA',
                             'TPA_TR_SIZE_Pole': 'POL_TPA',
                             'TPA_TR_SIZE_Sapling': 'SAP_TPA',
                             'QM_DBH_TR_SIZE_Mature': 'MAT_QMDBH',
                             'QM_DBH_TR_SIZE_Over Mature': 'OVM_QMDBH',
                             'QM_DBH_TR_SIZE_Saw': 'SAW_QMDBH',
                             'QM_DBH_TR_SIZE_Pole': 'POL_QMDBH',
                             'QM_DBH_TR_SIZE_Sapling': 'SAP_QMDBH'})\
            .set_index(level)
        arcpy.AddMessage("    TPA, BA, QMDBH Created for live trees by Size Class")

        # Create tpa, ba, qmdbh for dead trees by size class
        tpa_ba_qmdbh_dead_df = fcalc.tpa_ba_qmdbh_plot_by_case(tree_table=tree_table,
                                                               filter_statement=
                                                               tree_table.TR_HLTH.isin(["D", "DEAD"]),
                                                               case_column='TR_SIZE')

        # Rename columns and set index
        tpa_ba_qmdbh_dead_df = tpa_ba_qmdbh_dead_df\
            .rename(columns={'BA_TR_SIZE_Mature': 'MAT_D_BA',
                             'BA_TR_SIZE_Over Mature': 'OVM_D_BA',
                             'BA_TR_SIZE_Saw': 'SAW_D_BA',
                             'BA_TR_SIZE_Pole': 'POL_D_BA',
                             'BA_TR_SIZE_Sapling': 'SAP_D_BA',
                             'TPA_TR_SIZE_Mature': 'MAT_D_TPA',
                             'TPA_TR_SIZE_Over Mature': 'OVM_D_TPA',
                             'TPA_TR_SIZE_Saw': 'SAW_D_TPA',
                             'TPA_TR_SIZE_Pole': 'POL_D_TPA',
                             'TPA_TR_SIZE_Sapling': 'SAP_D_TPA',
                             'QM_DBH_TR_SIZE_Mature': 'MAT_D_QMDBH',
                             'QM_DBH_TR_SIZE_Over Mature': 'OVM_D_QMDBH',
                             'QM_DBH_TR_SIZE_Saw': 'SAW_D_QMDBH',
                             'QM_DBH_TR_SIZE_Pole': 'POL_D_QMDBH',
                             'QM_DBH_TR_SIZE_Sapling': 'SAP_D_QMDBH'})\
            .set_index(level)
        arcpy.AddMessage("    TPA, BA, QMDBH Created for dead trees by Size Class")

        # Create Dominant Health where tree size = sapling
        sap_dom_hlth = fcalc.health_dom_plot(tree_table=tree_table,
                                             filter_statement=tree_table['TR_SIZE'] == 'Sapling')
        sap_dom_hlth = sap_dom_hlth\
            .rename(columns={'HLTH_DOM': 'SAP_DOM_HLTH', 'HLTH_DOM_PCMP': 'SAP_DOM_HLTH_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Sapling dominant health created")

        # Create Dominant Species where tree size = sapling
        sap_dom_sp = fcalc.species_dom_plot(tree_table=tree_table,
                                            filter_statement=tree_table['TR_SIZE'] == 'Sapling')
        sap_dom_sp = sap_dom_sp\
            .rename(columns={'SP_DOM': 'SAP_DOM_SP', 'SP_DOM_PCMP': 'SAP_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Sapling dominant species created")

        # Create Dominant Health where tree size = pole
        pol_dom_hlth = fcalc.health_dom_plot(tree_table=tree_table,
                                             filter_statement=tree_table['TR_SIZE'] == 'Pole')
        pol_dom_hlth = pol_dom_hlth \
            .rename(columns={'HLTH_DOM': 'POL_DOM_HLTH', 'HLTH_DOM_PCMP': 'POL_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Pole Timber dominant health created")

        # Create Dominant Species where tree size = pole
        pol_dom_sp = fcalc.species_dom_plot(tree_table=tree_table,
                                            filter_statement=tree_table['TR_SIZE'] == 'Pole')
        pol_dom_sp = pol_dom_sp \
            .rename(columns={'SP_DOM': 'POL_DOM_SP', 'SP_DOM_PCMP': 'POL_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Pole Timber dominant species created")

        # Create Dominant Health where tree size = saw
        saw_dom_hlth = fcalc.health_dom_plot(tree_table=tree_table,
                                             filter_statement=tree_table['TR_SIZE'] == 'Saw')
        saw_dom_hlth = saw_dom_hlth \
            .rename(columns={'HLTH_DOM': 'SAW_DOM_HLTH', 'HLTH_DOM_PCMP': 'SAW_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Saw Timber dominant health created")

        # Create Dominant Species where tree size = saw
        saw_dom_sp = fcalc.species_dom_plot(tree_table=tree_table,
                                            filter_statement=tree_table['TR_SIZE'] == 'Saw')
        saw_dom_sp = saw_dom_sp \
            .rename(columns={'SP_DOM': 'SAW_DOM_SP', 'SP_DOM_PCMP': 'SAW_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Saw Timber dominant species created")

        # Create Dominant Health where tree size = mature
        mat_dom_hlth = fcalc.health_dom_plot(tree_table=tree_table,
                                             filter_statement=tree_table['TR_SIZE'] == 'Mature')
        mat_dom_hlth = mat_dom_hlth \
            .rename(columns={'HLTH_DOM': 'MAT_DOM_HLTH', 'HLTH_DOM_PCMP': 'MAT_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Mature Timber dominant health created")

        # Create Dominant Species where tree size = mature
        mat_dom_sp = fcalc.species_dom_plot(tree_table=tree_table,
                                            filter_statement=tree_table['TR_SIZE'] == 'Mature')
        mat_dom_sp = mat_dom_sp \
            .rename(columns={'SP_DOM': 'MAT_DOM_SP', 'SP_DOM_PCMP': 'MAT_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Mature Timber dominant species created")

        # Create Dominant Health where tree size = over mature
        ovm_dom_hlth = fcalc.health_dom_plot(tree_table=tree_table,
                                             filter_statement=tree_table['TR_SIZE'] == 'Over Mature')
        ovm_dom_hlth = ovm_dom_hlth \
            .rename(columns={'HLTH_DOM': 'OVM_DOM_HLTH', 'HLTH_DOM_PCMP': 'OVM_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Over Mature Timber dominant health created")

        # Create Dominant Species where tree size = over mature
        ovm_dom_sp = fcalc.species_dom_plot(tree_table=tree_table,
                                            filter_statement=tree_table['TR_SIZE'] == 'Over Mature')
        ovm_dom_sp = ovm_dom_sp \
            .rename(columns={'SP_DOM': 'OVM_DOM_SP', 'SP_DOM_PCMP': 'OVM_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Over Mature Timber dominant species created")

        # Create BA, TPA, QMDBH for live large wildlife trees and rename columns
        tpa_ba_qmdbh_lwt = fcalc.tpa_ba_qmdbh_plot(tree_table=tree_table,
                                                   filter_statement=
                                                   (tree_table['TR_TYPE'] == 'Wildlife') &
                                                   (~tree_table.TR_HLTH.isin(["D", "DEAD"])))

        tpa_ba_qmdbh_lwt = tpa_ba_qmdbh_lwt\
            .rename(columns={'BA': 'LWT_BA',
                             'TPA': 'LWT_TPA',
                             'QM_DBH': 'LWT_QMDBH'})\
            .drop(columns=['index', 'tree_count', 'plot_count'])\
            .set_index(level)
        arcpy.AddMessage("    TPA, BA, QMDBH Created for live large wildlife trees")

        # Create BA, TPA, QMDBH for dead large wildlife trees and rename columns
        tpa_ba_qmdbh_lwt_d = fcalc.tpa_ba_qmdbh_plot(tree_table=tree_table,
                                                     filter_statement=
                                                     (tree_table['TR_TYPE'] == 'Wildlife') &
                                                     (tree_table.TR_HLTH.isin(["D", "DEAD"])))

        tpa_ba_qmdbh_lwt_d = tpa_ba_qmdbh_lwt_d\
            .rename(columns={'BA': 'LWT_D_BA',
                             'TPA': 'LWT_D_TPA',
                             'QM_DBH': 'LWT_D_QMDBH'})\
            .drop(columns=['index', 'tree_count', 'plot_count']) \
            .set_index(level)
        arcpy.AddMessage("    TPA, BA, QMDBH Created for dead large wildlife trees")

        # Create Dominant Health for large wildlife trees
        lwt_dom_hlth = fcalc.health_dom_plot(tree_table=tree_table,
                                             filter_statement=tree_table['TR_TYPE'] == 'Wildlife')
        lwt_dom_hlth = lwt_dom_hlth \
            .rename(columns={'HLTH_DOM': 'LWT_DOM_HLTH', 'HLTH_DOM_PCMP': 'LWT_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Large Wildlife Tree dominant health created")

        # Create Dominant Species for large wildlife trees
        lwt_dom_sp = fcalc.species_dom_plot(tree_table=tree_table,
                                            filter_statement=tree_table['TR_TYPE'] == 'Wildlife')
        lwt_dom_sp = lwt_dom_sp \
            .rename(columns={'SP_DOM': 'LWT_DOM_SP', 'SP_DOM_PCMP': 'LWT_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Large Wildlife Tree dominant species created")

        # Merge component dataframes
        size_summary_df = base_df\
            .join(other=[tpa_ba_qmdbh_live_df,
                         tpa_ba_qmdbh_dead_df,
                         sap_dom_hlth,
                         sap_dom_sp,
                         pol_dom_hlth,
                         pol_dom_sp,
                         saw_dom_hlth,
                         saw_dom_sp,
                         mat_dom_hlth,
                         mat_dom_sp,
                         ovm_dom_hlth,
                         ovm_dom_sp,
                         tpa_ba_qmdbh_lwt,
                         tpa_ba_qmdbh_lwt_d,
                         lwt_dom_hlth,
                         lwt_dom_sp],
                  how='left')\
            .reset_index()
        arcpy.AddMessage("    All Component DFs Merged")

        # Reindex output dataframe
        size_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                          col_csv='resources/size_summary_cols.csv')
        size_summary_df = size_summary_df.reindex(labels=size_reindex_cols,
                                                  axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Handle NAN values for output
        nan_fill_dict = fcalc.fmg_nan_fill(col_csv='resources/size_summary_cols.csv')
        size_summary_df = size_summary_df.fillna(value=nan_fill_dict)
        arcpy.AddMessage("    No data/nan values set")

        # Enforce ESRI compatible DTypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/size_summary_cols.csv')
        size_summary_df = size_summary_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Export to GDB Table
        table_name = 'PID_Size_Summary'
        table_path = os.path.join(out_gdb, table_name)
        size_summary_df.spatial.to_table(location=table_path, sanitize_columns=False)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    arcpy.AddMessage('    Complete')
    return table_path


def species_summary(plot_table, tree_table, fixed_df, out_gdb, level):
    arcpy.AddMessage('--Execute Species Summary on {0}--'.format(level))
    if level != 'PID':

        # Create Base DF
        base_df = fcalc.create_level_df(level, plot_table)
        arcpy.AddMessage("    Base DF Created")

        # UUND_SP1 Most Frequent
        und_sp1_flt = fixed_df[~fixed_df.UND_SP1.isin(['NONE'])]

        und_sp1_freq = fcalc.get_groupby_modes(
            source=und_sp1_flt,
            keys=[level],
            values=['UND_SP1'],
            dropna=True,
            return_counts=False) \
            .set_index(level)
        arcpy.AddMessage("    Und Sp1 Freq Complete ")

        # UND_SP2 Most Frequent
        und_sp2_flt = fixed_df[~fixed_df.UND_SP2.isin(['NONE'])]

        und_sp2_freq = fcalc.get_groupby_modes(
            source=und_sp2_flt,
            keys=[level],
            values=['UND_SP2'],
            dropna=True,
            return_counts=False) \
            .set_index(level)
        arcpy.AddMessage("    Und Sp2 Freq Complete ")

        # UND_SP3 Most Frequent
        und_sp3_flt = fixed_df[~fixed_df.UND_SP3.isin(['NONE'])]

        und_sp3_freq = fcalc.get_groupby_modes(
            source=und_sp3_flt,
            keys=[level],
            values=['UND_SP3'],
            dropna=True,
            return_counts=False) \
            .set_index(level)
        arcpy.AddMessage("    Und Sp3 Freq Complete ")

        # GRD_SP1 Most Frequent
        grd_sp1_flt = fixed_df[~fixed_df.GRD_SP1.isin(['NONE'])]

        grd_sp1_freq = fcalc.get_groupby_modes(
            source=grd_sp1_flt,
            keys=[level],
            values=['GRD_SP1'],
            dropna=True,
            return_counts=False) \
            .set_index(level)
        arcpy.AddMessage("    Grd Sp1 Freq Complete ")

        # GRD_SP2 Most Frequent
        grd_sp2_flt = fixed_df[~fixed_df.GRD_SP2.isin(['NONE'])]

        grd_sp2_freq = fcalc.get_groupby_modes(
            source=grd_sp2_flt,
            keys=[level],
            values=['GRD_SP2'],
            dropna=True,
            return_counts=False) \
            .set_index(level)
        arcpy.AddMessage("    Grd Sp2 Freq Complete Complete ")

        # GRD_SP3 Most Frequent
        grd_sp3_flt = fixed_df[~fixed_df.GRD_SP3.isin(['NONE'])]

        grd_sp3_freq = fcalc.get_groupby_modes(
            source=grd_sp3_flt,
            keys=[level],
            values=['GRD_SP3'],
            dropna=True,
            return_counts=False) \
            .set_index(level)
        arcpy.AddMessage("    Grd Sp3 Freq Complete Complete ")

        # NOT_SP1 Most Frequent
        not_sp1_flt = fixed_df[~fixed_df.NOT_SP1.isin(['NONE'])]

        not_sp1_freq = fcalc.get_groupby_modes(
            source=not_sp1_flt,
            keys=[level],
            values=['NOT_SP1'],
            dropna=True,
            return_counts=False) \
            .set_index(level)
        arcpy.AddMessage("    Notable Sp1 Freq Complete ")

        # NOT_SP2 Most Frequent
        not_sp2_flt = fixed_df[~fixed_df.NOT_SP2.isin(['NONE'])]

        not_sp2_freq = fcalc.get_groupby_modes(
            source=not_sp2_flt,
            keys=[level],
            values=['NOT_SP2'],
            dropna=True,
            return_counts=False) \
            .set_index(level)
        arcpy.AddMessage("    Notable Sp2 Freq Complete ")

        # NOT_SP3 Most Frequent
        not_sp3_flt = fixed_df[~fixed_df.NOT_SP3.isin(['NONE'])]

        not_sp3_freq = fcalc.get_groupby_modes(
            source=not_sp3_flt,
            keys=[level],
            values=['NOT_SP3'],
            dropna=True,
            return_counts=False) \
            .set_index(level)
        arcpy.AddMessage("    Notable Sp3 Freq Complete ")

        # Overstory Sp Stats
        ov_sp = fcalc.top5_ov_species_level(tree_table=tree_table, level=level).set_index(level)
        arcpy.AddMessage("    Overstory Sp Stats Complete ")

        # Merge component dataframes
        sp_summary_df = base_df \
            .join(other=[und_sp1_freq,
                         und_sp2_freq,
                         und_sp3_freq,
                         grd_sp1_freq,
                         grd_sp2_freq,
                         grd_sp3_freq,
                         not_sp1_freq,
                         not_sp2_freq,
                         not_sp3_freq,
                         ov_sp],
                  how='left') \
            .reset_index()
        arcpy.AddMessage("    All Component DFs Merged")

        # Reindex output dataframe
        sp_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                        col_csv='resources/species_summary_cols.csv')
        sp_summary_df = sp_summary_df.reindex(labels=sp_reindex_cols,
                                              axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Handle NAN values for output
        nan_fill_dict = fcalc.fmg_nan_fill(col_csv='resources/species_summary_cols.csv')
        sp_summary_df = sp_summary_df.fillna(value=nan_fill_dict)
        arcpy.AddMessage("    No data/nan values set")

        # Enforce ESRI compatible DTypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/species_summary_cols.csv')
        sp_summary_df = sp_summary_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Export to GDB Table
        table_name = level + '_Species_Summary'
        table_path = os.path.join(out_gdb, table_name)
        sp_summary_df.spatial.to_table(location=table_path, sanitize_columns=False)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    elif level == 'PID':

        # Create Base DF
        base_df = fcalc.create_level_df(level, plot_table)
        arcpy.AddMessage("    Base DF Created")

        # Create Und, Grd, Not df
        columns = ['PID',
                   'UND_SP1', 'UND_SP2', 'UND_SP3',
                   'GRD_SP1', 'GRD_SP2', 'GRD_SP3',
                   'NOT_SP1', 'NOT_SP2', 'NOT_SP3']

        und_grd_not_sp = fixed_df[columns].set_index('PID')
        arcpy.AddMessage("    UND, GRD, NOT Sp Stats Created")

        # Create ov sp df
        ov_sp = fcalc.top5_ov_species_plot(tree_table=tree_table).set_index(level)
        arcpy.AddMessage("    Overstory Sp Stats Complete ")

        # Merge component dataframes
        sp_summary_df = base_df \
            .join(other=[und_grd_not_sp,
                         ov_sp],
                  how='left') \
            .reset_index()
        arcpy.AddMessage("    All Component DFs Merged")

        # Reindex output dataframe
        sp_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                        col_csv='resources/species_summary_cols.csv')
        sp_summary_df = sp_summary_df.reindex(labels=sp_reindex_cols,
                                              axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Handle NAN values for output
        nan_fill_dict = fcalc.fmg_nan_fill(col_csv='resources/species_summary_cols.csv')
        sp_summary_df = sp_summary_df.fillna(value=nan_fill_dict)
        arcpy.AddMessage("    No data/nan values set")

        # Enforce ESRI compatible DTypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/species_summary_cols.csv')
        sp_summary_df = sp_summary_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Export to GDB Table
        table_name = 'PID_Species_Summary'
        table_path = os.path.join(out_gdb, table_name)
        sp_summary_df.spatial.to_table(location=table_path, sanitize_columns=False)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    arcpy.AddMessage('    Complete')
    return table_path


def vert_comp_summary(plot_table, tree_table, out_gdb, level):
    arcpy.AddMessage('--Execute Vertical Composition Summary on {0}--'.format(level))
    if level != 'PID':

        # Create base table
        base_df = fcalc.create_level_df(level, plot_table)
        arcpy.AddMessage("    Base DF Created")

        # Run TPA Case with live tree filter to get CNP_TPA, CNP_BA, CNP_QMDBH, MID_TPA, MID_BA, MID_QMDBH
        vc_live_tpa = fcalc.tpa_ba_qmdbh_level_by_case(tree_table=tree_table,
                                                       filter_statement=~tree_table.TR_HLTH.isin(["D", "DEAD"]),
                                                       case_column='VERT_COMP',
                                                       level=level)
        vc_live_tpa = vc_live_tpa \
            .rename(columns={'BA_VERT_COMP_Canopy': 'CNP_BA',
                             'QM_DBH_VERT_COMP_Canopy': 'CNP_QMDBH',
                             'TPA_VERT_COMP_Canopy': 'CNP_TPA',
                             'BA_VERT_COMP_Midstory': 'MID_BA',
                             'QM_DBH_VERT_COMP_Midstory': 'MID_QMDBH',
                             'TPA_VERT_COMP_Midstory': 'MID_TPA'}) \
            .set_index(level)
        arcpy.AddMessage("    Live TPA, BA, QM DBH for vert comp created")

        # Run TPA Case with dead tree filter to get CNP_D_TPA, CNP_D_BA, CNP_D_QMDBH, MID_D_TPA, MID_D_BA, MID_D_QMDBH
        vc_dead_tpa = fcalc.tpa_ba_qmdbh_level_by_case(tree_table=tree_table,
                                                       filter_statement=tree_table.TR_HLTH.isin(["D", "DEAD"]),
                                                       case_column='VERT_COMP',
                                                       level=level)
        vc_dead_tpa = vc_dead_tpa \
            .rename(columns={'BA_VERT_COMP_Canopy': 'CNP_D_BA',
                             'QM_DBH_VERT_COMP_Canopy': 'CNP_D_QMDBH',
                             'TPA_VERT_COMP_Canopy': 'CNP_D_TPA',
                             'BA_VERT_COMP_Midstory': 'MID_D_BA',
                             'QM_DBH_VERT_COMP_Midstory': 'MID_D_QMDBH',
                             'TPA_VERT_COMP_Midstory': 'MID_D_TPA'}) \
            .set_index(level)
        arcpy.AddMessage("    Dead TPA, BA, QM DBH for vert comp created")

        # Run SP Prev Pct with Canopy (VERT_COMP) filter to get CNP_DOM_SP, CNP_DOM_SP_PCMP
        # Create Typical Species dominant species
        cnp_dom_sp_df = fcalc.species_dom_level(tree_table=tree_table,
                                                filter_statement=tree_table['VERT_COMP'] == 'Canopy',
                                                level=level)
        cnp_dom_sp_df = cnp_dom_sp_df\
            .rename(columns={'SP_DOM': 'CNP_DOM_SP', 'SP_DOM_PCMP': 'CNP_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Canopy Dom species created")

        # Run SP Prev Pct with Midstory (VERT_COMP) filter to get MID_DOM_SP, MID_DOM_SP_PCMP
        mid_dom_sp_df = fcalc.species_dom_level(tree_table=tree_table,
                                                filter_statement=tree_table['VERT_COMP'] == 'Midstory',
                                                level=level)
        mid_dom_sp_df = mid_dom_sp_df\
            .rename(columns={'SP_DOM': 'MID_DOM_SP', 'SP_DOM_PCMP': 'MID_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Midstory Dom species created")

        # Run SP Prev Pct with Intermediate (TR_CL==I) filter to get INT_DOM_SP, INT_DOM_SP_PCMP
        int_dom_sp_df = fcalc.species_dom_level(tree_table=tree_table,
                                                filter_statement=tree_table['TR_CL'] == 'I',
                                                level=level)
        int_dom_sp_df = int_dom_sp_df\
            .rename(columns={'SP_DOM': 'INT_DOM_SP', 'SP_DOM_PCMP': 'INT_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Intermediate Dom species created")

        # Run HLTH Prev Pct with Canopy (VERT_COMP) filter to get CNP_DOM_HLTH, CNP_DOM_HLTH_PCMP
        cnp_dom_hlth_df = fcalc.health_dom_level(tree_table=tree_table,
                                                 filter_statement=tree_table['VERT_COMP'] == 'Canopy',
                                                 level=level)
        cnp_dom_hlth_df = cnp_dom_hlth_df\
            .rename(columns={'HLTH_DOM': 'CNP_DOM_HLTH', 'HLTH_DOM_PCMP': 'CNP_DOM_HLTH_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Canopy Dom health created")

        # Run HLTH Prev Pct with Midstory (VERT_COMP) filter to get MID_DOM_HLTH, MID_DOM_HLTH_PCMP
        mid_dom_hlth_df = fcalc.health_dom_level(tree_table=tree_table,
                                                 filter_statement=tree_table['VERT_COMP'] == 'Midstory',
                                                 level=level)
        mid_dom_hlth_df = mid_dom_hlth_df\
            .rename(columns={'HLTH_DOM': 'MID_DOM_HLTH', 'HLTH_DOM_PCMP': 'MID_DOM_HLTH_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Midstory Dom health created")

        # Run HLTH Prev Pct with Intermediate (TR_CL==I) filter to get INT_DOM_HLTH, INT_DOM_HLTH_PCMP
        int_dom_hlth_df = fcalc.health_dom_level(tree_table=tree_table,
                                                 filter_statement=tree_table['TR_CL'] == 'I',
                                                 level=level)
        int_dom_hlth_df = int_dom_hlth_df\
            .rename(columns={'HLTH_DOM': 'INT_DOM_HLTH', 'HLTH_DOM_PCMP': 'INT_DOM_HLTH_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Intermediate Dom health created")

        # Merge component dataframes onto the base dataframe
        out_df = base_df \
            .join(other=[vc_live_tpa,
                         vc_dead_tpa,
                         cnp_dom_sp_df,
                         mid_dom_sp_df,
                         int_dom_sp_df,
                         cnp_dom_hlth_df,
                         mid_dom_hlth_df,
                         int_dom_hlth_df],
                  how='left')\
            .reset_index()
        arcpy.AddMessage("    All Component DFs Merged")

        # Reindex output dataframe
        general_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                             col_csv='resources/vertcomp_summary_cols.csv')
        out_df = out_df.reindex(labels=general_reindex_cols,
                                axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Handle NaN values appropriately
        nan_fill_dict_level = fcalc.fmg_nan_fill(col_csv='resources/vertcomp_summary_cols.csv')
        out_df = out_df.fillna(value=nan_fill_dict_level)
        arcpy.AddMessage("    Nan Values Filled")

        # Enforce ESRI compatible Dtypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/vertcomp_summary_cols.csv')
        out_df = out_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Export to gdb table
        table_name = level + "_Vert_Comp_Summary"
        table_path = os.path.join(out_gdb, table_name)
        out_df.spatial.to_table(location=table_path, sanitize_columns=False)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    if level == 'PID':

        # Create base table
        base_df = fcalc.create_level_df(level, plot_table)
        arcpy.AddMessage("    Base DF Created")

        # Run TPA Case with live tree filter to get CNP_TPA, CNP_BA, CNP_QMDBH, MID_TPA, MID_BA, MID_QMDBH
        vc_live_tpa = fcalc.tpa_ba_qmdbh_plot_by_case(tree_table=tree_table,
                                                      filter_statement=~tree_table.TR_HLTH.isin(["D", "DEAD"]),
                                                      case_column='VERT_COMP')

        vc_live_tpa = vc_live_tpa \
            .rename(columns={'BA_VERT_COMP_Canopy': 'CNP_BA',
                             'QM_DBH_VERT_COMP_Canopy': 'CNP_QMDBH',
                             'TPA_VERT_COMP_Canopy': 'CNP_TPA',
                             'BA_VERT_COMP_Midstory': 'MID_BA',
                             'QM_DBH_VERT_COMP_Midstory': 'MID_QMDBH',
                             'TPA_VERT_COMP_Midstory': 'MID_TPA'}) \
            .set_index(level)
        arcpy.AddMessage("    Live TPA, BA, QM DBH for vert comp created")

        # Run TPA Case with dead tree filter to get CNP_D_TPA, CNP_D_BA, CNP_D_QMDBH, MID_D_TPA, MID_D_BA, MID_D_QMDBH
        vc_dead_tpa = fcalc.tpa_ba_qmdbh_plot_by_case(tree_table=tree_table,
                                                      filter_statement=tree_table.TR_HLTH.isin(["D", "DEAD"]),
                                                      case_column='VERT_COMP')

        vc_dead_tpa = vc_dead_tpa \
            .rename(columns={'BA_VERT_COMP_Canopy': 'CNP_D_BA',
                             'QM_DBH_VERT_COMP_Canopy': 'CNP_D_QMDBH',
                             'TPA_VERT_COMP_Canopy': 'CNP_D_TPA',
                             'BA_VERT_COMP_Midstory': 'MID_D_BA',
                             'QM_DBH_VERT_COMP_Midstory': 'MID_D_QMDBH',
                             'TPA_VERT_COMP_Midstory': 'MID_D_TPA'}) \
            .set_index(level)
        arcpy.AddMessage("    Dead TPA, BA, QM DBH for vert comp created")

        # Run SP Prev Pct with Canopy (VERT_COMP) filter to get CNP_DOM_SP, CNP_DOM_SP_PCMP
        # Create Typical Species dominant species
        cnp_dom_sp_df = fcalc.species_dom_plot(tree_table=tree_table,
                                               filter_statement=tree_table['VERT_COMP'] == 'Canopy')

        cnp_dom_sp_df = cnp_dom_sp_df \
            .rename(columns={'SP_DOM': 'CNP_DOM_SP', 'SP_DOM_PCMP': 'CNP_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Canopy Dom species created")

        # Run SP Prev Pct with Midstory (VERT_COMP) filter to get MID_DOM_SP, MID_DOM_SP_PCMP
        mid_dom_sp_df = fcalc.species_dom_plot(tree_table=tree_table,
                                               filter_statement=tree_table['VERT_COMP'] == 'Midstory')

        mid_dom_sp_df = mid_dom_sp_df \
            .rename(columns={'SP_DOM': 'MID_DOM_SP', 'SP_DOM_PCMP': 'MID_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Midstory Dom species created")

        # Run SP Prev Pct with Intermediate (TR_CL==I) filter to get INT_DOM_SP, INT_DOM_SP_PCMP
        int_dom_sp_df = fcalc.species_dom_plot(tree_table=tree_table,
                                               filter_statement=tree_table['TR_CL'] == 'I')

        int_dom_sp_df = int_dom_sp_df \
            .rename(columns={'SP_DOM': 'INT_DOM_SP', 'SP_DOM_PCMP': 'INT_DOM_SP_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Intermediate Dom species created")

        # Run HLTH Prev Pct with Canopy (VERT_COMP) filter to get CNP_DOM_HLTH, CNP_DOM_HLTH_PCMP
        cnp_dom_hlth_df = fcalc.health_dom_plot(tree_table=tree_table,
                                                filter_statement=tree_table['VERT_COMP'] == 'Canopy')

        cnp_dom_hlth_df = cnp_dom_hlth_df \
            .rename(columns={'HLTH_DOM': 'CNP_DOM_HLTH', 'HLTH_DOM_PCMP': 'CNP_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Canopy Dom health created")

        # Run HLTH Prev Pct with Midstory (VERT_COMP) filter to get MID_DOM_HLTH, MID_DOM_HLTH_PCMP
        mid_dom_hlth_df = fcalc.health_dom_plot(tree_table=tree_table,
                                                filter_statement=tree_table['VERT_COMP'] == 'Midstory')

        mid_dom_hlth_df = mid_dom_hlth_df \
            .rename(columns={'HLTH_DOM': 'MID_DOM_HLTH', 'HLTH_DOM_PCMP': 'MID_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Midstory Dom health created")

        # Run HLTH Prev Pct with Intermediate (TR_CL==I) filter to get INT_DOM_HLTH, INT_DOM_HLTH_PCMP
        int_dom_hlth_df = fcalc.health_dom_plot(tree_table=tree_table,
                                                filter_statement=tree_table['TR_CL'] == 'I')

        int_dom_hlth_df = int_dom_hlth_df \
            .rename(columns={'HLTH_DOM': 'INT_DOM_HLTH', 'HLTH_DOM_PCMP': 'INT_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Intermediate Dom health created")

        # Merge component dataframes onto the base dataframe
        out_df = base_df \
            .join(other=[vc_live_tpa,
                         vc_dead_tpa,
                         cnp_dom_sp_df,
                         mid_dom_sp_df,
                         int_dom_sp_df,
                         cnp_dom_hlth_df,
                         mid_dom_hlth_df,
                         int_dom_hlth_df],
                  how='left') \
            .reset_index()
        arcpy.AddMessage("    All Component DFs Merged")

        # Reindex output dataframe
        general_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                             col_csv='resources/vertcomp_summary_cols.csv')
        out_df = out_df.reindex(labels=general_reindex_cols,
                                axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Handle NaN values appropriately
        nan_fill_dict_level = fcalc.fmg_nan_fill(col_csv='resources/vertcomp_summary_cols.csv')
        out_df = out_df.fillna(value=nan_fill_dict_level)
        arcpy.AddMessage("    Nan Values Filled")

        # Enforce ESRI compatible Dtypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/vertcomp_summary_cols.csv')
        out_df = out_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Export to gdb table
        table_name = "PID_Vert_Comp_Summary"
        table_path = os.path.join(out_gdb, table_name)
        out_df.spatial.to_table(location=table_path, sanitize_columns=False)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    arcpy.AddMessage('    Complete')
    return table_path


def management_summary(plot_table, tree_table, out_gdb, level):
    arcpy.AddMessage('--Execute Management Summary on {0}--'.format(level))
    if level != 'PID':

        # Create base table
        base_df = fcalc.create_level_df(level, plot_table)
        arcpy.AddMessage("    Base DF Created")

        # Create Stocking Percent df
        stocking_df = fcalc.tpa_ba_qmdbh_level(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]), level)
        stocking_df['STOCK_PCT'] = fcalc.stocking_pct(stocking_df['TPA'], stocking_df['QM_DBH'])
        stocking_df = stocking_df[[level, 'STOCK_PCT']].set_index(level)

        # Create hard mast stocking percent df
        hm_stocking_df = fcalc.tpa_ba_qmdbh_level(tree_table=tree_table,
                                                  filter_statement=(tree_table['TR_HLTH'] != 'D') &
                                                                   (tree_table['MAST_TYPE'] == 'Hard'),
                                                  level=level)
        hm_stocking_df['STOCK_PCT_HM'] = fcalc.stocking_pct(hm_stocking_df['TPA'], hm_stocking_df['QM_DBH'])
        hm_stocking_df = hm_stocking_df[[level, 'STOCK_PCT_HM']].set_index(level)

        # Create species richness df
        species_richness_df = fcalc.create_sp_richness(tree_table=tree_table,
                                                       plot_table=plot_table,
                                                       level=level)\
                                   .set_index(level)

        # Merge component dfs
        manage_summary_df = base_df \
            .join(other=[stocking_df,
                         hm_stocking_df,
                         species_richness_df],
                  how='left') \
            .reset_index()

        # Reindex output dataframe
        manage_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                            col_csv='resources/management_summary_cols.csv')
        manage_summary_df = manage_summary_df.reindex(labels=manage_reindex_cols,
                                                      axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Enforce ESRI compatible DTypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/management_summary_cols.csv')
        manage_summary_df = manage_summary_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Handle NAN values for output
        nan_fill_dict = fcalc.fmg_nan_fill(col_csv='resources/management_summary_cols.csv')
        manage_summary_df = manage_summary_df.fillna(value=nan_fill_dict)
        arcpy.AddMessage("    No data/nan values set")

        # Export to GDB Table
        table_name = level + '_Management_Summary'
        table_path = os.path.join(out_gdb, table_name)
        manage_summary_df.spatial.to_table(location=table_path, sanitize_columns=False)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    if level == 'PID':

        # Create base table
        base_df = fcalc.create_level_df(level, plot_table)
        arcpy.AddMessage("    Base DF Created")

        # Create Stocking Percent df
        stocking_df = fcalc.tpa_ba_qmdbh_plot(tree_table, ~tree_table.TR_HLTH.isin(["D", "DEAD"]))
        stocking_df['STOCK_PCT'] = fcalc.stocking_pct(stocking_df['TPA'], stocking_df['QM_DBH'])
        stocking_df = stocking_df[[level, 'STOCK_PCT']].set_index(level)

        # Create hard mast stocking percent df
        hm_stocking_df = fcalc.tpa_ba_qmdbh_plot(tree_table=tree_table,
                                                 filter_statement=(tree_table['TR_HLTH'] != 'D') &
                                                                  (tree_table['MAST_TYPE'] == 'Hard'))
        hm_stocking_df['STOCK_PCT_HM'] = fcalc.stocking_pct(hm_stocking_df['TPA'], hm_stocking_df['QM_DBH'])
        hm_stocking_df = hm_stocking_df[[level, 'STOCK_PCT_HM']].set_index(level)

        # Create species richness df
        species_richness_df = fcalc.create_sp_richness(tree_table=tree_table,
                                                       plot_table=plot_table,
                                                       level=level)\
                                   .set_index(level)

        # Merge component dfs
        manage_summary_df = base_df \
            .join(other=[stocking_df,
                         hm_stocking_df,
                         species_richness_df],
                  how='left') \
            .reset_index()

        # Reindex output dataframe
        manage_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                            col_csv='resources/management_summary_cols.csv')
        manage_summary_df = manage_summary_df.reindex(labels=manage_reindex_cols,
                                                      axis='columns')
        arcpy.AddMessage("    Columns reordered")

        # Enforce ESRI compatible DTypes
        dtype_dict = fcalc.fmg_dtype_enforce(col_csv='resources/management_summary_cols.csv')
        manage_summary_df = manage_summary_df.astype(dtype=dtype_dict, copy=False)
        arcpy.AddMessage("    Dtypes Enforced")

        # Handle NAN values for output
        nan_fill_dict = fcalc.fmg_nan_fill(col_csv='resources/management_summary_cols.csv')
        manage_summary_df = manage_summary_df.fillna(value=nan_fill_dict)
        arcpy.AddMessage("    No data/nan values set")

        # Export to GDB Table
        table_name = 'PID_Management_Summary'
        table_path = os.path.join(out_gdb, table_name)
        manage_summary_df.spatial.to_table(location=table_path, sanitize_columns=False)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    arcpy.AddMessage('    Complete')
    return table_path

