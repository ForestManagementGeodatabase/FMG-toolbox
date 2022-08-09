# -*- coding: UTF-8 -*-

"""
Tool Chain Overview -
Convert user selection to a feature layer persisted
Dissolve the feature layer as subsequent buffers are water and forest edge related
From feature layer create persisted water buffer (negative, full)
From feature layer create persisted walkthrough buffer (negative, outside only)
Create Fishnet with label points using feature layer extent info
Using Erase Points remove label points outside of water buffer
Spatial join with FOREST Stand Dataset to populate POOL COMP UNIT SITE STAND Fields
Add PLOT Field
Add Age Field
Add Walkthrough Field
Add WorkUnitName Field
Populate PLOT Field
Populate WorkUnitName
Create layer file from erased points
Create a selection based on walkthrough buffer
Populate walkthrough field based on selection
Remove selection
Persist layer file


Consider creating an option for auto populating Age field based on rules
Need to debug the removal of spatial join business fields
May skip adding the POOL COMP UNIT SITE STAND IDs until the SDE datasets get refined a bit

"""

import arcpy
import os, sys, datetime
from datetime import date

# Define Script Tool Inputs
inPolygon = arcpy.GetParameterAsText(0)
outGeodatabase = arcpy.GetParameterAsText(1)
workUnitName = arcpy.GetParameterAsText(2)
# addFMGIDFields = arcpy.GetParameterAsText(3) #will be boolean
# inPool = arcpy.GetParameterAsText(4)
# inComp = arcpy.GetParameterAsText(5)
# inUnit = arcpy.GetParameterAsText(6)
# inSite = arcpy.GetParameterAsText(7)
# inStand = arcpy.GetParameterAsTextAsText(8)
removeIntermediate = arcpy.GetParameterAsText(3)  # will be boolean
overwriteExisting = arcpy.GetParameterAsText(4)  # will be boolean

# Current Date String
tDate = datetime.date.today().strftime('%Y%m%d')

# Define Outputs
outUserSelection = os.path.join(outGeodatabase, 'UserDefined_PlotArea_{0}'.format(tDate))
outDissolve = os.path.join(outGeodatabase, 'PlotArea_Dissolve_{0}'.format(tDate))
outShoreBuffer = os.path.join(outGeodatabase, 'ShoreBuffer_{0}'.format(tDate))
outWalkBuffer = os.path.join(outGeodatabase, 'WalkBuffer_{0}'.format(tDate))
outFishPoly = os.path.join(outGeodatabase, 'Fish_Net_{0}'.format(tDate))
outFishPoint = os.path.join(outGeodatabase, 'Fish_Net_{0}_label'.format(tDate))
# outPoolJoin = os.path.join(outGeodatabase, 'PoolPlot_{0}'.format(tDate))
# outCompJoin = os.path.join(outGeodatabase, 'CompPlot_{0}'.format(tDate))
# outUnitJoin = os.path.join(outGeodatabase, 'UnitPlot_{0}'.format(tDate))
# outSiteJoin = os.path.join(outGeodatabase, 'SitePlot_{0}'.format(tDate))
# outStandJoin =  os.path.join(outGeodatabase, 'StandPlot_{0}'.format(tDate))
outWalkPoints = os.path.join(outGeodatabase, 'WalkPoints_{0}'.format(tDate))
outPlotPoints = os.path.join(outGeodatabase, 'PlotLocations_{0}'.format(tDate))

# Overwrite Output
if overwriteExisting == 'true':
    arcpy.env.overwriteOutput = True

# Do some initial checks:
# ID_Pairs = [(inPool, 'POOL'), (inComp, 'COMP'), (inUnit, 'UNIT'), (inSite, 'SITE'), (inStand, 'STAND')]
# if addFMGIDFields == 'true':
#    for item in ID_Pairs:
#        if arcpy.Exists(item[0]):
#            arcpy.AddMessage('Dataset {0} exists, field {1} will be added to plots'.format(item[0], item[1]))
#        if not arcpy.Exists(item[0]):
#            arcpy.AddError('No dataset provided for {0}, please provide, quitting...'.format(item[1]))
#            sys.exit(0)
# elif addFMGIDFields != 'true':
#    arcpy.AddMessage('FMG ID Fields will not be populated')

# Persist user selection
arcpy.MakeFeatureLayer_management(in_features=inPolygon,
                                  out_layer='AOI')

arcpy.CopyFeatures_management(in_features='AOI',
                              out_feature_class=os.path.join(outGeodatabase, outUserSelection))

arcpy.AddMessage('User selected area saved')

arcpy.Delete_management(in_data='AOI')

# Set workspace
arcpy.env.Workspace = outGeodatabase

# Dissolve persisted user selection
arcpy.Dissolve_management(in_features=outUserSelection,
                          out_feature_class=outDissolve,
                          multi_part="SINGLE_PART")
arcpy.AddMessage('User selection dissolved')

# Create Shore and Walkthrough Buffers
arcpy.Buffer_analysis(in_features=outDissolve,
                      out_feature_class=outShoreBuffer,
                      buffer_distance_or_field=-2.835,
                      line_side="FULL")
arcpy.AddMessage('Shoreline buffer created')

arcpy.Buffer_analysis(in_features=outDissolve,
                      out_feature_class=outWalkBuffer,
                      buffer_distance_or_field=-42.672,
                      line_side="OUTSIDE_ONLY")
arcpy.AddMessage('Walkthrough buffer created')

# Run Persisted Fishnet
outLayerDesc = arcpy.Describe(outDissolve)
origin = '{0} {1}'.format(str(outLayerDesc.extent.XMin), str(outLayerDesc.extent.YMin))
yaxis = '{0} {1}'.format(str(outLayerDesc.extent.XMin), str(outLayerDesc.extent.YMin + 100))
arcpy.CreateFishnet_management(out_feature_class=outFishPoly,
                               origin_coord=origin,
                               y_axis_coord=yaxis,
                               cell_width='100.584',
                               cell_height='100.584',
                               number_rows='0',
                               number_columns='0',
                               labels='LABELS',
                               template=outDissolve)
arcpy.AddMessage('Fishnet completed')

arcpy.Delete_management(in_data=outFishPoly)

# Remove fishnet points outside of the shore buffer
arcpy.ErasePoint_edit(in_features=outFishPoint,
                      remove_features=outShoreBuffer,
                      operation_type='OUTSIDE')
arcpy.AddMessage('Fishnet points in shoreline buffer removed')

# Attach POOL COMP UNIT SITE STAND IDs - need to figure out how to order this correctly and need to remove the extra
# join fields included
# Intersects = [(inPool, 'POOL', outFishPoint, outPoolJoin),
#              (inComp, 'COMPARTMENT', outPoolJoin, outCompJoin),
#              (inUnit, 'UNIT', outCompJoin, outUnitJoin),
#              (inSite, 'SITE', outUnitJoin, outSiteJoin),
#              (inStand, 'SID', outSiteJoin, outStandJoin)
#              ]
# if addFMGIDFields == 'true':
#    for item in Intersects:
#        fieldmappings = arcpy.FieldMappings()
#        fieldmappings.addTable(item[0])
#        for field in fieldmappings.fields:
#            if field.name != item[1]:
#                fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))
#        fieldmappings.addTable(item[2])
#        arcpy.SpatialJoin_analysis(target_features = item[2],
#                                   join_features = item[0],
#                                   out_feature_class = item[3],
#                                   field_mapping = fieldmappings,
#                                   match_option = 'INTERSECT')
#        arcpy.AddMessage('{0} ID Field added to fishnet points'.format(item[1]))


# Create Plot Point Feature Class
arcpy.AddField_management(in_table=outFishPoint,
                          field_name='PLOT',
                          field_type='SHORT')
arcpy.AddMessage('PLOT field added')

arcpy.AddField_management(in_table=outFishPoint,
                          field_name='AGE',
                          field_type='TEXT',
                          field_length=5)
arcpy.AddMessage('AGE field added')

arcpy.AddField_management(in_table=outFishPoint,
                          field_name='WorkUnitName',
                          field_type='TEXT',
                          field_length=50)
arcpy.AddMessage('WorkUnitName field added')

# Populate plot ID and work unit name
with arcpy.da.UpdateCursor(outFishPoint, ['OID', 'PLOT', 'WorkUnitName']) as cursor:
    for row in cursor:
        row[1] = int(row[0])
        if workUnitName is not None:
            row[2] = workUnitName
        cursor.updateRow(row)
    del row, cursor
arcpy.AddMessage('PLOT and WorkUnitName fields populated')

# Tag walkthrough points
# Select plot points that intersect with walthrough buffer
arcpy.MakeFeatureLayer_management(in_features=outFishPoint,
                                  out_layer='W_Plots')

arcpy.SelectLayerByLocation_management(in_layer='W_Plots',
                                       overlap_type='INTERSECT',
                                       select_features=outWalkBuffer,
                                       selection_type='NEW_SELECTION')
arcpy.AddMessage('Walkthrough selection made')

# Save out selected walkthrough points
arcpy.CopyFeatures_management(in_features='W_Plots',
                              out_feature_class=outWalkPoints)
arcpy.AddMessage('Walkthrough points saved out')

# Calc Walk field
arcpy.AddField_management(in_table=outWalkPoints,
                          field_name='WALK',
                          field_type='TEXT',
                          field_length=5)
arcpy.AddMessage('WALK field added')

with arcpy.da.UpdateCursor(outWalkPoints, ['WALK']) as cursor:
    for row in cursor:
        row[0] = 'W'
        cursor.updateRow(row)
    del row, cursor
arcpy.AddMessage('WALK field populated')

# Join Walk field to all plot points
arcpy.JoinField_management(in_data=outFishPoint,
                           in_field='PLOT',
                           join_table=outWalkPoints,
                           join_field='PLOT',
                           fields=['WALK'])
arcpy.AddMessage('WALK field joined back to plot locations')

# Create Plot Point Feature Class, re-populate PLOT Field
arcpy.CopyFeatures_management(in_features=outFishPoint,
                              out_feature_class=outPlotPoints)

with arcpy.da.UpdateCursor(outPlotPoints, ['OBJECTID', 'PLOT']) as cursor:
    for row in cursor:
        row[1] = int(row[0])
        cursor.updateRow(row)
    del row, cursor

arcpy.AddMessage('Plot location feature class created here: {0}'.format(outPlotPoints))

# Clean Up intermediate datasets
intermediates = [outUserSelection,
                 outDissolve,
                 outShoreBuffer,
                 outWalkBuffer,
                 outFishPoly,
                 outFishPoint,
                 outWalkPoints
                 ]
if removeIntermediate == 'true':
    for dataset in intermediates:
        arcpy.Delete_management(dataset)
    arcpy.AddMessage('Intermediate datasets cleaned up')

# Prompts ESRI Script Tool to return plot locations into map document
returnedPlotPoints = arcpy.SetParameterAsText(5, outPlotPoints)

# Remove join business fields from plot points
# fields1 = [f.name for f in arcpy.ListFields(outPlotPoints, 'TARGET*')]
# for field in fields1:
#    arcpy.DeleteField_management(outPlotPoints, field)
# fields2 = [f2.name for f2 in arcpy.ListFields(outPlotPoints, 'Join*')]
# for field2 in fields2:
#    arcpy.DeleteField_management(outPlotPoints, field2)
# arcpy.AddMessage('Junk fields removed from plot location feature class')
arcpy.AddMessage('Script complete, review plot locations and populate additional fields')
