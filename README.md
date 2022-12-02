# parcel-data-check
 Collection of scripts for assessing/analyzing datasets.

This repository contains (or will contain) a collection of scripts that I've utilized for assessing property parcel status across multiple counties. These scripts have been tweaked to allow anyone to utilize them and adjust the file sources (if applicable) for their personal use. 



"parcel_data_check.py"                 (Packages Required: os, arcpy, time, datetime, copy)

Issue: 
I was tasked with an annual review of parcels within specific counties to ensure that appropriate data existed to contact landowners for ongoing wildlife management. The parcel dataset incorporates close to 100 county parcel datasets on a quarterly basis and the data acquired can vary in quality and completion from year to year. Sometimes, a county may be completely empty. At other times, a county may have strictly property owner information but no address data. Still other occasions find that the names and street addresses are there, but there is no information on city/state/zip data. Sometimes, the physical address information is complete but the tax information is missing, and vice versa.

Rather than manually access the hosted shapefiles and ocularly inspect the attribute tables for the status of all parcels to ensure that the fields for names and street addresses were satisfactorily populated, I decided to write a script to check on the data with an eye for data presence assessment. 


Solution: 

1)
The script draws in data from the following sources:
"Parcels": parcel shapefile provided by my organization
"Counties": county shapefile provided by my organization
"Selector": shapefile containing county parcels that will be investigated by my partnering organizaiton
"Metadata": metadata shapefile for the "Parcels" shapefile provided by my organization

2)
The script sources the datasets listed above, defines a list of counties that will be investigated, then analyzes appropriate fields within the "Parcels" shapefile according to each constituent county and displays a list of results. In this case, there are two types of addresses : physical (OWNER, 6 fields with name or address information) and mailing/tax (TAX, 5 fields with name or address information). The script iterates over each of the selecting counties, selects the parcels that are within each selecting county, and records a count of how many polygons have a "NULL" value. The script also records a value for the number of polygons for which all of the 'OWNER' and 'TAX' fields are entirely empty and another for whether the address data fields are empty (but not the name fields). 

3)
Some calculations are run to determine the percentage of null values within each of the fields. Based on those calculations, it  investigates the status of the county parcels further: a mostly-empty series of 'OWNER' fields may not mean that the parcel is inadequate (the 'TAX' fields may be satisfactory, instead), and a mostly-empty series of 'TAX' fields might be matched with a complete series of 'OWNER' fields. Thus, the fields are assessed to determine whether they have >60% 'NULL' values. If they do, an iterable value is applied to a list ([testing_list]) from which various status indicators can be derived. If there are discrepancies, other lists are populated for further checks. 

4)
When the script finishes its run, a series of text blocks indicate which counties will need to be checked on, and the varying degree of the severity that flagged a request for a checkup. 

#_______________________________________________________________________________________________________________________________________


"parcel_data_deep_check.py"                 (Packages Required: os, arcpy, time, datetime, copy)

Issue: 
I was tasked with an annual review of parcels within specific counties to ensure that appropriate data existed to contact landowners for ongoing wildlife management. The parcel dataset incorporates close to 100 county parcel datasets on a quarterly basis and the data acquired can vary in quality and completion from year to year. Sometimes, a county may be completely empty. At other times, a county may have strictly property owner information but no address data. Still other occasions find that the names and street addresses are there, but there is no information on city/state/zip data. Sometimes, the physical address information is complete but the tax information is missing, and vice versa.

Rather than manually access the hosted shapefiles and ocularly inspect the attribute tables for the status of all parcels to ensure that the fields for names and street addresses were satisfactorily populated, I decided to write a script to check on the data with an eye for data presence assessment. The "parcels_data_check.py" script was successful in determining whether the various counties in question had the proper amount of data to negate the need for additional checks, but I was also curious about the deeper question about whether the data include road type designations (e.g. "123 Broadyway" may not be complete compared with "123 Broadway Avenue").


Solution: 

1)
The script draws in data from the following sources:
"Parcels": parcel shapefile provided by my organization
"Counties": county shapefile provided by my organization
"Selector": shapefile containing county parcels that will be investigated by my partnering organizaiton
"Metadata": metadata shapefile for the "Parcels" shapefile provided by my organization

2)
The script draws in a list of road types (plus abbrevations), then sets up a series of expressions that will be used to check on the presence of those terms in the address fields of the parcel data. 

The script sources the datasets listed in the first step, defines a list of counties that will be investigated, then analyzes appropriate fields within the "Parcels" shapefile according to each constituent county and displays a list of results. In this case, there are two types of addresses : physical (OWNER, 6 fields with name or address information) and mailing/tax (TAX, 5 fields with name or address information). The script iterates over each of the selecting counties, selects the parcels that are within each selecting county, and records a count of how many polygons have a "NULL" value. The script also records a value for the number of polygons for which all of the 'OWNER' and 'TAX' fields are entirely empty and another for whether the address data fields are empty (but not the name fields). Further, the script checks on whether road type entries are present in the fields. 

3)
Some calculations are run to determine the percentage of null values within each of the fields. Based on those calculations, it  investigates the status of the county parcels further: a mostly-empty series of 'OWNER' fields may not mean that the parcel is inadequate (the 'TAX' fields may be satisfactory, instead), and a mostly-empty series of 'TAX' fields might be matched with a complete series of 'OWNER' fields. Thus, the fields are assessed to determine whether they have >60% 'NULL' values. If they do, an iterable value is applied to a list ([testing_list]) from which various status indicators can be derived. If there are discrepancies, other lists are populated for further checks. 

Additional calculations are run to determine the percentage of each field that contains road type entries. By subtracting the null values of each field from the total number of entries in a field, the numerator (road type entries that come back TRUE) will adjust to only evaluate the number of cells that have entires. For owner or tax addresses, if the percentage of the address road entry presence percentage is greater than 20% and the number of cells with data in the first two columns of either owner or tax addresses is greater than 10 % (indicating that the fields do have more than incidental data), the county is flagged as needing an extra check. 
        - This threshold was somewhat arbitrary and seemed to match the ocular inspection of the counties when I checked them manually.

4)
When the script finishes its run, a series of text blocks indicate which counties will need to be checked on, and the varying degree of the severity that flagged a request for a checkup. 

