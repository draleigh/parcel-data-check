#-------------------------------------------------------------------------------
# Name:        Parcel Status Analysis (with Road Type Checkups)
# Purpose:      For checking on the status of parcels within specific counties
#                   to determine whether extra effort is required to find 
#                   full parcel datasets from specific counties (including 
#                   checking on null entries and presence of road type descriptors).
# Author:      draleigh
#
# Created:     25 October 2022
# Copyright:   (c) draleigh 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------




# Import packages and modules
import os,arcpy,time,datetime,copy                          # list of packages that will be needed
from datetime import date, timedelta                        # extract the modules
from arcpy import env                                       # extract the module
from arcpy.sa import *                                      # load all modules in the arcpy.sa path
arcpy.CheckOutExtension("Spatial")                          # retrieve the Spatial Analyst extension license

# Define Data Locations and Other Variables
Parcels = *path to parcel shapefile*
Counties = *path to county shapefile*
# This may need to be adjusted once the final DPA numbers are confirmed/updated (or from year to year):
Selector = *path to "Selector" shapefile*
Metadata = *path to "Selector" shapefile*

Selected_Counties = []                                  # set up list to contain names of counties
Selected_Counties_To_Go = []                            # holds a copy of Selected_Counties
Selected_Add_Counties_To_Go = []                        # holds a further copy of Selected_Counties from Selected_Counties_To_Go
start_time = time.time()                                # define the start time of the script's run

# Set up expressions to be used for road type checkups
field_list = ['OWN_ADD_L1', 'OWN_ADD_L2', 'OWN_ADD_L3', 'OWN_ADD_L4', 'TAX_ADD_L1', 'TAX_ADD_L2', 'TAX_ADD_L3', 'TAX_ADD_L4']
Road_Type = ['Ave', 'Avenue', 'Blvd', 'Boulevard', 'Cir', 'Circle', 'Court', 'Ct', 'Dr', 'Drive', 'Highway', 'Hwy', 'Lane', 'Ln', 'Parkway', 'Path', 'Pkwy', 'Pl', 'Place', 'Rd', 'Road', 'Street', 'St', 'Trail', 'Trl', 'Way']
Road_Types = []         # this will hold the eventual expression for road types
#Road_Types = ["' Ave'", "' Avenue'", "' Blvd'", "' Boulevard'", "' Court'", "' Ct'", "' Dr'", "' Drive'", "' Highway'", "' Hwy'", "' Lane'", "' Ln'", "' Parkway'", "' Path'", "' Pkwy'", "' Rd'", "' Road'", "' Street'", "' St'", "' Trail'", "' Trl'", "' Way'"]
OA1_RoadExp = ''                        # holding string for expected expression
OA2_RoadExp = ''                        # holding string for expected expression
OA3_RoadExp = ''                        # holding string for expected expression
OA4_RoadExp = ''                        # holding string for expected expression
TA1_RoadExp = ''                        # holding string for expected expression
TA2_RoadExp = ''                        # holding string for expected expression
TA3_RoadExp = ''                        # holding string for expected expression
TA4_RoadExp = ''                        # holding string for expected expression

# Set up 'Road_Types' list (which could be adjusted based on changes to the 'Road_Type' list before it):
for j in range(len(Road_Type)):                                                                             # set up a FOR loop to iterate over the Road_Type list
    Road_Types = Road_Types + ["'% "+Road_Type[j]+"%'"]                                                     # for every entry, add it to the Road_Types list with the format required for addition to a SQL expression

# Set up iteration expressions:

#OWNER_ADD_1 Expression
for i in range(len(Road_Types)):                                                                            # set up a FOR loop to iterate over the Road_Types list
    OA1_RoadExp = OA1_RoadExp + str(field_list[0] + ' LIKE {} '.format(Road_Types[i]) + 'OR ')              # for every entry, add it to OA1_RoadExp so that each entry has the appropriate SQL format (e.g. "'OWN_ADD_L1' LIKE 'Ave' OR ")
OA1_RoadExp = OA1_RoadExp[:-4]                                                                              # when the FOR loop has finished, truncate the last four digits of the string to remove the final " OR "
#print(OA1_RoadExp)                                                                                         # print that expression to terminal if desired
#OWNER_ADD_2 Expression
for i in range(len(Road_Types)):                                                                            # set up a FOR loop to iterate over the Road_Types list
    OA2_RoadExp = OA2_RoadExp + str(field_list[1] + ' LIKE {} '.format(Road_Types[i]) + 'OR ')              # for every entry, add it to OA2_RoadExp so that each entry has the appropriate SQL format (e.g. "'OWN_ADD_L2' LIKE 'Ave' OR ")
OA2_RoadExp = OA2_RoadExp[:-4]                                                                              # when the FOR loop has finished, truncate the last four digits of the string to remove the final " OR "
#print(OA2_RoadExp)                                                                                         # print that expression to terminal if desired
#OWNER_ADD_3 Expression
for i in range(len(Road_Types)):                                                                            # set up a FOR loop to iterate over the Road_Types list
    OA3_RoadExp = OA3_RoadExp + str(field_list[2] + ' LIKE {} '.format(Road_Types[i]) + 'OR ')              # for every entry, add it to OA3_RoadExp so that each entry has the appropriate SQL format (e.g. "'OWN_ADD_L3' LIKE 'Ave' OR ")
OA3_RoadExp = OA3_RoadExp[:-4]                                                                              # when the FOR loop has finished, truncate the last four digits of the string to remove the final " OR "
#print(OA3_RoadExp)                                                                                         # print that expression to terminal if desired
#OWNER_ADD_4 Expression
for i in range(len(Road_Types)):                                                                            # set up a FOR loop to iterate over the Road_Types list
    OA4_RoadExp = OA4_RoadExp + str(field_list[3] + ' LIKE {} '.format(Road_Types[i]) + 'OR ')              # for every entry, add it to OA4_RoadExp so that each entry has the appropriate SQL format (e.g. "'OWN_ADD_L4' LIKE 'Ave' OR ")
OA4_RoadExp = OA4_RoadExp[:-4]                                                                              # when the FOR loop has finished, truncate the last four digits of the string to remove the final " OR "
#print(OA4_RoadExp)                                                                                         # print that expression to terminal if desired


#TAX_ADD_1 Expression
for i in range(len(Road_Types)):                                                                            # set up a FOR loop to iterate over the Road_Types list
    TA1_RoadExp = TA1_RoadExp + str(field_list[4] + ' LIKE {} '.format(Road_Types[i]) + 'OR ')              # for every entry, add it to TA1_RoadExp so that each entry has the appropriate SQL format (e.g. "'TAX_ADD_L1' LIKE 'Ave' OR ")
TA1_RoadExp = TA1_RoadExp[:-4]                                                                              # when the FOR loop has finished, truncate the last four digits of the string to remove the final " OR "
#print(TA1_RoadExp)                                                                                         # print that expression to terminal if desired
#TAX_ADD_2 Expression
for i in range(len(Road_Types)):                                                                            # set up a FOR loop to iterate over the Road_Types list
    TA2_RoadExp = TA2_RoadExp + str(field_list[5] + ' LIKE {} '.format(Road_Types[i]) + 'OR ')              # for every entry, add it to TA2_RoadExp so that each entry has the appropriate SQL format (e.g. "'TAX_ADD_L2' LIKE 'Ave' OR ")
TA2_RoadExp = TA2_RoadExp[:-4]                                                                              # when the FOR loop has finished, truncate the last four digits of the string to remove the final " OR "
#print(TA2_RoadExp)                                                                                         # print that expression to terminal if desired
#TAX_ADD_3 Expression
for i in range(len(Road_Types)):                                                                            # set up a FOR loop to iterate over the Road_Types list
    TA3_RoadExp = TA3_RoadExp + str(field_list[6] + ' LIKE {} '.format(Road_Types[i]) + 'OR ')              # for every entry, add it to TA3_RoadExp so that each entry has the appropriate SQL format (e.g. "'TAX_ADD_L3' LIKE 'Ave' OR ")
TA3_RoadExp = TA3_RoadExp[:-4]                                                                              # when the FOR loop has finished, truncate the last four digits of the string to remove the final " OR "
#print(TA3_RoadExp)                                                                                         # print that expression to terminal if desired
#TAX_ADD_4 Expression
for i in range(len(Road_Types)):                                                                            # set up a FOR loop to iterate over the Road_Types list
    TA4_RoadExp = TA4_RoadExp + str(field_list[7] + ' LIKE {} '.format(Road_Types[i]) + 'OR ')              # for every entry, add it to TA4_RoadExp so that each entry has the appropriate SQL format (e.g. "'TAX_ADD_L4' LIKE 'Ave' OR ")
TA4_RoadExp = TA4_RoadExp[:-4]                                                                              # when the FOR loop has finished, truncate the last four digits of the string to remove the final " OR "
#print(TA4_RoadExp)                                                                                         # print that expression to terminal if desired


# Set up layers and define the counties to be investigated
arcpy.MakeFeatureLayer_management(Counties, 'Counties')                                                     # Make temporary feature layer for counties
arcpy.MakeFeatureLayer_management(Parcels, 'Parcels')                                                       # Make temporary feature layer for parcels
arcpy.MakeFeatureLayer_management(Metadata, 'Metadata')                                                     # Make temporary feature layer for metadata
arcpy.SelectLayerByLocation_management('Counties', "INTERSECT", WHP_DPAs, 0, "NEW_SELECTION")               # select features from the 'Counties' layer that intersect with WHP_DPAs
with arcpy.da.SearchCursor('Counties', ['CTY_NAME']) as cursor:                                             # set up a SearchCursor to iterate over the 'Counties' layer according to the field 'CTY_NAME'
    for row in cursor:                                                                                      # set up a FOR loop to investigate each row within the cursor
        print('{} County'.format(row[0]))                                                                   # print the county name for each entry found per row (which will be the first entry in the 'CTY_NAME' field)
        Selected_Counties = Selected_Counties + ['{}'.format(row[0])]                                       # append each row's county name to the Selected Counties list; this list will be unsorted
arcpy.SelectLayerByAttribute_management('Counties', "CLEAR_SELECTION")                                      # clear the selection of the 'Counties' layer
Selected_Counties_To_Go = copy.copy(Selected_Counties)                                                      # make a copy of the Selected_Counties list to be Selected_Counties_To_Go
Selected_Add_Counties_To_Go = copy.copy(Selected_Counties)                                                  # make a further copy of the Selected_Counties_To_Go
print('\nWHP parcel processing will require data from {} counties.'.format(len(Selected_Counties)))         # print out a statement to the terminal that indicates how many counties will need to be examined

# Set up lists
Ultimate_Checkup_Counties = []                                                                              # set up a list to hold a new list of counties that will require checkups
Owner_Address_Check = []                                                                                    # set up a list of counties that will require a check of 'OWNER' address information
Tax_Address_Check = []                                                                                      # set up a list of counties that will require a chekc of 'TAX' address information
Discrepancy_Check = []                                                                                      # set up a list of counties that have discrepancies that will need to be checked on
No_Data_Check = []                                                                                          # set up a list of counties that have no address data

# Begin the iteration over all required counties
print('\nConducting a full check on all fields for the flagged counties\n')                                 # print a message to the terminal that indicates the next step in the analaysis
with arcpy.da.SearchCursor('Counties', ['CTY_NAME']) as cursor:                                             # set up a new SearchCursor to iterate over the features in the layer 'Counties' according to the field 'CTY_NAME'
    for check in Selected_Counties:                                                                         # set up a FOR loop to iterate over the entries within the list Selected_Counties
        block_start = time.time()                                                                           # set the start time of the code block
        print('        Checking on {} County'.format(check))                                                # print a message indicating which county is being analyzed
        testing_list = [0, 0, 0]                                                                            # set up a new list with [0, 0, 0] as a baseline
        Expression = "CTY_NAME = '{}'".format(check)                                                        # set up a new Expression to include the county in question for this iteration
        arcpy.SelectLayerByAttribute_management('Counties', "NEW_SELECTION", Expression)                    # select the county polygon in question from the 'Counties' layer
        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        total_count = arcpy.GetCount_management('Parcels').getOutput(0)                                     # calculate the total_count as the sum of all parcels within the selection
        OWNER_NULL = "OWNER_NAME IS NULL"                                                                   # set up a new SQL expression to find all rows where the 'OWNER_NAME' field has a Null value
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OWNER_NULL)                  # subset the 'Parcels' selection to select all features where the 'OWNER_NAME' field is Null
        ONull_count = arcpy.GetCount_management('Parcels').getOutput(0)                                     # calculate the ONull_count which is the sum of all rows that have <Null> entries in the 'OWNER_NAME' field

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        OWNER_MORE_NULL = "OWNER_MORE IS NULL"                                                              # set up a new SQL expression to find all rows where the 'OWNER_MORE' field has a Null value
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OWNER_MORE_NULL)             # subset the 'Parcels' selection to select all features where the 'OWNER_MORE' field is Null
        OMoreNull_count = arcpy.GetCount_management('Parcels').getOutput(0)                                 # calculate the OMoreNull_count which is the sum of all rows that have <Null> entries in the 'OWNER_MORE' field

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        OWN_ADD1_NULL = "OWN_ADD_L1 IS NULL"                                                                # set up a new SQL expression to find all rows where the 'OWN_ADD_L1' field has a Null value
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OWN_ADD1_NULL)               # subset the 'Parcels' selection to select all features where the 'OWN_ADD_L1' field is Null
        OA1Null_count = arcpy.GetCount_management('Parcels').getOutput(0)                                   # calculate the OA1Null_count which is the sum of all rows that have <Null> entries in the 'OWN_ADD_L1' field

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        OWN_ADD2_NULL = "OWN_ADD_L2 IS NULL"                                                                # set up a new SQL expression to find all rows where the 'OWN_ADD_L2' field has a Null value
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OWN_ADD2_NULL)               # subset the 'Parcels' selection to select all features where the 'OWN_ADD_L2' field is Null
        OA2Null_count = arcpy.GetCount_management('Parcels').getOutput(0)                                   # calculate the OA2Null_count which is the sum of all rows that have <Null> entries in the 'OWN_ADD_L2' field
        #print('OA2Null_count: ', OA2Null_count)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        OWN_ADD3_NULL = "OWN_ADD_L3 IS NULL"                                                                # set up a new SQL expression to find all rows where the 'OWN_ADD_L3' field has a Null value
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OWN_ADD3_NULL)               # subset the 'Parcels' selection to select all features where the 'OWN_ADD_L3' field is Null
        OA3Null_count = arcpy.GetCount_management('Parcels').getOutput(0)                                   # calculate the OA3Null_count which is the sum of all rows that have <Null> entries in the 'OWN_ADD_L3' field
        #print('OA3Null_count: ', OA3Null_count)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        OWN_ADD4_NULL = "OWN_ADD_L4 IS NULL"                                                                # set up a new SQL expression to find all rows where the 'OWN_ADD_L4' field has a Null value
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OWN_ADD4_NULL)               # subset the 'Parcels' selection to select all features where the 'OWN_ADD_L4' field is Null
        OA4Null_count = arcpy.GetCount_management('Parcels').getOutput(0)                                   # calculate the OA4Null_count which is the sum of all rows that have <Null> entries in the 'OWN_ADD_L4' field
        #print('OA4Null_count: ', OA4Null_count)

        # Find out if the road types are present:
        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OA1_RoadExp)                 # subset the 'Parcels' selection to select all features where the 'OWN_ADD_L1' field has any of the Road Type entries
        OA1Road_count = arcpy.GetCount_management('Parcels').getOutput(0)                                   # calculate the OA1Road_count which is the sum of all rows that have any of the Road Type entries in the 'OWN_ADD_L1' field

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OA2_RoadExp)                 # subset the 'Parcels' selection to select all features where the 'OWN_ADD_L2' field has any of the Road Type entries
        OA2Road_count = arcpy.GetCount_management('Parcels').getOutput(0)                                   # calculate the OA2Road_count which is the sum of all rows that have any of the Road Type entries in the 'OWN_ADD_L2' field

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OA3_RoadExp)                 # subset the 'Parcels' selection to select all features where the 'OWN_ADD_L3' field has any of the Road Type entries
        OA3Road_count = arcpy.GetCount_management('Parcels').getOutput(0)                                   # calculate the OA3Road_count which is the sum of all rows that have any of the Road Type entries in the 'OWN_ADD_L3' field

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OA4_RoadExp)                 # subset the 'Parcels' selection to select all features where the 'OWN_ADD_L4' field has any of the Road Type entries
        OA4Road_count = arcpy.GetCount_management('Parcels').getOutput(0)                                   # calculate the OA4Road_count which is the sum of all rows that have any of the Road Type entries in the 'OWN_ADD_L4' field


        # Start calculations for road type counts/percentages in 'OWNER' fields
        try:                                                                                                    # set up a try/except function for calculating percentages; if the field is mostly full of null entries, this may cause the denominator in this expression to be 0
            OA1Road_Percent = round((float(int(OA1Road_count)/(int(total_count)-int(OA1Null_count))))*100, 2)   # calculate the percentage of all non-null entries in the 'OWN_ADD_L1' field that contain Road Type entries
        except ZeroDivisionError:                                                                               # except the ZeroDivisionError
            print('        Not enough parcel options for "'"OWNER_ADD_L1"'"')                                   # if the ZeroDivisionError is raised, print the statement
        try:                                                                                                    # set up a try/except function for calculating precentages; if the field is mostly full of null entries, this may cause the denominator in this expression to be 0
            OA2Road_Percent = round((float(int(OA2Road_count)/(int(total_count)-int(OA2Null_count))))*100, 2)   # calculate the percentage of all non-null entries in the 'OWN_ADD_L2' field that contain Road Type entries
        except ZeroDivisionError:                                                                               # added ZeroDivisionError?                  # except
            print('        Not enough parcel options for "'"OWNER_ADD_L2"'"')                                   # if the ZeroDivisionError is raised, print the statement
#        OA3Road_Percent = round((float(int(OA3Road_count)/(int(total_count)-int(OA3Null_count))))*100, 2)      # as of 22 November 2022, I have not set it up for 'OWN_ADD_L3'
        #OA4Road_Percent = round((float(int(OA4Road_count)/(int(total_count)-int(OA4Null_count))))*100, 2)      # as of 22 November 2022, I have not set it up for 'OWN_ADD_L4'
#        OARoad_Percent = round(float((int(OA1Road_count)+int(OA2Road_count)+int(OA3Road_count))/((3*int(total_count))-(int(OA1Null_count)+int(OA2Null_count)+int(OA3Null_count))))*100, 2)
        try:                                                                                                    # set up a try/except function for calculating precentages; if the field is mostly full of null entries, this may cause the denominator in this expression to be 0
            OARoad_Percent = round(float((int(OA1Road_count)+int(OA2Road_count))/((2*int(total_count))-(int(OA1Null_count)+int(OA2Null_count))))*100, 2)            # this calculation determines the percentage of road type entries in the cells of the 'OWN_ADD_L1' and 'OWN_ADD_L2' fields that do not contain Null values
        except:                                                                               # added ZeroDivisionError?                  # except
            OARoad_Percent = 0                                                                                  # if it can't complete the calculation, it'll prompt 0


        # Tax Null Analysis
        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        TAX_NULL = "TAX_NAME IS NULL"                                                                       # set up a new SQL expression to find all rows where the 'TAX_NAME' field has a Null value
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TAX_NULL)                    # subset the 'Parcels' selection to select all features where the 'TAX_NAME' field is Null
        TNull_count = arcpy.GetCount_management('Parcels').getOutput(0)                                     # calculate the TNull_count which is the sum of all rows that have <Null> entries in the 'TAX_NAME' field

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        TAX_ADD1_NULL = "TAX_ADD_L1 IS NULL"                                                                # set up a new SQL expression to find all rows where the 'TAX_ADD_L1' field has a Null value
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TAX_ADD1_NULL)               # subset the 'Parcels' selection to select all features where the 'TAX_ADD_L1' field is Null
        TA1Null_count = arcpy.GetCount_management('Parcels').getOutput(0)                                   # calculate the TNull_count which is the sum of all rows that have <Null> entries in the 'TAX_ADD_L1' field
        #print('TA1Null_count: ', TA1Null_count)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        TAX_ADD2_NULL = "TAX_ADD_L2 IS NULL"                                                                # set up a new SQL expression to find all rows where the 'TAX_ADD_L2' field has a Null value
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TAX_ADD2_NULL)               # subset the 'Parcels' selection to select all features where the 'TAX_ADD_L2' field is Null
        TA2Null_count = arcpy.GetCount_management('Parcels').getOutput(0)                                   # calculate the TNull_count which is the sum of all rows that have <Null> entries in the 'TAX_ADD_L2' field

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        TAX_ADD3_NULL = "TAX_ADD_L3 IS NULL"                                                                # set up a new SQL expression to find all rows where the 'TAX_ADD_L3' field has a Null value
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TAX_ADD3_NULL)               # subset the 'Parcels' selection to select all features where the 'TAX_ADD_L3' field is Null
        TA3Null_count = arcpy.GetCount_management('Parcels').getOutput(0)                                   # calculate the TNull_count which is the sum of all rows that have <Null> entries in the 'TAX_ADD_L3' field

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        TAX_ADD4_NULL = "TAX_ADD_L4 IS NULL"                                                                 # set up a new SQL expression to find all rows where the 'TAX_ADD_L4' field has a Null value
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TAX_ADD4_NULL)               # subset the 'Parcels' selection to select all features where the 'TAX_ADD_L4' field is Null
        TA4Null_count = arcpy.GetCount_management('Parcels').getOutput(0)                                   # calculate the TNull_count which is the sum of all rows that have <Null> entries in the 'TAX_ADD_L4' field


        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TA1_RoadExp)                 # subset the 'Parcels' selection to select all features where the 'TAX_ADD_L1' field has any of the Road Type entries
        TA1Road_count = arcpy.GetCount_management('Parcels').getOutput(0)                                   # calculate the TA1Road_count which is the sum of all rows that have any of the Road Type entries in the 'TAX_ADD_L1' field

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TA2_RoadExp)                 # subset the 'Parcels' selection to select all features where the 'TAX_ADD_L2' field has any of the Road Type entries
        TA2Road_count = arcpy.GetCount_management('Parcels').getOutput(0)                                   # calculate the TA2Road_count which is the sum of all rows that have any of the Road Type entries in the 'TAX_ADD_L2' field

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TA3_RoadExp)                 # subset the 'Parcels' selection to select all features where the 'TAX_ADD_L3' field has any of the Road Type entries
        TA3Road_count = arcpy.GetCount_management('Parcels').getOutput(0)                                   # calculate the TA3Road_count which is the sum of all rows that have any of the Road Type entries in the 'TAX_ADD_L3' field

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TA4_RoadExp)                 # subset the 'Parcels' selection to select all features where the 'TAX_ADD_L4' field has any of the Road Type entries
        TA4Road_count = arcpy.GetCount_management('Parcels').getOutput(0)                                   # calculate the TA4Road_count which is the sum of all rows that have any of the Road Type entries in the 'TAX_ADD_L4' field

        # Start calculations for road type counts/percentages in 'TAX' fields
        try:                                                                                                    # set up a try/except function for calculating percentages; if the field is mostly full of null entries, this may cause the denominator in this expression to be 0
            TA1Road_Percent = round((float(int(TA1Road_count)/(int(total_count)-int(TA1Null_count))))*100, 2)   # calculate the percentage of all non-null entries in the 'TAX_ADD_L1' field that contain Road Type entries
        except ZeroDivisionError:                                                                               # except the ZeroDivisionError
            print('        Not enough parcel options for "'"TAX_ADD_L1"'"')                                     # if the ZeroDivisionError is raised, print the statement
        try:                                                                                                    # set up a try/except function for calculating precentages; if the field is mostly full of null entries, this may cause the denominator in this expression to be 0
            TA2Road_Percent = round((float(int(TA2Road_count)/(int(total_count)-int(TA2Null_count))))*100, 2)   # calculate the percentage of all non-null entries in the 'TAX_ADD_L2' field that contain Road Type entries
        except ZeroDivisionError:                                                                               # except the ZeroDivisionError
            print('        Not enough parcel options for "'"TAX_ADD_L2"'"')                                     # if the ZeroDivisionError is raised, print the statement
        #TA3Road_Percent = round((float(int(TA3Road_count)/(int(total_count)-int(TA3Null_count))))*100, 2)      # as of 23 November 2022, I have not set it up for 'TAX_ADD_L3'
        #TA4Road_Percent = round((float(int(TA4Road_count)/(int(total_count)-int(TA4Null_count))))*100, 2)      # as of 23 November 2022, I have not set it up for 'TAX_ADD_L4'
#        TARoad_Percent = round(float((int(TA1Road_count)+int(TA2Road_count)+int(TA3Road_count))/((3*int(total_count))-(int(TA1Null_count)+int(TA2Null_count)+int(TA3Null_count))))*100, 2)
        try:
            TARoad_Percent = round(float((int(TA1Road_count)+int(TA2Road_count))/((2*int(total_count))-(int(TA1Null_count)+int(TA2Null_count))))*100, 2)        # this calculation determines the percentage of road type entries in the cells of the 'TAX_ADD_L1' and 'TAX_ADD_L2' fields that do not contain Null values
        except:                                                                                                 # except (add ZeroDivisionError?)
            TARoad_Percent = 0                                                                                  # if it can't complete the calculation, it'll prompt 0



        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        ALL_NULL = "OWNER_NAME IS NULL AND OWNER_MORE IS NULL AND OWN_ADD_L1 IS NULL AND OWN_ADD_L2 IS NULL AND OWN_ADD_L3 IS NULL AND OWN_ADD_L4 IS NULL AND TAX_NAME IS NULL AND TAX_ADD_L1 IS NULL AND TAX_ADD_L2 IS NULL AND TAX_ADD_L3 IS NULL AND TAX_ADD_L4 IS NULL"     # set up a new SQL expression to find all rows where all fields have a Null value
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", ALL_NULL)                    # subset the 'Parcels' selection to select all features where all fields have Null values
        AllNull_count = arcpy.GetCount_management('Parcels').getOutput(0)                                   # calculate the AllNull_count which is the sum of all rows that have <Null> entries in all fields

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # select all 'Parcels' polygons that intersect with the 'Counties' polygon
        ADDRESS_NULL = "OWN_ADD_L1 IS NULL AND OWN_ADD_L2 IS NULL AND OWN_ADD_L3 IS NULL AND OWN_ADD_L4 IS NULL AND TAX_ADD_L1 IS NULL AND TAX_ADD_L2 IS NULL AND TAX_ADD_L3 IS NULL AND TAX_ADD_L4 IS NULL"        # set up a new SQL expression to find all rows where all address information fields have a Null value
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", ADDRESS_NULL)                # subset the 'Parcels' selection to select all features where all address information fields have Null values
        AllAddressNull_count = arcpy.GetCount_management('Parcels').getOutput(0)                            # calculate the AllAddressNull_count which is the sum of all rows that have <Null> entries in all address information fields

        own_name_percent = round((float(int(ONull_count)/int(total_count))*100), 2)                         # calculate the percentage of Null entries in the 'OWNER_NAME' field
        own_more_percent = round((float(int(OMoreNull_count)/int(total_count))*100), 2)                     # calculate the percentage of Null entries in the 'OWNER_MORE' field
        own_add1_percent = round((float(int(OA1Null_count)/int(total_count))*100), 2)                       # calculate the percentage of Null entries in the 'OWN_ADD_L1' field
        own_add2_percent = round((float(int(OA2Null_count)/int(total_count))*100), 2)                       # calculate the percentage of Null entries in the 'OWN_ADD_L2' field
        own_add3_percent = round((float(int(OA3Null_count)/int(total_count))*100), 2)                       # calculate the percentage of Null entries in the 'OWN_ADD_L3' field
        own_add4_percent = round((float(int(OA4Null_count)/int(total_count))*100), 2)                       # calculate the percentage of Null entries in the 'OWN_ADD_L4' field
        own_add_full_percent = round((float((int(OA1Null_count) + int(OA2Null_count) + int(OA3Null_count) + int(OA4Null_count))/(int(total_count) * 4))*100), 2)    # calculate the percentage of Null entries (as a whole) within all 'OWN_ADD..' fields
        tax_name_percent = round((float(int(TNull_count)/int(total_count))*100), 2)                         # calculate the percentage of Null entries in the 'TAX_NAME' field
        tax_add1_percent = round((float(int(TA1Null_count)/int(total_count))*100), 2)                       # calculate the percentage of Null entries in the 'TAX_ADD_L1' field
        tax_add2_percent = round((float(int(TA2Null_count)/int(total_count))*100), 2)                       # calculate the percentage of Null entries in the 'TAX_ADD_L2' field
        tax_add3_percent = round((float(int(TA3Null_count)/int(total_count))*100), 2)                       # calculate the percentage of Null entries in the 'TAX_ADD_L3' field
        tax_add4_percent = round((float(int(TA4Null_count)/int(total_count))*100), 2)                       # calculate the percentage of Null entries in the 'TAX_ADD_L4' field
        tax_add_full_percent = round((float((int(TA1Null_count) + int(TA2Null_count) + int(TA3Null_count) + int(TA4Null_count))/(int(total_count) * 4))*100), 2)    # calculate the percentage of Null entries (as a whole) within all 'TAX_ADD..' fields
        all_percent = round((float(int(AllNull_count)/int(total_count))*100), 2)                            # calculate the percentage of all Null entries in all fields
        all_address_percent = round((float(int(AllAddressNull_count)/int(total_count))*100), 2)             # calculate the percentage of all Null entries in all address information fields
        Selected_Counties_To_Go.remove(check)                                                               # remove the current county being evaluated from the Selected_Counties_To_Go list

        # Set up an extensive print statement to display various data analyses
        #   This section print text in a large block (indented at the start for the terminal display) and substitutes the
        #   various variables into the text string that are listed after the text block with the .format() function.
        print('''        {} County has {} total parcels.
        The 'OWNER_NAME' field has {} Null values ({}%),
        the 'OWNER_MORE' field has {} Null values ({}%),
        the 'OWN_ADD_L1' field has {} Null values ({}%),
        the 'OWN_ADD_L2' field has {} Null values ({}%),
        the 'OWN_ADD_L3' field has {} Null values ({}%),
        the 'OWN_ADD_L4' field has {} Null values ({}%),
        the 'TAX_NAME' field has {} Null values ({}%),
        the 'TAX_ADD_L1' field has {} Null values ({}%),
        the 'TAX_ADD_L2' field has {} Null values ({}%),
        the 'TAX_ADD_L3' field has {} Null values ({}%),
        the 'TAX_ADD_L4' field has {} Null values ({}%),
        {} parcels in the county ({}%) have no information ("Null" entries in all fields),
        and {} parcels in the county ({}%) have no address information ("Null" entries in all address fields).'''.format(check, total_count,
        ONull_count, own_name_percent, OMoreNull_count, own_more_percent, OA1Null_count, own_add1_percent, OA2Null_count, own_add2_percent,
        OA3Null_count, own_add3_percent, OA4Null_count, own_add4_percent, TNull_count, tax_name_percent, TA1Null_count, tax_add1_percent,
        TA2Null_count, tax_add2_percent, TA3Null_count, tax_add3_percent, TA4Null_count, tax_add4_percent, AllNull_count, all_percent,
        AllAddressNull_count, all_address_percent))


        # Calculating county parcel status
        #
        # At the start of the code block, the variable testing_list was given the values [0,0,0].
        #    This list will eventually indicate whether the data (or lack thereof) indicate that
        #    further investigation is necessary according to a series of data evaluations.

        #    The first evaluation examines the 'OWNER' address fields.
        #       The logic here is based upon my own experiences working with the parcel dataset.
        #       The IF statement evaluates whether any combination of 3 of the 'OWNER' address fields
        #       are more than 60% empty or have null values, apiece. If any combination of 3 'OWNER' fields have greater than
        #       60% of the entries as null, the first value in the testing_list variable is changed to a 1 from a 0.
        #       This incidates that the majority of the 'OWNER' address cells are empty, and that is brought forward in
        #       the testing_list variable.

        print('        Owner address fields are {}% empty.'.format(own_add_full_percent))
        if (own_add1_percent>60 and own_add2_percent>60 and own_add3_percent>60) or (own_add1_percent>60 and own_add2_percent>60 and own_add4_percent>60) or (own_add1_percent>60 and own_add3_percent>60 and own_add4_percent>60) or (own_add2_percent>60 and own_add3_percent>60 and own_add4_percent>60):
            testing_list[0] = 1
#            print('        Confirm that all OWN_ADD_L# fields have data.'.format(check))

        #       Following the logic from the previous IF statement, this IF statement evaluates the 'TAX' address fields.
        #       The IF statement evaluates whether any combination of 3 of the 'TAX' address fields
        #       are more than 60% empty or have null values, apiece. If any combination of 3 'TAX' fields have greater than
        #       60% of the entries as null, the second value in the testing_list variable is changed to a 1 from a 0.
        #       This indicates that the majority of the 'TAX' address cells are empty, and that is brought forward in the
        #       testing_list variable.
        print('        Tax address fields are {}% empty.'.format(tax_add_full_percent))
        if (tax_add1_percent>60 and tax_add2_percent>60 and tax_add3_percent>60) or (tax_add1_percent>60 and tax_add2_percent>60 and tax_add4_percent>60) or (tax_add1_percent>60 and tax_add3_percent>60 and tax_add4_percent>60) or (tax_add2_percent>60 and tax_add3_percent>60 and tax_add4_percent>60):
            testing_list[1] = 1
#            print('        Confirm that all TAX_ADD_L# fields have data.'.format(check))

        #       In this next section, the script evaluates the total number of cells that contain null values.
        #       If the total number of rows that contain all null values is greater than 30 percent of the total number of rows, the
        #       IF statement evaluates to TRUE and the third value of the testing_list variable is changed to a 1 from a 0. Additionally,
        #       a TRUE result prompts the county to be added to the Ultimate_Checkup_Counties list variable.
        if all_address_percent > 30:
            testing_list[2] = 1
            Ultimate_Checkup_Counties = Ultimate_Checkup_Counties + ['{}'.format(check)]
#            print('        {} County will need a checkup.\n'.format(check))
#        print('Testing List: ', testing_list)

        # Evaluating the results
        #       To follow up with the testing_list changes (or lack thereof), the next section of code
        #       evaluates the status of the county's parcels with respect to the null values within those parcels.

        #       When testing_list holds the values [0,1,1], this indicates that the 'OWNER' fields passed the check,
        #       but the majority of 'TAX' values were null and the number of fully-null rows was considerable.
        #       In this case, the 'TAX' parcels will likely need to be investigated:
        if testing_list[0] == 0 and testing_list[1] == 1 and testing_list[2] == 1:
            Tax_Address_Check = Tax_Address_Check + ['{}'.format(check)]
            print('        {} County will need a checkup; check Tax address fields.'.format(check))

        #       When testing_list holds the values [1,0,1], this indicates that the 'TAX' fields passed the check,
        #       but the majority of 'OWNER' values were null and the number of fully-null rows was considerable.
        #       In this case, the 'OWNER' parcels will likely need to be investigated:
        elif testing_list[0] == 1 and testing_list[1] == 0 and testing_list[2] == 1:
            Owner_Address_Check = Owner_Address_Check + ['{}'.format(check)]
            print('        {} County will need a checkup; check Owner address fields.'.format(check))

        #       When testing_list holds the values [1,1,0], this indicates that neither the 'OWNER' nor the 'TAX' fields passed the check,
        #       but a large portion of the rows were not completely null. In this case, it's likely that a scattering of entries in 'OWNER'
        #       and 'TAX' fields will not be sufficient for future utilization and will need to be checked on:
        elif testing_list[0] == 1 and testing_list[1] == 1 and testing_list[2] == 0:
            Discrepancy_Check = Discrepancy_Check + ['{}'.format(check)]
            print('        {} County has discrepancies and will need to be checked on.'.format(check))


        #
        elif OARoad_Percent < 20 and round(float(((int(total_count)-int(OA1Null_count))+(int(total_count)-int(OA2Null_count)))/(2*int(total_count)))*100, 2) > 10:
            Discrepancy_Check = Discrepancy_Check + ['{}'.format(check)]
            print('        {} County has road type discrepancies in OWNER fields and will need to be checked on.'.format(check))
        elif TARoad_Percent < 20 and round(float(((int(total_count)-int(TA1Null_count))+(int(total_count)-int(TA2Null_count)))/(2*int(total_count)))*100, 2) > 10:
            Discrepancy_Check = Discrepancy_Check + ['{}'.format(check)]
            print('        {} County has road type discrepancies in TAX fields and will need to be checked on.'.format(check))



        #       When testing_list holds the values [1,1,1], this indicates that 'OWNER' and 'TAX' fields failed the check and a considerable
        #       number of rows are also fully null. In this case, it's likely that this county's parcels are completely empty and further
        #       investigation will be required:
        elif testing_list[0] == 1 and testing_list[1] == 1 and testing_list[2] == 1:
            No_Data_Check = No_Data_Check + ['{}'.format(check)]
            print('        {} County has no data and will need to be checked on.'.format(check))

        #       When testing_list holds the values [1,0,0], this indicates that 'OWNER' fields failed the check but 'TAX' fields were
        #       satisfactory and there were not a considerable number of fully-null rows. In this case, it's likely that the 'TAX' fields
        #       will hold a sufficient amount of data and further utilization is possible. This expression further confirms that the percentage of
        #       cells in the 'TAX_ADD_L1' and 'TAX_ADD_L2' fields which do not contain Null values and do contain road type designations
        #       is greater than a very minimal amount (20%):
        elif testing_list[0] == 1 and testing_list[1] == 0 and testing_list[2] == 0 and TARoad_Percent > 20:
            print('        {} County is cleared.'.format(check))

        #       When testing_list holds the values [0,1,0], this indicates that 'TAX' fields failed the check but 'OWNER' fields were
        #       satisfactory and there were not a considerable number of fully-null rows. In this case, it's likely that the 'OWNER' fields
        #       will hold a sufficient amount of data and further utilization is possible. This expression further confirms that the percentage of
        #       cells in the 'OWN_ADD_L1' and 'OWN_ADD_L2' fields which do not contain Null values and do contain road type designations
        #       is greater than a very minimal amount (20%):
        elif testing_list[0] == 0 and testing_list[1] == 1 and testing_list[2] == 0 and OARoad_Percent > 20:
            print('        {} County is cleared.'.format(check))

        #       When testing_list holds the values [0,0,0], this indicates that 'OWNER' and 'TAX' fields passed the check and there were
        #       not a considerable number of empty rows. In this case, it is highly likely that sufficient data are available for future utilization.
        #       The expression further confirms that the percentage of cells in the 'OWN_ADD_L1' and 'OWN_ADD_L2' or 'TAX_ADD_L1' and 'TAX_ADD_L2' fields
        #       which do not contain Null values and do contain road type designations is greater than a very minimal amount for each grouping (20%):
        elif testing_list[0] == 0 and testing_list[1] == 0 and testing_list[2] == 0 and (OARoad_Percent > 20 or TARoad_Percent > 20):
            print('        {} County is cleared.'.format(check))
#        if (testing_list[0] == 1 and testing_list[1] == 0) or (testing_list[0] == 0 and testing_list[1] == 1)
#       new
        print('        This county took %s seconds to process.' % round(time.time() - block_start))  # print an expression that indicates how long it took the county in question to process
        print('        {} counties to go.'.format(len(Selected_Counties_To_Go)))                # print a len() of the number of counties still to go (recall that the current county's name was removed from this list)
        print('')




#________________________________________________________________________


# Script Summary


#   This block of code presents a list of counties in the terminal that held more than 30% of rows with fully-null values:
print('\nThese counties may be devoid of data and will require an additional check:\n')
for spot in Ultimate_Checkup_Counties:
    print(spot)

#   This block of code presents a list of counties in the terminal that held majority-null values in 'TAX' values with concerns about large numbers of empty rows:
print('\nThese counties prioritize Tax address information that will need to be checked on:\n')
for spot in Tax_Address_Check:
    print(spot)

#   This block of code presents a list of counties in the terminal that held majority-null values in 'OWNER' values with concerns about large numbers of empty rows:
print('\nThese counties prioritize Owner address information that will need to be checked on:\n')
for spot in Owner_Address_Check:
    print(spot)

#   This block of code presents a list of counties that were flagged by the script but without clear-cut issues:
print('\nThese counties have issues with data and they should be checked on:\n')
for spot in Discrepancy_Check:
    print(spot)

#   This block of code presents a list of counties that failed the 'OWNER' and 'TAX' field checks with concerns about large numbers of empty rows:
print('\nThese counties have no data and you will need to reach out to the counties directly:\n')
for spot in No_Data_Check:
    print(spot)

#   In case the counties weren't added to the Ultimate_Checkup_Counties list previously, this next expression combines the lists and eliminates duplicates:
Ultimate_Checkup_Counties = Ultimate_Checkup_Counties + Discrepancy_Check + No_Data_Check
Ultimate_Checkup_Counties = list(set(Ultimate_Checkup_Counties))



# Iterate over the "ultimate" entries and find the dates when data was last sumitted and the script was last run:

print('\nChecking on the last date of data updates and script concatenation:\n')            # Print a statement in the terminal declaring that the next step is progressing:

today = date.today()                                                                        # define a datetime.date class for the script's run date
today_year = today.year                                                                     # define an integer value of the year of the script's run date
today_month = today.month                                                                   # define an integer value of the month of the script's run date
today_day = today.day                                                                       # define an integer value of the day of the script's run date


for county in Ultimate_Checkup_Counties:                                                                # set up a FOR loop
    Expression = "COUNTYNAME = '{}'".format(county)                                                     # define an iterable expression
    with arcpy.da.SearchCursor('Metadata', ['COUNTYNAME', 'RunDate', 'AcqDate'], Expression) as cursor: # set up a SearchCursor that will iterate over the 'Metadata' layer according to the 'COUNTYNAME', 'RunDate', and 'AcqDate' fields
        for row in cursor:                                                                              # set up a FOR loop to investigate each row within the cursor
            sdate = row[1]                                                                              # define the variable for the date that the consolidation script was run
            ddate = row[2]                                                                              # define the variable for the date that the county last received data
            sdate_trunc = sdate.strftime("%d %B %Y")                                                    # define the format of the sdate variable
            ddate_trunc = ddate.strftime("%d %B %Y")                                                    # define the format of the ddate variable
            ddate_year = ddate.year                                                                     # define the year of the ddate variable
            ddate_month = ddate.month                                                                   # define the month of the ddate variable
            ddate_day = ddate.day                                                                       # define the day of the ddate variable
            d0 =date(ddate_year, ddate_month, ddate_day)                                                # define the variable that holds the date that the county last received data
            d1 = date(today_year, today_month, today_day)                                               # define the variable that holds the script run date
            delta = d1 - d0                                                                             # define the variable with the difference between the script run date and the date that the county last received data
            days_int = delta.days                                                                       # define the integer value of the difference
            print('{} County was last scripted on {}; data was last acquired on {}. Data are {} days old.'.format(county, sdate_trunc, ddate_trunc, days_int))  # set up a print statement to display the various variables within the text string that are listed with the .format() function.



# Display time taken just for fun:
print('This script took %s seconds...' % round(time.time() - start_time))
# originally at 462 lines at the start of 27 November 2022