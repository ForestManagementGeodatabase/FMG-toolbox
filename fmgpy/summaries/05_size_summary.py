# Do some imports
import os
import sys
import arcpy
import arcgis
import math
import pandas as pd
import numpy as np
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import fmgpy.summaries.forest_calcs as fcalc


# Loop through levels, producing mast summary table for each
def size_summary(plot_table, tree_table, out_gdb, level):
    arcpy.AddMessage('--Execute Size Summary--')
    if level != 'PID':
        arcpy.AddMessage('Work on {0}'.format(level))

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
        size_summary_df.spatial.to_table(table_path)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    elif level == 'PID':
        arcpy.AddMessage('Work on {0}'.format(level))

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
        size_summary_df.spatial.to_table(table_path)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    arcpy.AddMessage('Complete')
    return table_path



