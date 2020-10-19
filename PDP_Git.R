
library(randomForest); library(caret); library(VSURF); library(readr); library(dplyr); library(SpatialML); library(readxl); library(openxlsx); library(pdp)

rm(list = ls())
setwd("")  ##Chose a working environment

## Script for obtention of partial dependendy plots for all variables at a chosen resolution
## LCZ variables are previously merged by their similarities. 
## See Python script "Merge_Data_PfPR_Modelling_Git.py" and Bechtel et al. (2017) for more information on LCZ similarities

cities = list('city1', 'city2', 'city3') ## Change the name of the cities and add as many cities as studied cities
resolutions = c('1km')  ## Change the resolution based on the buffer sizes that were chosen

for (res in resolutions){
  
  ## Adapt these switches based on the choices made in Merge_Data_PfPR_Modelling_Git.py
  normalize = FALSE
  filtered = TRUE
  
  if (normalize == TRUE){
    Norm = '_Norm'
  } else {
    Norm = ''
  }
  
  if (filtered == TRUE){
    filt = '_Filt'
  } else {
    filt = ''
  }

  ## Should not be adapted normally if output files names were not changed. If yes, then change accordingly
  data_city = read.csv(paste0('Final_Merged_Predictors/All_Data_',res,'_Ex20Min',Norm,filt,'.csv'))
  
  colnames(data_city)
  
  var_list=c('LCZ_compact', 'LCZ_open', 'LCZ_indu', 'LCZ_informal', 'LCZ_sparse',  
             'LCZ_trees','LCZ_lowland','LCZ_mineral','LCZ_water', 'LCZ_wetlands', 
             'Dist_compact', 'Dist_open', 'Dist_indu', 'Dist_informal', 'Dist_sparse',
             'Dist_trees','Dist_lowland','Dist_mineral','Dist_water', 'Dist_wetlands',
             'NDWI', 'NDWI_std', 'NDVI', 'NDVI_std', 'SRTM',
             'Prec_max','Prec_min','Prec_mean')

  bootstrap=25
    
## Partial dependency plot

pdp_plots <- array(NaN, c(length(data_city$PfPR2_10),(bootstrap*2),length(var_list)))

 for (i in 1:bootstrap) {
   rf_allvars=randomForest(data_city$PfPR2_10~.,data=data_city[var_list],mtry=4,ntree=1000,importance=TRUE)
   rf_allvars

   for (j in 1:length(var_list)) {
     part_dep <- partial(rf_allvars, var_list[j], ice = FALSE, center = TRUE, smooth=TRUE,lwd=2,
                 plot = TRUE, rug = TRUE, alpha = 1, plot.engine = "ggplot2",
                 train =as.matrix(data_city[var_list]))
     part_dep

     vector_pdp_out = part_dep$data
     pdp_plots[1:length(vector_pdp_out[[1]]),i,j] <- as.matrix(vector_pdp_out[c(1)])
     pdp_plots[1:length(vector_pdp_out[[2]]),i+bootstrap,j] <- as.matrix(vector_pdp_out[c(2)])
   }
 }

## Write all outputs in CSV and XLSX sheets

# Create a blank workbook
 output_pdp <- createWorkbook()

 for (i in 1:length(var_list)){
   addWorksheet(output_pdp, paste0(var_list[i]))
   writeData(output_pdp, sheet = paste0(var_list[i]), x = data.frame(pdp_plots[,,i]))
 }

## Save all necessary outputs for plotting in Python

 output_file = paste0("PDP_indicators.xlsx")  ## Chose an output file name
 #Delete file if it exists
 if (file.exists(output_file)){
   file.remove(output_file)
 }
 saveWorkbook(output_pdp, paste0(output_file))
}