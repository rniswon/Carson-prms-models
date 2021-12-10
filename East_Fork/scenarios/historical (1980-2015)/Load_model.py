import os
import gsflow
import matplotlib.pyplot as plt
import numpy as np
import pyemu
import pandas as pd

## The GSFLOW model is loaded as follows
control_file = r"C:\Users\rniswon\Documents\Data\Git\Carson-prms-models.git\East_Fork\scenarios\historical (1980-2015)\eastfork_clim2_hist.control"
gs = gsflow.GsflowModel.load_from_file(control_file)
#gs = Gsflow(control_file=control_file)

#ssmax = gs.prms.parameters.get_values('soil_moist_max')
nrows = 332
ncols = 217
hru_type = gs.prms.parameters.get_values('hru_type')
hru_subbasin = gs.prms.parameters.get_values('hru_subbasin')  #gets as a vector
sat_threshold = gs.prms.parameters.get_values('sat_threshold')
soil_moist_max = gs.prms.parameters.get_values('soil_moist_max')
mask = hru_type > 0
#dprst_depth_avg = np.zeros_like(dprst_depth_avg)  # set all values to zero
plt.imshow(gs.prms.parameters.get_values('soil_moist_max').reshape(nrows,ncols))  #converts to grid
plt.show()
plt.imshow(gs.prms.parameters.get_values('hru_subbasin').reshape(nrows,ncols))  #converts to grid
plt.show()
#gs.prms.parameters.set_values(name="dprst_depth_avg", values=dprst_depth_avg)
#gs.write_input(workspace="Ag_EP2a_dprst", basename='gsflow_gsflowHighKc')
#rain_adj=gs.prms.parameters.get_values('rain_adj')
i=1