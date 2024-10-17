library(gsubfn)
library(dataRetrieval)
library(hydroGOF)

# Define function for reading statvar file
readstatvar2df <- function(fname){
  print(paste0('Reading ',as.character(basename(fname)),' ...'))
  
  # get header information
  fname_con <- file(fname)
  con <- fname_con
  open(con)
  nstats <- as.integer(readLines(con, n = 1, warn = FALSE))
  close(con)
  
  # Read the variable names
  txt_lines <- read.table(fname, skip=1, nrows=nstats, col.names=c('var_name','code'))
  
  # Strip trailing '1's on basin variables; attach any segment numbers to names
  dfn <- ifelse(txt_lines$code==1, as.character(txt_lines$var_name), paste0(txt_lines$var_name,'_',txt_lines$code))
  
  # Read the meat
  dat <- read.table(fname, skip=nstats + 1, col.names=c('rownum','yr','mon','day','H','M','S',dfn))
  
  # Construct usable date column
  dat$Date <- with(dat, as.Date(paste0(yr,'-',mon,'-',day), '%Y-%m-%d'))
  
  # Drop and reorder columns
  dat2 <- dat[,c(ncol(dat),seq(8, ncol(dat)-1, by=1))]
  
  dat2
}

# Replace the following depending on where the repo is cloned to:
base_pth <- 'E:/WftS_reboot/Rich_UpCatch_PRMS_models.git'

wf_sca_fl <- paste(base_pth, 'West_Fork/SCA/statvar_sca.dat', sep='/')
wf_reg_fl <- paste(base_pth, 'West_Fork/scenarios/historical (1980-2015)/statvar_hist.dat', sep='/')
ef_sca_fl <- paste(base_pth, 'East_Fork/SCA/statvar_sca.dat', sep='/')
ef_reg_fl <- paste(base_pth, 'East_Fork/scenarios/historical (1980-2015)/statvar_hist_gsflow.dat', sep='/')

wf_sca <- readstatvar2df(wf_sca_fl)
wf_reg <- readstatvar2df(wf_reg_fl)
ef_sca <- readstatvar2df(ef_sca_fl)
ef_reg <- readstatvar2df(ef_reg_fl)

# Get the observed flows for comparison
StartDate <- "1980-10-01"
EndDate <- "2015-09-30"

siteNumber <- "10310000"  # Woodfords
QParameterCd <- "00060"
Daily_wf <- readNWISDaily(siteNumber, QParameterCd, StartDate, EndDate)

siteNumber <- "10309000"  # E Fk nr Gardnerville
Daily_ef <- readNWISDaily(siteNumber, QParameterCd, StartDate, EndDate)


gof(wf_sca$basin_cfs, Daily_wf$Q * 35.315)
gof(wf_reg$basin_cfs, Daily_wf$Q * 35.315)
#             SCA   regular
# ME        -1.22     -0.68
# MAE       32.34     34.79
# MSE     8521.13   7898.21
# RMSE      92.31     88.87
# ubRMSE    92.30     88.87
# NRMSE %   56.40     54.30
# PBIAS %   -1.20     -0.70
# RSR        0.56      0.54
# rSD        0.94      0.91
# NSE        0.68      0.71
# mNSE       0.67      0.64
# rNSE       0.91      0.89
# wNSE       0.53      0.55
# wsNSE      0.56      0.54
# d          0.91      0.91
# dr         0.83      0.82
# md         0.83      0.82
# rd         0.97      0.97
# cp        -1.43     -1.25
# r          0.83      0.84
# R2         0.68      0.71
# bR2        0.57      0.58
# VE         0.68      0.65
# KGE        0.82      0.82
# KGElf      0.77      0.60
# KGEnp      0.90      0.88
# KGEkm      0.83      0.84


gof(ef_sca$basin_cfs, Daily_ef$Q * 35.315)
gof(ef_reg$basin_cfs, Daily_ef$Q * 35.315)
#               SCA      regular
# ME           3.73       -10.66
# MAE        127.55       146.16
# MSE     110765.60    128626.06
# RMSE       332.81       358.64
# ubRMSE     332.79       358.49
# NRMSE %     62.10        66.90
# PBIAS %      1.10        -3.00
# RSR          0.62         0.67
# rSD          1.00         1.12
# NSE          0.61         0.55
# mNSE         0.62         0.56
# rNSE         0.85         0.82
# wNSE         0.53         0.50
# wsNSE        0.51         0.45
# d            0.89         0.89
# dr           0.81         0.78
# md           0.81         0.80
# rd           0.96         0.96
# cp          -1.66        -2.09
# r            0.81         0.81
# R2           0.61         0.55
# bR2          0.53         0.51
# VE           0.64         0.58
# KGE          0.81         0.77
# KGElf        0.40        -1.08
# KGEnp        0.89         0.84
# KGEkm        0.81         0.80
