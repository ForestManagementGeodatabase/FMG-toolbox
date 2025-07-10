### Console Testing Set Up Start
# Do Some Imports
import pandas as pd
import fmgpy.fmglib.forest_calcs as fcalc
import arcpy

# Define Some input data - pool 12 full
output_gdb = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb'
level = 'SID'
age = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Age_QA_20250513'
fixed = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Fixed_QA_20250513'
prism = r'C:\Users\b5ecdiws\Documents\FMG\fmg_test_data\FMG_FieldData_QA_20250513\FMG_FieldData_QA_20250513.gdb\Prism_QA_20250513'
filter_statement = None

# Define some input data - null return on inv_sp
# output_gdb = r'C:\LocalProjects\FMG\LocalWorking\FMG_Code_Testing.gdb'
# level = 'SID'
# age = r'C:\LocalProjects_ProWorkspace\FMG_Testing_20240724\FMG_FieldData_QA_20240930.gdb\Age_QA_20240930'
# fixed = r'C:\LocalProjects_ProWorkspace\FMG_Testing_20240724\FMG_FieldData_QA_20240930.gdb\Fixed_QA_20240930'
# prism = r'C:\LocalProjects_ProWorkspace\FMG_Testing_20240724\FMG_FieldData_QA_20240930.gdb\Prism_QA_20240930'
# filter_statement = None
#
# age = r'\\mvd.ds.usace.army.mil\mvr\EGIS\Work\FMG\MVR_Working\Summaries\Pool_18\Pool18_Forest_Summaries_HREP_20241001.gdb\AGE_PLOTS'
# fixed = r'\\mvd.ds.usace.army.mil\mvr\EGIS\Work\FMG\MVR_Working\Summaries\Pool_18\Pool18_Forest_Summaries_HREP_20241001.gdb\FIXED_PLOTS'
# prism = r'\\mvd.ds.usace.army.mil\mvr\EGIS\Work\FMG\MVR_Working\Summaries\Pool_18\Pool18_Forest_Summaries_HREP_20241001.gdb\PRISM_PLOTS'

# Reimport statements for dev changes
# importlib.reload(arcpy)
# importlib.reload(fcalc)
# importlib.reload(tcalc)

# Create dataframes
age_df = pd.DataFrame.spatial.from_featureclass(age)
fixed_df = pd.DataFrame.spatial.from_featureclass(fixed)
prism_df = pd.DataFrame.spatial.from_featureclass(prism)
tree_table = fcalc.create_tree_table(prism_df)
plot_table = fcalc.create_plot_table(fixed_df, age_df)
#
# pid_sum = 'True'
# sid_sum = 'True'
# site_sum = 'False'
# unit_sum = 'false'
# comp_sum = 'true'
# pool_sum = 'True'
#
# if pid_sum.lower() == 'true':
#     levels.append('PID')
# else:
#     pass
#
# if sid_sum.lower() == 'true':
#     levels.append('SID')
# else:
#     pass
#
# if site_sum.lower() == 'true':
#     levels.append('SITE')
# else:
#     pass
#
# if unit_sum.lower() == 'true':
#     levels.append('UNIT')
# else:
#     pass
#
# if comp_sum.lower() == 'true':
#     levels.append('COMP')
# else:
#     pass
#
# if pool_sum.lower() == 'true':
#     levels.append('POOL')
# else:
#     pass