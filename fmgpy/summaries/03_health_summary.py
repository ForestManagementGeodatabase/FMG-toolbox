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

# Define inputs
prism_fc = r"C:\LocalProjects\FMG\FMG-toolbox\test\data\FMG_OracleSchema.gdb\PRISM_PLOTS"
fixed_fc = r"C:\LocalProjects\FMG\FMG-toolbox\test\data\FMG_OracleSchema.gdb\FIXED_PLOTS"
age_fc = r"C:\LocalProjects\FMG\FMG-toolbox\test\data\FMG_OracleSchema.gdb\AGE_PLOTS"
out_gdb = r"C:\LocalProjects\FMG\FMG_CODE_TESTING.gdb"

# Import ESRI feature classes as pandas dataframes
fixed_df = pd.DataFrame.spatial.from_featureclass(fixed_fc)
age_df = pd.DataFrame.spatial.from_featureclass(age_fc)
prism_df = pd.DataFrame.spatial.from_featureclass(prism_fc)

# Create base datasets
plot_table = fcalc.create_plot_table(fixed_df=fixed_df, age_df=age_df)
tree_table = fcalc.create_tree_table(prism_df=prism_df)

# Allow output overwrite during testing
arcpy.env.overwriteOutput = True

# Define list of levels
levels = ['PID', 'SID', 'SITE', 'UNIT', 'COMP', 'POOL']

# loop through levels, producing healthy summary table for each
for level in levels:
    if level != 'PID':
        arcpy.AddMessage('Work on {0}'.format(level))

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
        health_summary_df = health_summary_df.fillna(value={'DEAD_TPA': 0,
                                                            'DEAD_BA': 0,
                                                            'DEAD_QMDBH': 0,
                                                            'DEAD_DOM_SP': 'NONE',
                                                            'DEAD_DOM_SP_PCMP': 0,
                                                            'SD_TPA': 0,
                                                            'SD_BA': 0,
                                                            'SD_QMDBH': 0,
                                                            'SD_DOM_SP': 'NONE',
                                                            'SD_DOM_SP_PCMP': 0,
                                                            'STR_TPA': 0,
                                                            'STR_BA': 0,
                                                            'STR_QMDBH': 0,
                                                            'STR_DOM_SP': 'NONE',
                                                            'STR_DOM_SP_PCMP': 0,
                                                            'HLTH_TPA': 0,
                                                            'HLTH_BA': 0,
                                                            'HLTH_QMDBH': 0,
                                                            'HLTH_DOM_SP': 'NONE',
                                                            'HLTH_DOM_SP_PCMP': 0,
                                                            'LG_D_TPA': 0,
                                                            'DOM_HLTH': 'NONE',
                                                            'DOM_HLTH_PCMP': 0,
                                                            'DOM_SP': 'NONE',
                                                            'DOM_SP_PCMP': 0,
                                                            'TYP_SP_DOM_HLTH': 'NONE',
                                                            'TYP_SP_DOM_HLTH_PCMP': 0,
                                                            'TYP_DOM_SP': 'NONE',
                                                            'TYP_DOM_SP_PCMP': 0,
                                                            'NTYP_SP_DOM_HLTH': 'NONE',
                                                            'NTYP_SP_DOM_HLTH_PCMP': 0,
                                                            'NTYP_DOM_SP': 'NONE',
                                                            'NTYP_DOM_SP_PCMP': 0})
        arcpy.AddMessage("    No data/nan values set")

        # Export to GDB Table
        table_name = level + '_Health_Summary'
        table_path = os.path.join(out_gdb, table_name)
        health_summary_df.spatial.to_table(table_path)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    elif level == 'PID':
        arcpy.AddMessage('Work on {0}'.format(level))

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
        health_summary_df = health_summary_df.fillna(value={'DEAD_TPA': 0,
                                                            'DEAD_BA': 0,
                                                            'DEAD_QMDBH': 0,
                                                            'DEAD_DOM_SP': 'NONE',
                                                            'DEAD_DOM_SP_PCMP': 0,
                                                            'SD_TPA': 0,
                                                            'SD_BA': 0,
                                                            'SD_QMDBH': 0,
                                                            'SD_DOM_SP': 'NONE',
                                                            'SD_DOM_SP_PCMP': 0,
                                                            'STR_TPA': 0,
                                                            'STR_BA': 0,
                                                            'STR_QMDBH': 0,
                                                            'STR_DOM_SP': 'NONE',
                                                            'STR_DOM_SP_PCMP': 0,
                                                            'HLTH_TPA': 0,
                                                            'HLTH_BA': 0,
                                                            'HLTH_QMDBH': 0,
                                                            'HLTH_DOM_SP': 'NONE',
                                                            'HLTH_DOM_SP_PCMP': 0,
                                                            'LG_D_TPA': 0,
                                                            'DOM_HLTH': 'NONE',
                                                            'DOM_HLTH_PCMP': 0,
                                                            'DOM_SP': 'NONE',
                                                            'DOM_SP_PCMP': 0,
                                                            'TYP_SP_DOM_HLTH': 'NONE',
                                                            'TYP_SP_DOM_HLTH_PCMP': 0,
                                                            'TYP_DOM_SP': 'NONE',
                                                            'TYP_DOM_SP_PCMP': 0,
                                                            'NTYP_SP_DOM_HLTH': 'NONE',
                                                            'NTYP_SP_DOM_HLTH_PCMP': 0,
                                                            'NTYP_DOM_SP': 'NONE',
                                                            'NTYP_DOM_SP_PCMP': 0})
        arcpy.AddMessage("    No data/nan values set")

        # Export to GDB Table
        table_name = level + '_Health_Summary'
        table_path = os.path.join(out_gdb, table_name)
        health_summary_df.spatial.to_table(table_path)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

arcpy.AddMessage('Complete')
