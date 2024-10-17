# Carson-prms-models
### 2 prms models for east and west forks of the upper Carson River
### Final claibrated parameter file is in the SCA folder within each fork

Note: on 10/17/2024 an R script was added to assess PRMS model fits.
Script is located here: ./scripts/Assess_PRMS_Fits.R
Fits are assessed by comparing the gaged output to simulated equivalents from the following models:

./West_Fork/SCA/westfork_sca.control
./West_Fork/scenarios/historical (1980-2015)/westfork_clim2.control
./East_Fork/SCA/eastfork_sca.control
./East_Fork/scenarios/historical (1980-2015)/eastfork_clim2_hist.control

Various fit statistics can be found at the end of the R script.