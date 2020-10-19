# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 12:22:06 2020

@author: Oscar Brousse

This script builds a complete Data Frame merging all the malaria data from cities of interest to run the RF modelling in R
First run Merge_Data_PfPR_Modelling_Git.py
"""

###############
### IMPORTS ###
###############

import pandas as pd

######################
### INITIALIZATION ###
######################

datadir = '' ## Same as in Merge_Data_PfPR_Modelling_Git.py
savedir = ''

cities = ['city1', 'city2', 'city3'] ## Change to the names of cities of interest
resolutions = ['250m', '500m', '1km', '2km'] ## Can be changed according to the buffers used

## Needs to be adapted based on the choices made in Merge_Data_PfPR_Modelling_Git.py
threshold_patients = 20
normalize = False
filtered = True
dummy_city = False ## Add a dummy variable per city

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


Var_List = ['City', 'Lon', 'Lat', 'Ex', 'PfPR2_10', 
            'LCZ_compact', 'LCZ_open', 'LCZ_indu', 'LCZ_informal', 'LCZ_sparse',  
            'LCZ_trees','LCZ_lowland','LCZ_mineral','LCZ_water', 'LCZ_wetlands', 
            'Dist_compact', 'Dist_open', 'Dist_indu', 'Dist_informal', 'Dist_sparse',
            'Dist_trees','Dist_lowland','Dist_mineral','Dist_water', 'Dist_wetlands',
            'NDWI', 'NDWI_std', 'NDVI', 'NDVI_std', 'SRTM',
            'Prec_max','Prec_min','Prec_mean']

if dummy_city == True:
    Var_List = ['City', 'Lon', 'Lat', 'Ex', 'PfPR2_10', 
            'LCZ_compact', 'LCZ_open', 'LCZ_indu', 'LCZ_informal', 'LCZ_sparse',  
            'LCZ_trees','LCZ_lowland','LCZ_mineral','LCZ_water', 'LCZ_wetlands', 
            'Dist_compact', 'Dist_open', 'Dist_indu', 'Dist_informal', 'Dist_sparse',
            'Dist_trees','Dist_lowland','Dist_mineral','Dist_water', 'Dist_wetlands',
            'NDWI', 'NDWI_std', 'NDVI', 'NDVI_std', 'SRTM',
            'Prec_max','Prec_min','Prec_mean']

#########################
### READ & MERGE DATA ###   
#########################
for res in resolutions:
    All_Data_df = pd.DataFrame(columns=Var_List)
    for city in cities:   
        file = datadir + city + '_' + res + '_Ex' + str(threshold_patients) + 'Min' + norm + filt + '.csv'
        data = pd.read_csv(file, sep=',')
        All_Data_df = pd.concat([All_Data_df, data], axis=0)
    All_Data_df = All_Data_df.fillna(0)
    if dummy_city == True:
        All_Data_df['Dummies'] = 0
        for i in range(len(cities)):
            All_Data_df['Dummies'][All_Data_df['City'] == cities[i]] = i
            
    ## Preferably don't change the name of the output file. Otherwise, have to do it in all other scripts
    All_Data_df.to_csv(savedir + 'Final_Merged_Predictors/All_Data_' + res + '_Ex' + str(threshold_patients) + 'Min' 
                       + norm + filt + dummy + '.csv', header=True, sep=',')
