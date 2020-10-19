# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 13:48:36 2020

@author: Oscar Brousse

This script applies a variety of filers on the malaria data for each city of interest
It then merges the LCZ predictive variables (see Brousse et al. 2020 ERL paper for the rationale)
It needs to be run prior to Merge_Data_Git.py which merges all the information in one big Data Frame
"""

###############
### IMPORTS ###
###############

import pandas as pd  
import numpy as np
import xarray as xr

######################
### INITIALIZATION ###
######################


cities = ['city1', 'city2', 'city3'] ## Change to the names of cities of interest
resolutions = ['250m', '500m', '1km', '2km'] ## Can be changed according to the buffers used

threshold_patients = 20 ## Can be adapted. Lowering the threshold increases the amount of surveys but lowers the representativity of these surveys
threshold_upage = 18 ## Can be adapted. Adults' infections may be more subject to daily migrations
normalize = False ## Chose whether to normalize the PfPR by Min/Max or not
filtered = True ## Chose to filter the data with the filters applied below

## This switch below just adds an extension to the output file to specify that the user aims at adding a dummy variable to each city
## The inclusion of the dummy is done in the subsequent script Merge_Data_Git.py
dummy_city = True 

if normalize == True:
    norm = '_Norm'
else:
    norm = ''

if dummy_city == True:
    dummy = '_dummy'
else:
    dummy = ''

if filtered == True:
    filt = '_Filt'
else:
    filt = ''

######################
### NORMALIZE DATA ###
######################

## We decided to normalize the data per city by minimum and maximum values

for res in resolutions:
    for city in cities:
        city_res = city + '_' + res
        
        datadir = ''  ## Raw malaria data directory
        datadir_lcz = '' ## LCZ maps directory
        
        file = datadir + city_res + '.csv' ## Raw malaria data saved as a CSV file
        spat_accu_datadir = '' ## Spatially accurate malaria data directory
        spat_accu_file = spat_accu_datadir + city + '.csv' ## Spatially accurate data. Filtering is done manually.
        
        ## Read LCZs map
        ## The LCZ maps were converted fro TIFF to NC files using GDAL
        ## This can be adapted as long as longitudes and latitudes are derived.
        lcz_city = xr.open_dataset(datadir_lcz + city + '_LCZ.nc') 
        lon_lcz = lcz_city.lon.values
        lat_lcz = lcz_city.lat.values
        
        spat_accu_data = pd.read_csv(spat_accu_file, sep = ';')    
        data = pd.read_csv(file, sep='|')
        
        data_filtered = pd.DataFrame(columns = data.columns) ## Create a filtered data frame
        
        if filtered == True:
            for i in range(len(spat_accu_data)):
                predictors_tmp = data[(data['Author'] == spat_accu_data.loc[i,'Author']) & (data['Full_name'] == spat_accu_data.loc[i,'Full_name'])
                            & (data['Lat'] == spat_accu_data.loc[i,'Lat']) & (data['Long'] == spat_accu_data.loc[i,'Long'])
                            & (data['Ex'] == spat_accu_data.loc[i,'Ex']) & (data['PfPR2_10'] == spat_accu_data.loc[i,'PfPR2_10'])
                            & (data['Source_Tit'] == spat_accu_data.loc[i,'Source_Tit'])]
                data_filtered = pd.concat((data_filtered, predictors_tmp), axis = 0)

            ## Filter out surveys with less than 20 patients
            data_filtered = data_filtered[data_filtered['Ex'] > threshold_patients] 
            ## Filter out surveys with patients older than 18
            data_filtered = data_filtered[data_filtered['UpAge'] <= threshold_upage] 
            ## Filter out surveys that are clustered (eg. DHS)
            data_filtered = data_filtered[~data_filtered.Full_name.str.contains("Cluster")] ## Makes sure that DHS data is not present
        
        ## Always filter out data outside the LCZ map
        ## Filter out surveys outside the study area
        data_filtered = data_filtered[data_filtered['Long'] > np.min(lon_lcz)] 
        data_filtered = data_filtered[data_filtered['Long'] < np.max(lon_lcz)] 
        data_filtered = data_filtered[data_filtered['Lat'] > np.min(lat_lcz)] 
        data_filtered = data_filtered[data_filtered['Lat'] < np.max(lat_lcz)] 
        
        city_studied = data_filtered['Name_of_Ci']
        
        PfPR = data_filtered['PfPR2_10']; 
        if normalize == True:
            PfPR = PfPR / max(PfPR)
        
        Nbr_Patients = data_filtered['Ex']
        
        ## This depends on the data that had been extracted.
        ## In our case, the predictive variables started at column number 32. Needs to be adapted if changed.
        predictors = data_filtered.iloc[:,32::]
        
        predictors = pd.concat([city_studied, data_filtered['Long'], data_filtered['Lat'], Nbr_Patients, PfPR, predictors], axis=1)
        
        predictors = predictors.dropna()
        predictors = predictors.reset_index(drop=True)
        
        labels_predictors = list(predictors.columns)
        print(labels_predictors)
        
        var_compact = ['LCZ1_average',                 
                'LCZ2_average',                 
                'LCZ3_average']
        var_open = ['LCZ4_average',                
                'LCZ5_average',                 
                'LCZ6_average']
        var_indu = ['LCZ8_average'
                    ,'LCZ10_average'                 
                    ]
        var_informal = ['LCZ7_average']                 
        var_sparse = ['LCZ9_average']                
        
        var_trees = ['LCZ11_average', 'LCZ12_average']
        var_lowland = ['LCZ13_average',
                'LCZ14_average'              
                ]
        var_mineral = ['LCZ15_average',                 
                       'LCZ16_average',]                
        var_water = ['LCZ17_average']
        var_wetlands = ['LCZ18_average']
        
        var_dist_compact = ['Dist_1_average',                 
                            'Dist_2_average',                 
                            'Dist_3_average']
        var_dist_open = ['Dist_4_average',                 
                            'Dist_5_average',                 
                            'Dist_6_average']
        var_dist_indu = ['Dist_8_average'
                         ,'Dist_10_average'                 
                         ]
        var_dist_informal = ['Dist_7_average']                 
        var_dist_sparse = ['Dist_9_average']                 
        var_dist_trees = ['Dist_11_average','Dist_12_average']
        var_dist_lowland = ['Dist_13_average',
                            'Dist_14_average']             
        var_dist_mineral = ['Dist_15_average',                
                            'Dist_16_average']                 
        var_dist_water = ['Dist_17_average']
        var_dist_wetlands = ['Dist_18_average']
        
        var_indices = ['NDWI_average','NDWI_STD_average','NDVI_average','NDVI_STD_average','SRTM_average']
        
        var_precip = ['Precip_max_average','Precip_min_average','Precip_mean_average']
        
        list_all_predictors = var_compact + var_open + var_indu + var_informal + var_sparse + \
            var_trees + var_lowland + var_mineral + var_water + var_wetlands + \
            var_dist_compact + var_dist_open + var_dist_indu + var_dist_informal + var_dist_sparse + \
            var_dist_trees + var_dist_lowland + var_dist_mineral + var_dist_water + var_dist_wetlands + \
            var_indices + var_precip
        
        all_predictors = pd.DataFrame(np.zeros((len(predictors),len(list_all_predictors))), columns = list_all_predictors)
        all_predictors[all_predictors==0] = np.nan
        
        for var_name in labels_predictors:
            all_predictors.loc[:,var_name] = predictors.loc[:,var_name]
        
        list_names_merged = ['City', 'Lon', 'Lat', 'Ex', 'PfPR2_10', 
                             'LCZ_compact', 'LCZ_open', 'LCZ_indu', 'LCZ_informal', 'LCZ_sparse',  
                             'LCZ_trees','LCZ_lowland','LCZ_mineral','LCZ_water', 'LCZ_wetlands', 
                             'Dist_compact', 'Dist_open', 'Dist_indu', 'Dist_informal', 'Dist_sparse',
                             'Dist_trees','Dist_lowland','Dist_mineral','Dist_water', 'Dist_wetlands',
                             'NDWI', 'NDWI_std', 'NDVI', 'NDVI_std', 'SRTM',
                             'Prec_max','Prec_min','Prec_mean']
        
        
        ####################
        ### MERGING DATA ###
        ####################
        
        LCZ_compact = all_predictors[var_compact].sum(axis='columns')
        LCZ_open = all_predictors[var_open].sum(axis='columns')
        LCZ_indu = all_predictors[var_indu].sum(axis='columns')
        LCZ_informal = all_predictors[var_informal].sum(axis='columns')
        LCZ_sparse = all_predictors[var_sparse].sum(axis='columns')
        LCZ_trees = all_predictors[var_trees].sum(axis='columns')
        LCZ_lowland = all_predictors[var_lowland].sum(axis='columns')   
        LCZ_mineral = all_predictors[var_mineral].sum(axis='columns')             
        LCZ_water = all_predictors[var_water].sum(axis='columns')
        LCZ_wetlands = all_predictors[var_wetlands].sum(axis='columns')
        
        Dist_compact = all_predictors[var_dist_compact].min(axis='columns')
        Dist_open = all_predictors[var_dist_open].min(axis='columns')
        Dist_indu = all_predictors[var_dist_indu].min(axis='columns')
        Dist_informal = all_predictors[var_dist_informal].min(axis='columns')
        Dist_sparse = all_predictors[var_dist_sparse].min(axis='columns')
        Dist_trees = all_predictors[var_dist_trees].min(axis='columns')
        Dist_lowland = all_predictors[var_dist_lowland].min(axis='columns')   
        Dist_mineral = all_predictors[var_dist_mineral].min(axis='columns')             
        Dist_water = all_predictors[var_dist_water].min(axis='columns')
        Dist_wetlands = all_predictors[var_dist_wetlands].min(axis='columns')
        
        LCZ_Merged = [predictors['Name_of_Ci'], predictors['Long'], predictors['Lat'], predictors['Ex'], predictors['PfPR2_10'], 
                      LCZ_compact, LCZ_open, LCZ_indu, LCZ_informal, LCZ_sparse, 
                      LCZ_trees, LCZ_lowland, LCZ_mineral, LCZ_water, LCZ_wetlands,  
                      Dist_compact, Dist_open, Dist_indu, Dist_informal, Dist_sparse,
                      Dist_trees, Dist_lowland, Dist_mineral, Dist_water, Dist_wetlands,
                      all_predictors['NDWI_average'],all_predictors['NDWI_STD_average'],
                      all_predictors['NDVI_average'],all_predictors['NDVI_STD_average'],all_predictors['SRTM_average'],
                      all_predictors['Precip_max_average'],all_predictors['Precip_min_average'],all_predictors['Precip_mean_average']]
        
        
        predictors_merged = np.array([LCZ_Merged]); predictors_merged = predictors_merged[0,:,:].T      
        Data_Merged = pd.DataFrame(predictors_merged, columns=list_names_merged)
        Data_Merged = Data_Merged.fillna(0) ## Just fills NaN obtained after merging prop LCZ with 0 value (no LCZ present in the buffer)
        
        ## Preferably don't change the name of the output file. Otherwise, have to do it in all other scripts
        Data_Merged.to_csv(datadir + city_res + '_Ex' + str(threshold_patients) + 'Min' 
                           + norm + filt + '.csv', header=True, sep=',')

