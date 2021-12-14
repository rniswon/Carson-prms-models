import os
import gsflow
import matplotlib.pyplot as plt
import numpy as np
import pyemu
import pandas as pd
import datetime
from datetime import date
from datetime import timedelta
from dateutil.parser import parse
import matplotlib.dates as mdates
from dateutil.relativedelta import relativedelta

## The GSFLOW model is loaded as follows
control_file = r"C:\Users\rniswon\Documents\Data\Git\Carson-prms-models.git\East_Fork\scenarios\historical (1980-2015)\eastfork_clim2_hist.control"
gs = gsflow.GsflowModel.load_from_file(control_file)
#gs = Gsflow(control_file=control_file)

#ssmax = gs.prms.parameters.get_values('soil_moist_max')
nrows = 332
ncols = 217
#hru_type = gs.prms.parameters.get_values('hru_type')
#hru_subbasin = gs.prms.parameters.get_values('hru_subbasin')  #gets as a vector
#sat_threshold = gs.prms.parameters.get_values('sat_threshold')
#soil_moist_max = gs.prms.parameters.get_values('soil_moist_max')
#mask = hru_type > 0
#dprst_depth_avg = np.zeros_like(dprst_depth_avg)  # set all values to zero
#plt.imshow(gs.prms.parameters.get_values('soil_moist_max').reshape(nrows,ncols))  #converts to grid
#plt.show()
#plt.imshow(gs.prms.parameters.get_values('hru_subbasin').reshape(nrows,ncols))  #converts to grid
#plt.show()
gs.gsflow_exe = os.path.join(os.path.abspath(r".\..\..\bin"), "gsflow.exe")
#The next line should be uncommented to rerun the model.
#gs.run_model()
#load PRMS output with simulated and measured streamflow
gs.prms.get_StatVar()
sim_stream_flow = gs.prms.stat.stat_df['basin_cfs_1'].values
meas_stream_flow = gs.prms.stat.stat_df['runoff_2'].values
# set dates for daily values
dates = []
for i in range(len(sim_stream_flow)):
    dates.append(datetime.date(1980, 10, 1)+datetime.timedelta(days=i))
fig, ax = plt.subplots(figsize=(20,8))
plt.xlabel("Time, in days")
plt.ylabel("Streamflow, in cfs")
X=dates
y=sim_stream_flow
z=meas_stream_flow
plt.plot(X, y, color='r', linewidth=2.5, label='simulated')
plt.plot(X, z, color='g', linewidth=2.5, label='measured')
plt.legend()
plt.show()
i=1