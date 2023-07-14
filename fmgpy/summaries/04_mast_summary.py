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
levels = ['PID', 'SID', 'SITE', 'UNIT']

# Loop through levels, producing mast summary table for each
for level in levels:
    if level != 'PID':
        arcpy.AddMessage('Work on {0}'.format(level))

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
        hm_dom_hlth_df = fcalc.health_prev_pct_level(tree_table=tree_table,
                                                     filter_statement=tree_table['MAST_TYPE'] == 'Hard',
                                                     level=level)
        hm_dom_hlth_df = hm_dom_hlth_df\
            .rename(columns={'HLTH_PREV': 'HM_DOM_HLTH', 'HLTH_PREV_PCT': 'HM_DOM_HLTH_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Hard mast dominant health created")

        # Create Species Dom where Mast = Hard
        hm_dom_sp_df = fcalc.species_prev_pct_level(tree_table=tree_table,
                                                    filter_statement=tree_table['MAST_TYPE'] == 'Hard',
                                                    level=level)
        hm_dom_sp_df = hm_dom_sp_df\
            .rename(columns={'SP_PREV': 'HM_DOM_SP', 'SP_PREV_PCT': 'HM_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Hard mast dominant species created")

        # Create Health Dom where Mast = Soft
        sm_dom_hlth_df = fcalc.health_prev_pct_level(tree_table=tree_table,
                                                     filter_statement=tree_table['MAST_TYPE'] == 'Soft',
                                                     level=level)
        sm_dom_hlth_df = sm_dom_hlth_df \
            .rename(columns={'HLTH_PREV': 'SM_DOM_HLTH', 'HLTH_PREV_PCT': 'SM_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Soft mast dominant health created")

        # Create Species Dom where Mast = Soft
        sm_dom_sp_df = fcalc.species_prev_pct_level(tree_table=tree_table,
                                                    filter_statement=tree_table['MAST_TYPE'] == 'Soft',
                                                    level=level)
        sm_dom_sp_df = sm_dom_sp_df\
            .rename(columns={'SP_PREV': 'SM_DOM_SP', 'SP_PREV_PCT': 'SM_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Soft mast dominant species created")

        # Create Health Dom where Mast = Lightseed
        lm_dom_hlth_df = fcalc.health_prev_pct_level(tree_table=tree_table,
                                                     filter_statement=tree_table['MAST_TYPE'] == 'Lightseed',
                                                     level=level)
        lm_dom_hlth_df = lm_dom_hlth_df \
            .rename(columns={'HLTH_PREV': 'LM_DOM_HLTH', 'HLTH_PREV_PCT': 'LM_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Lightseed mast dominant health created")

        # Create Species Dom where Mast = Lightseed
        lm_dom_sp_df = fcalc.species_prev_pct_level(tree_table=tree_table,
                                                    filter_statement=tree_table['MAST_TYPE'] == 'Lightseed',
                                                    level=level)
        lm_dom_sp_df = lm_dom_sp_df\
            .rename(columns={'SP_PREV': 'LM_DOM_SP', 'SP_PREV_PCT': 'LM_DOM_SP_PCMP'})\
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
        mast_summary_df = mast_summary_df.fillna(value={'HM_TPA': 0,
                                                        'HM_BA': 0,
                                                        'HM_QMDBH': 0,
                                                        'HM_DOM_HLTH': 'NONE',
                                                        'HM_DOM_HLTH_PCMP': 0,
                                                        'HM_DOM_SP': 'NONE',
                                                        'HM_DOM_SP_PCMP': 0,
                                                        'SM_TPA': 0,
                                                        'SM_BA': 0,
                                                        'SM_QMDBH': 0,
                                                        'SM_DOM_HLTH': 'NONE',
                                                        'SM_DOM_HLTH_PCMP': 0,
                                                        'SM_DOM_SP': 'NONE',
                                                        'SM_DOM_SP_PCMP': 0,
                                                        'LM_TPA': 0,
                                                        'LM_BA': 0,
                                                        'LM_QMDBH': 0,
                                                        'LM_DOM_HLTH': 'NONE',
                                                        'LM_DOM_HLTH_PCMP': 0,
                                                        'LM_DOM_SP': 'NONE',
                                                        'LM_DOM_SP_PCMP': 0})
        arcpy.AddMessage("    No data/nan values set")

        # Export to GDB Table
        table_name = level + '_Mast_Summary'
        table_path = os.path.join(out_gdb, table_name)
        mast_summary_df.spatial.to_table(table_path)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    elif level == 'PID':
        arcpy.AddMessage('Work on {0}'.format(level))

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
        hm_dom_hlth_df = fcalc.health_prev_pct_plot(tree_table=tree_table,
                                                    filter_statement=tree_table['MAST_TYPE'] == 'Hard')
        hm_dom_hlth_df = hm_dom_hlth_df\
            .rename(columns={'HLTH_PREV': 'HM_DOM_HLTH', 'HLTH_PREV_PCT': 'HM_DOM_HLTH_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Hard mast dominant health created")

        # Create Species Dom where Mast = Hard
        hm_dom_sp_df = fcalc.species_prev_pct_plot(tree_table=tree_table,
                                                   filter_statement=tree_table['MAST_TYPE'] == 'Hard')
        hm_dom_sp_df = hm_dom_sp_df\
            .rename(columns={'SP_PREV': 'HM_DOM_SP', 'SP_PREV_PCT': 'HM_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Hard mast dominant species created")

        # Create Health Dom where Mast = Soft
        sm_dom_hlth_df = fcalc.health_prev_pct_plot(tree_table=tree_table,
                                                    filter_statement=tree_table['MAST_TYPE'] == 'Soft')
        sm_dom_hlth_df = sm_dom_hlth_df \
            .rename(columns={'HLTH_PREV': 'SM_DOM_HLTH', 'HLTH_PREV_PCT': 'SM_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Soft mast dominant health created")

        # Create Species Dom where Mast = Soft
        sm_dom_sp_df = fcalc.species_prev_pct_plot(tree_table=tree_table,
                                                   filter_statement=tree_table['MAST_TYPE'] == 'Soft')
        sm_dom_sp_df = sm_dom_sp_df\
            .rename(columns={'SP_PREV': 'SM_DOM_SP', 'SP_PREV_PCT': 'SM_DOM_SP_PCMP'})\
            .set_index(level)
        arcpy.AddMessage("    Soft mast dominant species created")

        # Create Health Dom where Mast = Lightseed
        lm_dom_hlth_df = fcalc.health_prev_pct_plot(tree_table=tree_table,
                                                    filter_statement=tree_table['MAST_TYPE'] == 'Lightseed')
        lm_dom_hlth_df = lm_dom_hlth_df \
            .rename(columns={'HLTH_PREV': 'LM_DOM_HLTH', 'HLTH_PREV_PCT': 'LM_DOM_HLTH_PCMP'}) \
            .set_index(level)
        arcpy.AddMessage("    Lightseed mast dominant health created")

        # Create Species Dom where Mast = Lightseed
        lm_dom_sp_df = fcalc.species_prev_pct_plot(tree_table=tree_table,
                                                   filter_statement=tree_table['MAST_TYPE'] == 'Lightseed')
        lm_dom_sp_df = lm_dom_sp_df\
            .rename(columns={'SP_PREV': 'LM_DOM_SP', 'SP_PREV_PCT': 'LM_DOM_SP_PCMP'})\
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
        mast_summary_df = mast_summary_df.fillna(value={'HM_TPA': 0,
                                                        'HM_BA': 0,
                                                        'HM_QMDBH': 0,
                                                        'HM_DOM_HLTH': 'NONE',
                                                        'HM_DOM_HLTH_PCMP': 0,
                                                        'HM_DOM_SP': 'NONE',
                                                        'HM_DOM_SP_PCMP': 0,
                                                        'SM_TPA': 0,
                                                        'SM_BA': 0,
                                                        'SM_QMDBH': 0,
                                                        'SM_DOM_HLTH': 'NONE',
                                                        'SM_DOM_HLTH_PCMP': 0,
                                                        'SM_DOM_SP': 'NONE',
                                                        'SM_DOM_SP_PCMP': 0,
                                                        'LM_TPA': 0,
                                                        'LM_BA': 0,
                                                        'LM_QMDBH': 0,
                                                        'LM_DOM_HLTH': 'NONE',
                                                        'LM_DOM_HLTH_PCMP': 0,
                                                        'LM_DOM_SP': 'NONE',
                                                        'LM_DOM_SP_PCMP': 0})
        arcpy.AddMessage("    No data/nan values set")

        # Export to GDB Table
        table_name = level + '_Mast_Summary'
        table_path = os.path.join(out_gdb, table_name)
        mast_summary_df.spatial.to_table(table_path)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

arcpy.AddMessage('Complete')
