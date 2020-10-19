
library(randomForest); library(caret); library(VSURF); library(readr); library(dplyr); library(SpatialML); library(readxl); library(openxlsx); library(pdp)

rm(list = ls())
setwd("~/Work/REACT/PfPR_Modelling/")

## Predictive variables and resolutions of buffer size around malaria point were chosen through a sensitivity test 
## using 25 bootstrapped RF models evaluated against 20% of randomly selected malaria surveys per city 
## See Python script "RandomForest_Git.R"

## Leave one city out Random Forest modelling. 
## Predicts PfPR 2-10 in the city of interest using the malaria data of all other cities

cities = list('city1', 'city2', 'city3') ## Add the name of the cities of interest
res = '1km' ## Adapt based on the best buffer

i=1
results = matrix(0, ncol=3,nrow=length(cities))
rownames(results) <- c(cities)
colnames(results) <- c('RMSE', 'R2', 'MAE')

var_importance = list()

## The var_list is based on the optimal set of variables for the cities of interest obtained by the RandomForest_Git.R

var_list=c('LCZ_compact', 'LCZ_open', 'LCZ_indu', 'LCZ_informal', 'LCZ_sparse',  
           'LCZ_trees','LCZ_lowland','LCZ_water','LCZ_wetlands', 
           'Dist_compact', 'Dist_open', 'Dist_indu', 'Dist_informal', 'Dist_sparse',
           'Dist_trees','Dist_lowland','Dist_water','Dist_wetlands',
           'NDWI', 'NDWI_std', 'NDVI', 'NDVI_std', 'SRTM',
           'Prec_max','Prec_min','Prec_mean'
)

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


data_city = read.csv(paste0('Final_Merged_Predictors/All_Data_',res,'_Ex20Min',Norm,filt,'.csv'))
colnames(data_city)

### Leave one city out

for (city in cities){
  
  city_test=data_city[data_city$City == city, ]
  city_train=data_city[data_city$City != city, ]

  rf_allvars=randomForest(city_train$PfPR2_10~.,data=city_train[,var_list],ntree=1000,importance=TRUE,mtry=4)
  rf_pred=predict(rf_allvars,city_test[,var_list])
  
  var_importance[[i]] <- importance(rf_allvars)

  metrics=caret::postResample(rf_pred,city_test$PfPR2_10)
  results[i,1]=metrics[1]
  results[i,2]=metrics[2]
  results[i,3]=metrics[3]
  
  predicted_observed = cbind(rf_pred, city_test$PfPR2_10)
  colnames(predicted_observed) <- c('Pred_PfPR2_10', 'Obs_PfPR2_10')
  
  write.csv(predicted_observed, file = paste0("Final_Merged_Predictors/Predict_All_OneCity/",city,"_",res,"_PredObs",Norm,filt,".csv"))
  
  i=i+1
}

## Save all necessary outputs for plotting in Python

write.csv(var_importance, file = paste0("Final_Merged_Predictors/Leave_One_City/LeaveOneCity_",res,"_Var_Importance",Norm,filt,".csv"))
write.csv(results, file = paste0("Final_Merged_Predictors/Leave_One_City/LeaveOneCity_",res,"_RF_Results",Norm,filt,".csv"))