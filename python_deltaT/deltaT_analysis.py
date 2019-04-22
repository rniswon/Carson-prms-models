import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import shutil

# define T increments to temperature data of PRMS file
# Or, just specify a list, e.g., deltaT = [0, 2.5, 4.152]  
deltaT = np.arange(0, 4.5, 0.25).tolist()

# define a variable that later gets used to set the working directory path
# When working with the East Fork, set EFWF = 'EF'
# When working with the West Fork, set EFWF = 'WF'
EFWF = 'EF'

# Original delta T analysis location (on Eric's machine only)
# wdir=r'D:\EDM_LT\Carson\East_Fork_Delta_Temperature_Analysis_for_WftS'
# 
# Set a new working directory ("wdir") 
wdir = r'D:\EDM_LT\GitHub\Carson-prms-models.git\python_deltaT'


# Found this on the internet for quickly ripping through the PRMS output file
def tokenizer(fname):
    with open(fname) as f:
        chunk = []
        for line in f:
            if 'Basin weekly mean:' in line:
                continue
            if '####' in line:
                yield chunk
                chunk = []
                continue
            
            chunk.append(line)


# Incorporating delta T analysis directly on the repo
# bmdir: "base model directory"
if EFWF=='EF':
    bmdir = r'D:\EDM_LT\GitHub\Carson-prms-models.git\East_Fork\scenarios\historical (1980-2015)'
elif EFWF=='WF':
    bmdir = r'D:\EDM_LT\GitHub\Carson-prms-models.git\West_Fork\scenarios\historical (1980-2015)'

os.chdir(wdir)

# Make a copy of the executable to the directory that is going to be repeatedly copied
# (if it doesn't already exist there)

if not os.path.isfile(os.path.join(bmdir,'gsflow.exe')):
    # If the file doesn't yet exist in this location, bring a copy in
    shutil.copy(os.path.join(wdir,'..','Model Archive','bin','gsflow.exe'), bmdir)

for dT in deltaT:

    # Create a new directory
    directory = os.path.join(os.getcwd(),EFWF,'temp_' + str(dT))
    if os.path.exists(directory):
        os.rmtree(directory)

    # Copy the needed files to the new directory
    shutil.copytree(bmdir, directory)

    os.chdir(directory)
    if EFWF=='EF':
        ogname='upper_carson_climate_2.data'  # original name
        bname='upper_carson_climate_2'   
        control_file='eastfork_clim2_hist.control'
    elif EFWF=='WF':
        ogname='upper_carson_climate_2.data'  # currently both CR forks have same name, but could change
        bname='upper_carson_climate_2'
        control_file='westfork_clim2.control'

    # get original data
    with open(os.path.join(os.getcwd(), ogname),'r') as f:
        lines=f.readlines()

    # header data
    nhead=0
    while '##' not in lines[nhead]:
        nhead=nhead+1

    # get variable columns
    cols=[]
    curcol=5 #first 6 are dates
    for n in range(0,nhead):
        data=lines[n].strip().split()
        if len(data)==2:   # get variable names and number of columns
            try:
                if data[0]=='tmax' or data[0]=='tmin':
                    for j in range(0,int(data[1])):
                        curcol = curcol + 1
                        if curcol not in cols:
                            cols.append(curcol)
                else:
                    curcol=curcol + int(data[1])
                    print(curcol,data)
            except:
                print('illegal input')

    inc = dT

    nfname = bname + '_' + str(inc) + '.data'                 # new input file name = "nfname"
    with open(os.path.join(os.getcwd(), nfname),'w+') as nf:  # parse and copy header
        for n in range(0,nhead):
            nf.write(lines[n])     # echo header lines to new file
        for nl in lines[n+1:]:
            data=nl.strip().split()
            for c,d in enumerate(data):
                if c in cols and d != '-999':
                    par = float(d) + (inc * (9/5))
                    nf.write('%10s ' %str(par))
                else:
                    nf.write('%10s ' %d)
            nf.write('\n')

    # In order to stick with the name in the control file, delete the old and rename the new to the old
    ofname = ogname
    os.remove(ofname)
    os.rename(nfname, ofname)

    # Execute the model
    # -----------------
    # The original cmd for the original delta T runs on Eric's machine:
    # os.system('prmsIV.exe eastfork_hist_temp_inc.control')
    
    # For running the model now, get a copy of the gsflow.exe and place it in the current working directory
    # -----------------------------------------------------------------------------------------------------
    os.system('gsflow.exe ' + control_file)

    print("loading ppt data...")
    ppt = [np.loadtxt(A) for A in tokenizer('hru_ppt.weekly')]
    print("loading rain data...")
    rain = [np.loadtxt(A) for A in tokenizer('hru_rain.weekly')]
    print("loading snow data...")
    snow = [np.loadtxt(A) for A in tokenizer('hru_snow.weekly')]
    print("finished loading output data...")

    print("converting output to np arrays in memory...")
    ppt = np.array(ppt)
    rain = np.array(rain)
    snow = np.array(snow)

    # open one of the output files and get the start date from the first line
    f = open('hru_ppt.weekly', 'r')
    first = True
    for line in f:
        if first:
            date_start = datetime.strptime(line[1:11], '%Y/%m/%d')
            first = False

        if 'Basin weekly mean:' in line:
            date_end = datetime.strptime(line[1:11], '%Y/%m/%d')

    f.close()

    df = pd.DataFrame(columns=['Date', 'basin_rain', 'basin_snow', 'basin_ppt'])

    df['Date'] = pd.date_range(date_start, date_end, freq='7D')
    df['basin_rain'] = rain.sum(axis=(1, 2))
    df['basin_snow'] = snow.sum(axis=(1, 2))
    df['basin_ppt'] = ppt.sum(axis=(1, 2))

    df.to_csv('delta_T_' + str(inc) + '_result.csv', float_format='%.3f')

    os.chdir(wdir)

