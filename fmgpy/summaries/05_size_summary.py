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
        arcpy.AddMessage("    Hard mast dominant species created")

        # Create Dominant Health where tree size = pole
        pol_dom_hlth =
        # Create Dominant Species where tree size = pole
        pol_dom_sp =
        # Create Dominant Health where tree size = saw
        saw_dom_hlth =
        # Create Dominant Species where tree size = saw
        saw_dom_sp =
        # Create Dominant Health where tree size = mature
        mat_dom_hlth =
        # Create Dominant Species where tree size = mature
        mat_dom_sp =
        # Create Dominant Health where tree size = over mature
        ovm_dom_hlth =
        # Create Dominant Species where tree size = over mature
        ovm_dom_sp =

        # Create BA, TPA, QMDBH for large wildlife trees
        # Create Dominant Health for large wildlife trees
        # Create Dominant Species for large wildlife trees
