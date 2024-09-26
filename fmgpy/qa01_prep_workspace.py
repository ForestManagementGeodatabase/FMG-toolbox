# -*- coding: UTF-8 -*-

import datetime
import os
import arcpy
import importlib

importlib.reload(arcpy)

# define input parameters
destinationFolder = arcpy.GetParameterAsText(0)
inFixed = arcpy.GetParameterAsText(1)
inPrism = arcpy.GetParameterAsText(2)
inAge = arcpy.GetParameterAsText(3)
inPlot = arcpy.GetParameterAsText(4)

# define global date string used for naming
tDate = datetime.date.today().strftime('%Y%m%d')

# create QA geodatabase
gdbName = f'FMG_FieldData_QA_{tDate}'

arcpy.CreateFileGDB_management(out_folder_path=destinationFolder,
                               out_name=gdbName,
                               out_version='CURRENT')

arcpy.AddMessage(f'Working GDB {gdbName} created')


def save_qa_fc(fc, name, date, folder, gdb):
    out_name = f'{name}_QA_{date}'
    out_path = os.path.join(folder, gdb + '.gdb', out_name)
    fc_out = arcpy.CopyFeatures_management(in_features=fc,
                                           out_feature_class=out_path)
    arcpy.AddMessage(f'{name} copied to {out_path}')
    return fc_out


out_fixed = save_qa_fc(inFixed, 'Fixed', tDate, destinationFolder, gdbName)
out_prism = save_qa_fc(inPrism, 'Prism', tDate, destinationFolder, gdbName)
out_age = save_qa_fc(inAge, 'Age', tDate, destinationFolder, gdbName)
out_plot = save_qa_fc(inPlot, 'Plot', tDate, destinationFolder, gdbName)

arcpy.SetParameterAsText(5, out_fixed)
arcpy.SetParameterAsText(6, out_prism)
arcpy.SetParameterAsText(7, out_age)
arcpy.SetParameterAsText(8, out_plot)

# for fc in FCs:
#     outName = f'{fc[1]}_QA_{tDate}'
#     outPath = os.path.join(destinationFolder, gdbName + '.gdb', outName)
#     arcpy.CopyFeatures_management(in_features=fc[0],
#                                   out_feature_class=outPath)
#     arcpy.AddMessage(f'{fc[1]} copied to {outPath}')
