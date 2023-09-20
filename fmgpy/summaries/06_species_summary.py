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

for level in levels:
    if level != 'PID':

        arcpy.AddMessage('Work on {0}'.format(level))

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
            return_counts=False)\
            .set_index(level)
        arcpy.AddMessage("    Und Sp1 Freq Complete ")

        # UND_SP2 Most Frequent
        und_sp2_flt = fixed_df[~fixed_df.UND_SP2.isin(['NONE'])]

        und_sp2_freq = fcalc.get_groupby_modes(
            source=und_sp2_flt,
            keys=[level],
            values=['UND_SP2'],
            dropna=True,
            return_counts=False)\
            .set_index(level)
        arcpy.AddMessage("    Und Sp2 Freq Complete ")

        # UND_SP3 Most Frequent
        und_sp3_flt = fixed_df[~fixed_df.UND_SP3.isin(['NONE'])]

        und_sp3_freq = fcalc.get_groupby_modes(
            source=und_sp3_flt,
            keys=[level],
            values=['UND_SP3'],
            dropna=True,
            return_counts=False)\
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
        sp_summary_df = base_df\
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
                   how='left')\
            .reset_index()
        arcpy.AddMessage("    All Component DFs Merged")

        # Reindex output dataframe
        sp_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                        col_csv='resources/species_summary_cols.csv')
        size_summary_df = sp_summary_df.reindex(labels=sp_reindex_cols,
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
        sp_summary_df.spatial.to_table(table_path)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))

    elif level == 'PID':

        arcpy.AddMessage('Work on {0}'.format(level))

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
        sp_summary_df = base_df\
            .join(other=[und_grd_not_sp,
                         ov_sp],
                  how='left')\
            .reset_index()
        arcpy.AddMessage("    All Component DFs Merged")

        # Reindex output dataframe
        sp_reindex_cols = fcalc.fmg_column_reindex_list(level=level,
                                                        col_csv='resources/species_summary_cols.csv')
        size_summary_df = sp_summary_df.reindex(labels=sp_reindex_cols,
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
        sp_summary_df.spatial.to_table(table_path)
        arcpy.AddMessage('    Merged df exported to {0}'.format(table_path))






