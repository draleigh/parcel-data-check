#-------------------------------------------------------------------------------
# Name:        Parcel Status Analysis (with Road Type Checkups)
# Purpose:      For checking on the status of parcels within specific counties
#                   to determine whether extra effort is required to find 
#                   full parcel datasets from specific counties (including 
#                   checking on null entries and presence of road type descriptors).
# Author:      draleig
#
# Created:     25 October 2022
# Copyright:   (c) daraleig 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------




#import sys,string,os,arcpy,time,datetime,zipfile,tarfile,shutil,gzip,urllib,ftplib         # Full list just in case
import sys,string,os,arcpy,time,datetime,shutil,copy
from datetime import date, timedelta
from shutil import copyfile
from ftplib import FTP
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

# Define Data Locations and Other Variables
Parcels = *path to parcel shapefile*
Counties = *path to county shapefile*
# This may need to be adjusted once the final DPA numbers are confirmed/updated (or from year to year):
Selector = *path to "Selector" shapefile*
Metadata = *path to "Selector" shapefile*

Selected_Counties = []                  # define a temporary list for counties that will be analyzed
Selected_Counties_To_Go = []            # define a temporary list to track the number of counties still to be analyzed
start_time = time.time()

# Set up expressions to be used for road type checkups
field_list = ['OWN_ADD_L1', 'OWN_ADD_L2', 'OWN_ADD_L3', 'OWN_ADD_L4', 'TAX_ADD_L1', 'TAX_ADD_L2', 'TAX_ADD_L3', 'TAX_ADD_L4']
Road_Type = ['Ave', 'Avenue', 'Blvd', 'Boulevard', 'Cir', 'Circle', 'Court', 'Ct', 'Dr', 'Drive', 'Highway', 'Hwy', 'Lane', 'Ln', 'Parkway', 'Path', 'Pkwy', 'Pl', 'Place', 'Rd', 'Road', 'Street', 'St', 'Trail', 'Trl', 'Way']
Road_Types = []
#Road_Types = ["' Ave'", "' Avenue'", "' Blvd'", "' Boulevard'", "' Court'", "' Ct'", "' Dr'", "' Drive'", "' Highway'", "' Hwy'", "' Lane'", "' Ln'", "' Parkway'", "' Path'", "' Pkwy'", "' Rd'", "' Road'", "' Street'", "' St'", "' Trail'", "' Trl'", "' Way'"]
OA1_RoadExp = ''
OA2_RoadExp = ''
OA3_RoadExp = ''
OA4_RoadExp = ''
TA1_RoadExp = ''
TA2_RoadExp = ''
TA3_RoadExp = ''
TA4_RoadExp = ''

# Set up 'Road_Types' list (which could be adjusted based on changes to the 'Road_Type' list before it):
for j in range(len(Road_Type)):
    Road_Types = Road_Types + ["'% "+Road_Type[j]+"%'"]

#OWNER_ADD_1 Expression
for i in range(len(Road_Types)):
    OA1_RoadExp = OA1_RoadExp + str(field_list[0] + ' LIKE {} '.format(Road_Types[i]) + 'OR ')
OA1_RoadExp = OA1_RoadExp[:-4]
#print(OA1_RoadExp)
#OWNER_ADD_2 Expression
for i in range(len(Road_Types)):
    OA2_RoadExp = OA2_RoadExp + str(field_list[1] + ' LIKE {} '.format(Road_Types[i]) + 'OR ')
OA2_RoadExp = OA2_RoadExp[:-4]
#print(OA2_RoadExp)
#OWNER_ADD_3 Expression
for i in range(len(Road_Types)):
    OA3_RoadExp = OA3_RoadExp + str(field_list[2] + ' LIKE {} '.format(Road_Types[i]) + 'OR ')
OA3_RoadExp = OA3_RoadExp[:-4]
#print(OA3_RoadExp)
#OWNER_ADD_4 Expression
for i in range(len(Road_Types)):
    OA4_RoadExp = OA4_RoadExp + str(field_list[3] + ' LIKE {} '.format(Road_Types[i]) + 'OR ')
OA4_RoadExp = OA4_RoadExp[:-4]

#TAX_ADD_1 Expression
for i in range(len(Road_Types)):
    TA1_RoadExp = TA1_RoadExp + str(field_list[4] + ' LIKE {} '.format(Road_Types[i]) + 'OR ')
TA1_RoadExp = TA1_RoadExp[:-4]
#print(TA1_RoadExp)
#TAX_ADD_2 Expression
for i in range(len(Road_Types)):
    TA2_RoadExp = TA2_RoadExp + str(field_list[5] + ' LIKE {} '.format(Road_Types[i]) + 'OR ')
TA2_RoadExp = TA2_RoadExp[:-4]

#TAX_ADD_3 Expression
for i in range(len(Road_Types)):
    TA3_RoadExp = TA3_RoadExp + str(field_list[6] + ' LIKE {} '.format(Road_Types[i]) + 'OR ')
TA3_RoadExp = TA3_RoadExp[:-4]

#TAX_ADD_4 Expression
for i in range(len(Road_Types)):
    TA4_RoadExp = TA4_RoadExp + str(field_list[7] + ' LIKE {} '.format(Road_Types[i]) + 'OR ')
TA4_RoadExp = TA4_RoadExp[:-4]



arcpy.MakeFeatureLayer_management(Counties, 'Counties')                                     # Make temporary feature layer for counties
arcpy.MakeFeatureLayer_management(Parcels, 'Parcels')                                       # Make temporary feature layer for parcels
arcpy.MakeFeatureLayer_management(Metadata, 'Metadata')                                     # Make temporary feature layer for metadata
arcpy.SelectLayerByLocation_management('Counties', "INTERSECT", WHP_DPAs, 0, "NEW_SELECTION")
with arcpy.da.SearchCursor('Counties', ['CTY_NAME']) as cursor:
    for row in cursor:
        print('{} County'.format(row[0]))
        Selected_Counties = Selected_Counties + ['{}'.format(row[0])]           # maybe sort them first, or is that necessary?
arcpy.SelectLayerByAttribute_management('Counties', "CLEAR_SELECTION")
Selected_Counties_To_Go = copy.copy(Selected_Counties)
print('\nWHP parcel processing will require data from {} counties.'.format(len(Selected_Counties)))


Ultimate_Checkup_Counties = []
Owner_Address_Check = []
Tax_Address_Check = []
Discrepancy_Check = []
No_Data_Check = []

print('\nConducting a full check on all fields for the flagged counties\n')
with arcpy.da.SearchCursor('Counties', ['CTY_NAME']) as cursor:
# Final_Checkup was changed to Selected_Counties
    for check in Selected_Counties:
        print('        Checking on {} County'.format(check))
        testing_list = [0, 0, 0]
        Expression = "CTY_NAME = '{}'".format(check)
        arcpy.SelectLayerByAttribute_management('Counties', "NEW_SELECTION", Expression)
        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # Begin selecting all parcels within the county
        total_count = arcpy.GetCount_management('Parcels').getOutput(0)                                     # total_count is sum of all parcels
        OWNER_NULL = "OWNER_NAME IS NULL"                                                                   # Begin selecting all Null 'OWNER_NAME' entries
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OWNER_NULL)
        ONull_count = arcpy.GetCount_management('Parcels').getOutput(0)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        OWNER_MORE_NULL = "OWNER_MORE IS NULL"
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OWNER_MORE_NULL)
        OMoreNull_count = arcpy.GetCount_management('Parcels').getOutput(0)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        OWN_ADD1_NULL = "OWN_ADD_L1 IS NULL"
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OWN_ADD1_NULL)
        OA1Null_count = arcpy.GetCount_management('Parcels').getOutput(0)
        #print('OA1Null_count: ', OA1Null_count)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        OWN_ADD2_NULL = "OWN_ADD_L2 IS NULL"
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OWN_ADD2_NULL)
        OA2Null_count = arcpy.GetCount_management('Parcels').getOutput(0)
        #print('OA2Null_count: ', OA2Null_count)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        OWN_ADD3_NULL = "OWN_ADD_L3 IS NULL"
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OWN_ADD3_NULL)
        OA3Null_count = arcpy.GetCount_management('Parcels').getOutput(0)
        #print('OA3Null_count: ', OA3Null_count)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        OWN_ADD4_NULL = "OWN_ADD_L4 IS NULL"
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OWN_ADD4_NULL)
        OA4Null_count = arcpy.GetCount_management('Parcels').getOutput(0)
        #print('OA4Null_count: ', OA4Null_count)

        # Find out if the road types are present:
        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OA1_RoadExp)
        OA1Road_count = arcpy.GetCount_management('Parcels').getOutput(0)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OA2_RoadExp)
        OA2Road_count = arcpy.GetCount_management('Parcels').getOutput(0)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OA3_RoadExp)
        OA3Road_count = arcpy.GetCount_management('Parcels').getOutput(0)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OA4_RoadExp)
        OA4Road_count = arcpy.GetCount_management('Parcels').getOutput(0)

        # Start calculations for road type counts/percentages in 'OWNER' fields
        try:
            OA1Road_Percent = round((float(int(OA1Road_count)/(int(total_count)-int(OA1Null_count))))*100, 2)
        except ZeroDivisionError:
            print('Not enough parcel options for "'"OWNER_ADD_L1"'"')
        try:
            OA2Road_Percent = round((float(int(OA2Road_count)/(int(total_count)-int(OA2Null_count))))*100, 2)
        except:
            print('Not enough parcel options for "'"OWNER_ADD_L2"'"')
#        OA3Road_Percent = round((float(int(OA3Road_count)/(int(total_count)-int(OA3Null_count))))*100, 2)
        #OA4Road_Percent = round((float(int(OA4Road_count)/(int(total_count)-int(OA4Null_count))))*100, 2)
#        OARoad_Percent = round(float((int(OA1Road_count)+int(OA2Road_count)+int(OA3Road_count))/((3*int(total_count))-(int(OA1Null_count)+int(OA2Null_count)+int(OA3Null_count))))*100, 2)
        try:
            OARoad_Percent = round(float((int(OA1Road_count)+int(OA2Road_count))/((2*int(total_count))-(int(OA1Null_count)+int(OA2Null_count))))*100, 2)
        except:
            OARoad_Percent = 0
        #print('OARoad_Percent: ', OARoad_Percent)
        #print('OA1Road_count: ', OA1Road_count)
        #print('OA2Road_count: ', OA2Road_count)
        #print('OA3Road_count: ', OA3Road_count)
        #print('OA4Road_count: ', OA4Road_count)

        #print('OA1_Percent: ', OA1Road_Percent)
        #print('OA2_Percent: ', OA2Road_Percent)
        #print('OA3_Percent: ', OA3Road_Percent)
        #print('OA4_Percent: ', OA4Road_Percent)
        #print('OARoad_Percent: ', OARoad_Percent)




        # Tax Null Analysis
        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        TAX_NULL = "TAX_NAME IS NULL"
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TAX_NULL)
        TNull_count = arcpy.GetCount_management('Parcels').getOutput(0)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        TAX_ADD1_NULL = "TAX_ADD_L1 IS NULL"
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TAX_ADD1_NULL)
        TA1Null_count = arcpy.GetCount_management('Parcels').getOutput(0)
        #print('TA1Null_count: ', TA1Null_count)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        TAX_ADD2_NULL = "TAX_ADD_L2 IS NULL"
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TAX_ADD2_NULL)
        TA2Null_count = arcpy.GetCount_management('Parcels').getOutput(0)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        TAX_ADD3_NULL = "TAX_ADD_L3 IS NULL"
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TAX_ADD3_NULL)
        TA3Null_count = arcpy.GetCount_management('Parcels').getOutput(0)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        TAX_ADD4_NULL = "TAX_NAME IS NULL"
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TAX_ADD4_NULL)
        TA4Null_count = arcpy.GetCount_management('Parcels').getOutput(0)


        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TA1_RoadExp)
        TA1Road_count = arcpy.GetCount_management('Parcels').getOutput(0)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TA2_RoadExp)
        TA2Road_count = arcpy.GetCount_management('Parcels').getOutput(0)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TA3_RoadExp)
        TA3Road_count = arcpy.GetCount_management('Parcels').getOutput(0)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TA4_RoadExp)
        TA4Road_count = arcpy.GetCount_management('Parcels').getOutput(0)

        # Start calculations for road type counts/percentages in 'TAX' fields
        try:
            TA1Road_Percent = round((float(int(TA1Road_count)/(int(total_count)-int(TA1Null_count))))*100, 2)
        except ZeroDivisionError:
            print('Not enough parcel options for "'"TAX_ADD_L1"'"')
        try:
            TA2Road_Percent = round((float(int(TA2Road_count)/(int(total_count)-int(TA2Null_count))))*100, 2)
        except ZeroDivisionError:
            print('Not enough parcel options for "'"TAX_ADD_L2"'"')
        #TA3Road_Percent = round((float(int(TA3Road_count)/(int(total_count)-int(TA3Null_count))))*100, 2)
        #TA4Road_Percent = round((float(int(TA4Road_count)/(int(total_count)-int(TA4Null_count))))*100, 2)
#        TARoad_Percent = round(float((int(TA1Road_count)+int(TA2Road_count)+int(TA3Road_count))/((3*int(total_count))-(int(TA1Null_count)+int(TA2Null_count)+int(TA3Null_count))))*100, 2)
        try:
            TARoad_Percent = round(float((int(TA1Road_count)+int(TA2Road_count))/((2*int(total_count))-(int(TA1Null_count)+int(TA2Null_count))))*100, 2)
        except:
            TARoad_Percent = 0
        #print('TARoad_Percent: ', TARoad_Percent)
        #print('TA1Road_count: ', TA1Road_count)
        #print('TA2Road_count: ', TA2Road_count)
        #print('TA3Road_count: ', TA3Road_count)
        #print('TA4Road_count: ', TA4Road_count)

        #print('TA1_Percent: ', TA1Road_Percent)
        #print('TA2 Percent: ', TA2Road_Percent)
        #print('TA3 Percent: ', TA3Road_Percent)
        #print('TA4 Percent: ', TA4Road_Percent)
        #print('TARoad_Percent: ', TARoad_Percent)






        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # Begin selecting all Null 'OWN' and 'TAX' entries
        ALL_NULL = "OWNER_NAME IS NULL AND OWNER_MORE IS NULL AND OWN_ADD_L1 IS NULL AND OWN_ADD_L2 IS NULL AND OWN_ADD_L3 IS NULL AND OWN_ADD_L4 IS NULL AND TAX_NAME IS NULL AND TAX_ADD_L1 IS NULL AND TAX_ADD_L2 IS NULL AND TAX_ADD_L3 IS NULL AND TAX_ADD_L4 IS NULL"
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", ALL_NULL)
        AllNull_count = arcpy.GetCount_management('Parcels').getOutput(0)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # Begin selecting all Null 'OWN' and 'TAX' entries
        ADDRESS_NULL = "OWN_ADD_L1 IS NULL AND OWN_ADD_L2 IS NULL AND OWN_ADD_L3 IS NULL AND OWN_ADD_L4 IS NULL AND TAX_ADD_L1 IS NULL AND TAX_ADD_L2 IS NULL AND TAX_ADD_L3 IS NULL AND TAX_ADD_L4 IS NULL"
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", ADDRESS_NULL)
        AllAddressNull_count = arcpy.GetCount_management('Parcels').getOutput(0)

        own_name_percent = round((float(int(ONull_count)/int(total_count))*100), 2)
        own_more_percent = round((float(int(OMoreNull_count)/int(total_count))*100), 2)
        own_add1_percent = round((float(int(OA1Null_count)/int(total_count))*100), 2)
        own_add2_percent = round((float(int(OA2Null_count)/int(total_count))*100), 2)
        own_add3_percent = round((float(int(OA3Null_count)/int(total_count))*100), 2)
        own_add4_percent = round((float(int(OA4Null_count)/int(total_count))*100), 2)
        own_add_full_percent = round((float((int(OA1Null_count) + int(OA2Null_count) + int(OA3Null_count) + int(OA4Null_count))/(int(total_count) * 4))*100), 2)
        tax_name_percent = round((float(int(TNull_count)/int(total_count))*100), 2)
        tax_add1_percent = round((float(int(TA1Null_count)/int(total_count))*100), 2)
        tax_add2_percent = round((float(int(TA2Null_count)/int(total_count))*100), 2)
        tax_add3_percent = round((float(int(TA3Null_count)/int(total_count))*100), 2)
        tax_add4_percent = round((float(int(TA4Null_count)/int(total_count))*100), 2)
        tax_add_full_percent = round((float((int(TA1Null_count) + int(TA2Null_count) + int(TA3Null_count) + int(TA4Null_count))/(int(total_count) * 4))*100), 2)
        all_percent = round((float(int(AllNull_count)/int(total_count))*100), 2)
        all_address_percent = round((float(int(AllAddressNull_count)/int(total_count))*100), 2)
#        average_address_data = round((float((int(OA1Null_count)+int(OA2Null_count)+int(OA3Null_count)+int(OA4Null_count)+int(TA1Null_count)+int(TA2Null_count)+int(TA3Null_count)+int(TA4Null_count))/(int(newtotal)*8))*100), 2)
#        print('all_address_percent (allAND): {}, average_address_data (sum/total_count): {}'.format(all_address_percent, average_address_data))
# changed Final_Checkup_To_Go to Selected_Counties_To_Go
        Selected_Counties_To_Go.remove(check)
#        print('Counties still to check for name presence: {}'.format(len(Selected_Counties_To_Go)))
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
# add something about how many cells in total are empty? maybe conduct the calculation from there?

        print('        Owner address fields are {}% empty.'.format(own_add_full_percent))
        if (own_add1_percent>60 and own_add2_percent>60 and own_add3_percent>60) or (own_add1_percent>60 and own_add2_percent>60 and own_add4_percent>60) or (own_add1_percent>60 and own_add3_percent>60 and own_add4_percent>60) or (own_add2_percent>60 and own_add3_percent>60 and own_add4_percent>60):
            testing_list[0] = 1
#            print('        Confirm that all OWN_ADD_L# fields have data.'.format(check))
        print('        Tax address fields are {}% empty.'.format(tax_add_full_percent))
        if (tax_add1_percent>60 and tax_add2_percent>60 and tax_add3_percent>60) or (tax_add1_percent>60 and tax_add2_percent>60 and tax_add4_percent>60) or (tax_add1_percent>60 and tax_add3_percent>60 and tax_add4_percent>60) or (tax_add2_percent>60 and tax_add3_percent>60 and tax_add4_percent>60):
            testing_list[1] = 1
#            print('        Confirm that all TAX_ADD_L# fields have data.'.format(check))
        if all_address_percent > 30:
            testing_list[2] = 1
            Ultimate_Checkup_Counties = Ultimate_Checkup_Counties + ['{}'.format(check)]
#            print('        {} County will need a checkup.\n'.format(check))
#        print('Testing List: ', testing_list)
        if testing_list[0] == 0 and testing_list[1] == 1 and testing_list[2] == 1:
            Tax_Address_Check = Tax_Address_Check + ['{}'.format(check)]
            print('        {} County will need a checkup; check Tax address fields.'.format(check))
        elif testing_list[0] == 1 and testing_list[1] == 0 and testing_list[2] == 1:
            Owner_Address_Check = Owner_Address_Check + ['{}'.format(check)]
            print('        {} County will need a checkup; check Owner address fields.'.format(check))
        elif testing_list[0] == 1 and testing_list[1] == 1 and testing_list[2] == 0:
            Discrepancy_Check = Discrepancy_Check + ['{}'.format(check)]
            print('        {} County has discrepancies and will need to be checked on.'.format(check))
        elif OARoad_Percent < 20 and round(float(((int(total_count)-int(OA1Null_count))+(int(total_count)-int(OA2Null_count)))/(2*int(total_count)))*100, 2) > 10:
            Discrepancy_Check = Discrepancy_Check + ['{}'.format(check)]
            print('        {} County has road type discrepancies in OWNER fields and will need to be checked on.'.format(check))
        elif TARoad_Percent < 20 and round(float(((int(total_count)-int(TA1Null_count))+(int(total_count)-int(TA2Null_count)))/(2*int(total_count)))*100, 2) > 10:
            Discrepancy_Check = Discrepancy_Check + ['{}'.format(check)]
            print('        {} County has road type discrepancies in TAX fields and will need to be checked on.'.format(check))



#        elif testing_list[0] == 1 and testing_list[1] == 0 and testing_list[2] == 0 and OARoad_Percent < 20:
#            print('        {} County has road type discrepancies in OWNER fields and will need to be checked on.'.format(check))
#        elif testing_list[0] == 0 and testing_list[1] == 1 and testing_list[2] == 0 and TARoad_Percent < 20:
#            print('        {} County has road type discrepancies in TAX fields and will need to be checked on.'.format(check))
#        elif testing_list[0] == 0 and testing_list[1] == 0 and testing_list[2] == 0 and (OARoad_Percent < 20 or TARoad_Percent < 20):
#            print('        {} County has road type discrepancies and will need to be checked on.'.format(check))


        elif testing_list[0] == 1 and testing_list[1] == 1 and testing_list[2] == 1:
            No_Data_Check = No_Data_Check + ['{}'.format(check)]
            print('        {} County has no data and will need to be checked on.'.format(check))
        elif testing_list[0] == 1 and testing_list[1] == 0 and testing_list[2] == 0 and OARoad_Percent > 20:
            print('        {} County is cleared.'.format(check))
        elif testing_list[0] == 0 and testing_list[1] == 1 and testing_list[2] == 0 and OARoad_Percent > 20:
            print('        {} County is cleared.'.format(check))
        elif testing_list[0] == 0 and testing_list[1] == 0 and testing_list[2] == 0 and (OARoad_Percent > 20 or TARoad_Percent > 20):
            print('        {} County is cleared.'.format(check))
#        if (testing_list[0] == 1 and testing_list[1] == 0) or (testing_list[0] == 0 and testing_list[1] == 1)
#       new
        print('        {} counties to go.'.format(len(Selected_Counties_To_Go)))
        print('')





#________________________________________________________________________

#print('\nThese counties may be devoid of data and will require an additional check:\n')
#for spot in Ultimate_Checkup_Counties:
#    print(spot)

#print('\nThese counties prioritize Tax address information that will need to be checked on:\n')
#for spot in Tax_Address_Check:
#    print(spot)

#print('\nThese counties prioritize Owner address information that will need to be checked on:\n')
#for spot in Owner_Address_Check:
#    print(spot)

print('\nThese counties have issues with data and they should be checked on:\n')
for spot in Discrepancy_Check:
    print(spot)

print('\nThese counties have no data and you will need to reach out to the counties directly:\n')
for spot in No_Data_Check:
    print(spot)

# Combined the added entries from the groupings above to finalize the 'Ultimate_Checkup_Counties' list:
# bazinga
Ultimate_Checkup_Counties = Ultimate_Checkup_Counties + Discrepancy_Check + No_Data_Check
Ultimate_Checkup_Counties = list(set(Ultimate_Checkup_Counties))





# Iterate over the "ultimate" entries and find the dates when data was last sumitted and the script was last run:

print('\nChecking on the last date of data updates and script concatenation:\n')

today = date.today()
today_year = today.year
today_month = today.month
today_day = today.day

for county in Ultimate_Checkup_Counties:
    Expression = "COUNTYNAME = '{}'".format(county)
    with arcpy.da.SearchCursor('Metadata', ['COUNTYNAME', 'RunDate', 'AcqDate'], Expression) as cursor:
        for row in cursor:
            sdate = row[1]
            ddate = row[2]
            sdate_trunc = sdate.strftime("%d %B %Y")
            ddate_trunc = ddate.strftime("%d %B %Y")
            ddate_year = ddate.year
            ddate_month = ddate.month
            ddate_day = ddate.day
            d0 =date(ddate_year, ddate_month, ddate_day)
            d1 = date(today_year, today_month, today_day)
            delta = d1 - d0
            days_int = delta.days
            print('{} County was last scripted on {}; data was last acquired on {}. Data are {} days old.'.format(county, sdate_trunc, ddate_trunc, days_int))






# Display time taken just for fun:
print('This script took %s seconds...' % (time.time() - start_time))