
library(randomForest); library(caret); library(VSURF); library(readr); library(dplyr); library(SpatialML); library(readxl); library(openxlsx); library(pdp)

rm(list = ls())
setwd("") ## Set the working directory

## LCZ variables are previously merged by their similarities. 
## See Python script "Merge_Data_PfPR_Modelling_Git.py" and Bechtel et al. (2017)

## Chose which predictive variables out of LCZ to keep. NDVI, NDWI and SRTM are always kept
## For proportions of LCZ only (PROP = TRUE, DIST = FALSE)
## For distances to other LCZ only (PROP = FALSE, DIST = TRUE)
## For all variables (PROP = FALSE, DIST = FALSE)
## For inclusion of dummies (dummy_city = TRUE)

PROP = FALSE
DIST = FALSE

## Chose to perform RF model only on best predictive variables from VSURF using all variables: 
## PROP = FALSE, DIST = FALSE, BEST = TRUE

BEST = TRUE

cities = list('city1', 'city2', 'city3') ## Add the name of the cities of interest
resolutions = list('250m', '500m', '1km', '2km') ## Can be adapted but needs to be done consistently throughout the scripts

for (res in resolutions){

## Adapt these switches based on the choices made in Merge_Data_PfPR_Modelling_Git.py
  
normalize = FALSE
filtered = TRUE
dummy_city = FALSE
idl_dummy = FALSE

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

if (dummy_city == TRUE){
  dummy = '_dummy'
} else {
  dummy = ''
}

## Should not be adapted normally if output files names were not changed. If yes, then change accordingly

data_city = read.csv(paste0('Final_Merged_Predictors/All_Data_',res,'_Ex20Min',Norm,filt,dummy,'.csv')) 

colnames(data_city)

var_list_merged=c('LCZ_compact', 'LCZ_open', 'LCZ_indu', 'LCZ_informal', 'LCZ_sparse',  
                  'LCZ_trees','LCZ_lowland','LCZ_water','LCZ_wetlands', 
                  'Dist_compact', 'Dist_open', 'Dist_indu', 'Dist_informal', 'Dist_sparse',
                  'Dist_trees','Dist_lowland','Dist_water','Dist_wetlands',
                  'NDWI', 'NDWI_std', 'NDVI', 'NDVI_std', 'SRTM',
                  'Prec_max','Prec_min','Prec_mean')

if (dummy_city == TRUE){
  var_list_merged = c('LCZ_compact', 'LCZ_open', 'LCZ_indu', 'LCZ_informal', 'LCZ_sparse',  
                      'LCZ_trees','LCZ_lowland','LCZ_water','LCZ_wetlands', 
                      'Dist_compact', 'Dist_open', 'Dist_indu', 'Dist_informal', 'Dist_sparse',
                      'Dist_trees','Dist_lowland','Dist_water','Dist_wetlands',
                      'NDWI', 'NDWI_std', 'NDVI', 'NDVI_std', 'SRTM',
                      'Prec_max','Prec_min','Prec_mean',
                      'Dummies')
}

if (PROP == TRUE){
  var_list = var_list_merged[-10:-18] ## Without Distances to LCZ 
} else if (DIST == TRUE){
  var_list = var_list_merged[-1:-9]   ## Without Proportions of LCZ
} else{
  var_list = var_list_merged
}

print(var_list)

bootstrap = 25
number_split = 5 

## Best predictive variables using VSURF module

if (BEST == TRUE){
  Surf=VSURF(data_city$PfPR2_10~.,data=data_city[var_list], ncores=12)
  subset=data_city[var_list]
  index=colnames(subset[,Surf$varselect.interp])
  print(index)
  } 

## kfold with VSURF
tunegrid <- expand.grid(mtry=c(1:length(var_list)))

if (BEST == TRUE){
  pred_var=data_city[,index]
} else {
  pred_var=data_city[,var_list]
}

classifier_rf_PO <- train(y=data_city$PfPR2_10,
                          x=pred_var,
                          data=data_city,
                          method='rf',
                          ntree=1000,
                          tuneGrid = tunegrid,
                          trControl=trainControl(method='repeatedcv',
                                                 number=number_split,
                                                 repeats=5,
                                                 savePredictions = "final",
                                                 returnResamp = "final"
                          ))
print(res)
print(classifier_rf_PO$bestTune)
mtry_best = classifier_rf_PO$bestTune

### Stratified Bootstrap
i=1
results= matrix(0, ncol=3,nrow=bootstrap)
var_importance = list()
for(j in 1:bootstrap) {
  city_test <- data.frame()
  city_train <- data.frame()
  for (city in cities){
    city_test_tmp=data_city[data_city$City == city, ] %>%  sample_frac(.2)
    city_train_tmp=subset(data_city[data_city$City == city, ], !(X %in% city_test_tmp$X))
    city_test <- rbind(city_test, city_test_tmp)
    city_train <- rbind(city_train, city_train_tmp)
  }
  
  if (BEST == TRUE){
    rf_allvars=randomForest(city_train$PfPR2_10~.,data=city_train[,index],ntree=1000,importance=TRUE,mtry=mtry_best[[1]])
    rf_pred=predict(rf_allvars,city_test[,index])
  } else {
    rf_allvars=randomForest(city_train$PfPR2_10~.,data=city_train[,var_list],ntree=1000,importance=TRUE,mtry=mtry_best[[1]])
    rf_pred=predict(rf_allvars,city_test[,var_list])
  }

  var_importance[[i]] <- importance(rf_allvars)

  metrics=caret::postResample(rf_pred,city_test$PfPR2_10)
  results[i,1]=metrics[1]
  results[i,2]=metrics[2]
  results[i,3]=metrics[3]
  i=i+1
}

## Save all necessary outputs for plotting in Python
## Should not be adapted normally if output files names were not changed. If yes, then change accordingly

if ((PROP == TRUE)&(DIST == FALSE)){
    write.csv(var_importance, file = paste0("Final_Merged_Predictors/All_Data_",res,"_Var_Importance_PROP",Norm,filt,dummy,".csv"))
    write.csv(results, file = paste0("Final_Merged_Predictors/All_Data_",res,"_RF_Results_PROP",Norm,filt,dummy,".csv"))
  } else if ((PROP == FALSE)&(DIST == TRUE)) {
    write.csv(var_importance, file = paste0("Final_Merged_Predictors/All_Data_",res,"_Var_Importance_DIST",Norm,filt,dummy,".csv"))
    write.csv(results, file = paste0("Final_Merged_Predictors/All_Data_",res,"_RF_Results_DIST",Norm,filt,dummy,".csv"))
  } else
  {
    if (BEST == TRUE) {
      write.csv(var_importance, file = paste0("Final_Merged_Predictors/All_Data_",res,"_Var_Importance_ALL_BEST",Norm,filt,dummy,".csv"))
      write.csv(results, file = paste0("Final_Merged_Predictors/All_Data_",res,"_RF_Results_ALL_BEST",Norm,filt,dummy,".csv"))
    } else {
      write.csv(var_importance, file = paste0("Final_Merged_Predictors/All_Data_",res,"_Var_Importance_ALL",Norm,filt,dummy,".csv"))
      write.csv(results, file = paste0("Final_Merged_Predictors/All_Data_",res,"_RF_Results_ALL",Norm,filt,dummy,".csv"))
    }
}
}