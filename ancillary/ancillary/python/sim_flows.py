import pandas as pd
import datetime
import os
import CV_tools

t0=datetime.date(1979,7,2)
starttime=datetime.date(2000,9,25)
startobs=datetime.date(2000,9,25)+datetime.timedelta(days=7)
endobs=datetime.date(2005,10,3)

#need obs dates for consistent sampling
#gage obs
ssf=pd.read_csv(os.path.join('tsproc','CV-wes-8015trans-flows.ssf'),names=['ste','date','time','flow'],
                low_memory=False,delim_whitespace=True,comment='#')
ssf.head()

ssf['Datetime']=pd.to_datetime(ssf['date'])
mask=[o for o in ssf.index if ssf.loc[o,'Datetime'].date()>endobs or ssf.loc[o,'Datetime'].date()<startobs]
ssf.drop(mask,inplace=True)
ssf['year']=ssf['Datetime'].dt.strftime('%y')
ssf['month']=ssf['Datetime'].dt.strftime('%m')
ssf.head()

#missing data is an issue here.
#e.g. if half a month is missing, obs will be linear interp over period
stes=ssf.ste.unique()
sim={}
#get gage data
#interpolate gage to day
for ste in stes:
    print(ste)
    simdf=CV_tools.ts2df(ste,'.sgag',t0,'output')
    simflow=simdf.resample('D').fillna(method='backfill')#.interpolate('linear')
    #get stedf dates based on ssf, not resampled, already cropped to start and end
    stedf=ssf[ssf['ste']==ste]
    stedf.set_index('Datetime',inplace=True)
    dfyr=stedf.index.year.unique()
    for yr in list(dfyr):
        d8s=[s for s in stedf.index if s.date().year==yr]
        obsnme=ste+'_'+str(yr)[-2:]
        sim[obsnme]=[simflow.loc[d8s,'flow'].sum(),'avo']
        dfyrmo=list(set([s.month for s in d8s]))
        for mo in dfyrmo:
            d8s=[s for s in stedf.index if s.date().year==yr and s.date().month==mo]
            obsnme=ste+'_'+str(yr)[-2:].zfill(2)+str(mo).zfill(2)
            sim[obsnme]=[simflow.loc[d8s,'flow'].sum(),'mvo']


simdf=pd.DataFrame.from_dict(sim,orient='index',columns=['obsval','obgnme'])
simdf['obsnme']=simdf.index
simdf=simdf.reindex()
simdf.sort_values(by='obsnme',inplace=True)    
simdf.set_index('obsnme',inplace=True)




simdf.to_csv(os.path.join('output','sim_flows.txt'),sep=' ')