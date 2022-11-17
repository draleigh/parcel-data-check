#-------------------------------------------------------------------------------
# Name:        Parcel Status Analysis
# Purpose:      For checking on the status of parcels within specific counties
#                   to determine whether extra effort is required to find 
#                   full parcel datasets from specific counties. 
# Author:      draleig
#
# Created:     21 October 2022
# Copyright:   (c) draleig 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import os,arcpy,time,datetime,copy
from datetime import date, timedelta

from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

# Define Data Locations and Other Variables
Parcels = *path to parcel shapefile*
Counties = *path to county shapefile*
# This may need to be adjusted once the final DPA numbers are confirmed/updated (or from year to year):
Selector = *path to "Selector" shapefile*
Metadata = *path to "Selector" shapefile*

Selected_Counties = []                                      # define a temporary list for counties that will be analyzed
Selected_Counties_To_Go = []                                # define a temporary list to track the number of counties still to be analyzed
start_time = time.time()


arcpy.MakeFeatureLayer_management(Counties, 'Counties')                                     # Make temporary feature layer for counties
arcpy.MakeFeatureLayer_management(Parcels, 'Parcels')                                       # Make temporary feature layer for parcels
arcpy.MakeFeatureLayer_management(Metadata, 'Metadata')                                     # Make temporary feature layer for metadata
arcpy.SelectLayerByLocation_management('Counties', "INTERSECT", Selector, 0, "NEW_SELECTION")
with arcpy.da.SearchCursor('Counties', ['CTY_NAME']) as cursor:
    for row in cursor:
        print('{} County'.format(row[0]))
        Selected_Counties = Selected_Counties + ['{}'.format(row[0])]           # maybe sort them first, or is that necessary?
arcpy.SelectLayerByAttribute_management('Counties', "CLEAR_SELECTION")
Selected_Counties_To_Go = copy.copy(Selected_Counties)
Selected_Add_Counties_To_Go = copy.copy(Selected_Counties)
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
        testing_list = [0, 0, 0]
        Expression = "CTY_NAME = '{}'".format(check)
        arcpy.SelectLayerByAttribute_management('Counties', "NEW_SELECTION", Expression)
        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # Begin selecting all parcels within the county
        total_count = arcpy.GetCount_management('Parcels').getOutput(0)                                     # total_count is sum of all parcels
        OWNER_NULL = "OWNER_NAME IS NULL"                                                                   # Begin checking all Null 'OWNER' entries
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

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        OWN_ADD2_NULL = "OWN_ADD_L2 IS NULL"
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OWN_ADD2_NULL)
        OA2Null_count = arcpy.GetCount_management('Parcels').getOutput(0)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        OWN_ADD3_NULL = "OWN_ADD_L3 IS NULL"
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OWN_ADD3_NULL)
        OA3Null_count = arcpy.GetCount_management('Parcels').getOutput(0)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        OWN_ADD4_NULL = "OWN_ADD_L4 IS NULL"
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", OWN_ADD4_NULL)
        OA4Null_count = arcpy.GetCount_management('Parcels').getOutput(0)





        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")      # Begin checking all Null values in TAX entries
        TAX_NULL = "TAX_NAME IS NULL"
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TAX_NULL)
        TNull_count = arcpy.GetCount_management('Parcels').getOutput(0)

        arcpy.SelectLayerByLocation_management('Parcels', "INTERSECT", 'Counties', 0, "NEW_SELECTION")
        TAX_ADD1_NULL = "TAX_ADD_L1 IS NULL"
        arcpy.SelectLayerByAttribute_management('Parcels', "SUBSET_SELECTION", TAX_ADD1_NULL)
        TA1Null_count = arcpy.GetCount_management('Parcels').getOutput(0)

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

        Selected_Counties_To_Go.remove(check)
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
        elif testing_list[0] == 1 and testing_list[1] == 1 and testing_list[2] == 1:
            No_Data_Check = No_Data_Check + ['{}'.format(check)]
            print('        {} County has no data and will need to be checked on.'.format(check))
        elif testing_list[0] == 1 and testing_list[1] == 0 and testing_list[2] == 0:
            print('        {} County is cleared.'.format(check))
        elif testing_list[0] == 0 and testing_list[1] == 1 and testing_list[2] == 0:
            print('        {} County is cleared.'.format(check))
        elif testing_list[0] == 0 and testing_list[1] == 0 and testing_list[2] == 0:
            print('        {} County is cleared.'.format(check))
#        if (testing_list[0] == 1 and testing_list[1] == 0) or (testing_list[0] == 0 and testing_list[1] == 1)
        print('        {} counties to go.'.format(len(Selected_Counties_To_Go)))
        print('')





print('\nThese counties may be devoid of data and will require an additional check:\n')
for spot in Ultimate_Checkup_Counties:
    print(spot)

print('\nThese counties have issues with data and they should be checked on:\n')
for spot in Discrepancy_Check:
    print(spot)

print('\nThese counties have no data and you will need to reach out to the counties directly:\n')
for spot in No_Data_Check:
    print(spot)

# Combined the added entries from the groupings above to finalize the 'Ultimate_Checkup_Counties' list:

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
# took 701 seconds on prior run