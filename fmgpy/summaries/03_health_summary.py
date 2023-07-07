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
out_gdb = r"C:\LocalProjects\FMG\FMG_CODE_TESTING.gdb"

# Import ESRI feature classes as pandas dataframes
prism_df = pd.DataFrame.spatial.from_featureclass(prism_fc)

# Create base datasets
tree_table = fcalc.create_tree_table(prism_df=prism_df)

# Allow output overwrite during testing
arcpy.env.overwriteOutput = True

# Define list of levels
levels = ['PID', 'SID', 'SITE', 'UNIT']

# loop through levels, producing general description table for each
for level in levels:
    if level != 'PID':

        # Create TPA, BA, QMDBH for each health class
        tpa_ba_qmdbh_base_df = fcalc.tpa_ba_qmdbh_level_by_case(tree_table=tree_table,
                                                                filter_statement=None,
                                                                case_column='TR_HLTH',
                                                                level=level)

        # Create Species Dom where Health = D
        sp_dom_d_df = fcalc.species_prev_pct_level(tree_table=tree_table,
                                                   filter_statement=tree_table['TR_HLTH'] == 'D',
                                                   level=level)
        sp_dom_d_df = sp_dom_d_df\
            .rename(columns={'SP_PREV': 'DEAD_DOM_SP', 'SP_PREV_PCT': 'DEAD_DOM_SP_PCMP'}) \
            .set_index(level)


        # Create Species Dom where Health = SD
        sp_dom_sd_df = fcalc.species_prev_pct_level(tree_table=tree_table,
                                                    filter_statement=tree_table['TR_HLTH'] == 'SD',
                                                    level=level)
        sp_dom_sd_df = sp_dom_sd_df\
            .rename(columns={'SP_PREV': 'SD_DOM_SP', 'SP_PREV_PCT': 'SD_DOM_SP_PCMP'})\
            .reset_index(level)

        # Create Species Dom where Health = S
        sp_dom_s_df = fcalc.species_prev_pct_level(tree_table=tree_table,
                                                   filter_statement=tree_table['TR_HLTH'] == 'S',
                                                   level=level)
        sp_dom_s_df = sp_dom_s_df\
            .rename(columns={'SP_PREV': 'STR_DOM_SP', 'SP_PREV_PCT': 'STR_DOM_SP_PCMP'})\
            .reset_index(level)

        # Create Species Dom where Health = H
        sp_dom_h_df = fcalc.species_prev_pct_level(tree_table=tree_table,
                                                   filter_statement=tree_table['TR_HLTH'] == 'H',
                                                   level=level)




