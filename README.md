# REACT LCZ for Malaria (ERL paper: Brousse et al. 2020)

### Workflow:
1. **Variables extraction in buffers**

The script City_Variables_Extraction.ipynb is created as a Jupyter Notebook. This script permits the extraction of all the variables required by the Random Forest algorithm at the desired buffer. Buffers are centered around each malaria survey. The new user needs to change all the directories that refer to inputs and outputs. They also need to acquire the relevant satellite data. For this, please follow the indications given in the ERL paper. All data was extracted at a horizontal grid of 100 m in Google's Earth Engine, apart from the MSWEP precipitation data. For the LCZ maps, please refer to the WUDAPT website.

2. **Filter and merge all the data for the cities of interest**

Once all the data is acquired, you need to run two Python scripts: Merge_Data_PfPR_Modelling_Git.py first and then Merge_Data_Git.py . The first one filters the malaria data based on the criteria given in the ERL paper. These can be adapted for each city of interest. It also merges LCZs according to their similarities (see Bechtel et al. 2017). In addition, this script permits the normalization of PfPR 2-10 by the maximum and the minimum. Once run, you need to run Merge_Data_Git.py which will compile a single data frame that will be used in the R program for running the Random Forest algorithm. In this scripts, you can chose to add a dummy variable per city.

3. **Testing the buffer sizes and the predictive variables' importance**

The next step consists in running the Random Forest algorithm in R to define which set of variable is the most predictive for the cities of interest as well as the optimal buffer size around malaria surveys. You can also test the added value of the dummy variable for the model's performance. This is done by running the RandomForest_Git.R script.

4. **Predicting PfPR 2-10 per city**

Once you have defined the optimal set of variables aggregated within a certain buffer size around the malaria survey, you can predict the PfPR 2-10 for the chose city of interest by running each strategy: "Single City", "All Other Cities" or "All Cities". Please refer to the ERL paper for more information about these strategies. 
