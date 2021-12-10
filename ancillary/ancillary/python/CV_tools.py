import pandas as pd
import datetime
import os


#from wr_et.py
def ts2df(nme,suffix,t0,rpath='',val='flow'):
    '''suck in ts file from gage files with suffix and nme in file name'''
    val=val.lower()
    for f in os.listdir(rpath):
        if suffix in f:
            if 'well' not in f and 'well' not in suffix:
                data=f.lower().replace(suffix,'').split('-')
                d=data[3:] #assumes 'CV-wes-8015trans-'
                if len(d)>=1:
                    if 'jobs' not in d:
                        wr=d[0].replace('obs','')
                    else:
                        wr=d[0]
                    for w in d[1:]:
                        wr=wr+'-'+w
                    site=wr
                    nwr=wr
            elif 'well' in f and 'well' in suffix:
                data=f.lower().replace(suffix,'').split('-')
                well=data[-1]
                d=data[3:-1] #assumes 'CV-wes-8015trans-'
                if len(d)>=1:
                    if 'jobs' not in d:
                        wr=d[0].replace('obs','')
                    else:
                        wr=d[0]
                    for w in d[1:]:
                        wr=wr+'-'+w
                    site=wr
                    nwr=site+'-'+well #add well back in
            else:
                nwr=''
            if nwr.lower()==nme.lower() or nwr.lower()==nme.lower()+'obs': #site name MUST be just before suffix
                ##wr=f.lower().replace(suffix,'').split('-')
                ##wr=wr[3:] #assumes 'CV-wes-8015trans-'
                ##nwr=wr[0].lower().replace('obs','')
                ##for w in wr[1:]:
                ##    nwr=nwr+'-'+w.lower()
                #print('reading site {} from {}'.format(nwr,f))
                with open(os.path.join(rpath,f),'r') as fil:
                    lines=fil.readlines()
                lcount=0
                for line in lines[0:10]:
                    dum=line.strip().split()
                    try:
                        a=[float(d) for d in dum] #fails for strings
                    except:
                        names=line.strip().replace('\"','').replace('DATA:','').split()
                        names=[n.lower() for n in names]
                        #print(names)
                        for i,name in enumerate(names):
                            if 'flow' in name:
                                names[i]='flow'
                        lcount=lcount+1
                df=pd.read_csv(os.path.join(rpath,f),delim_whitespace=True,quoting=3,skiprows=lcount,names=names)
                df['t0']=pd.to_datetime(t0)
                df['date']=df['t0']+pd.to_timedelta(df['time'],unit='D')
                #groupby to take care of '_rot' concats
                df.groupby('date').sum()
                df.set_index('date',inplace=True)
                df.drop(['t0'],axis=1,inplace=True)
                df['site']=site
                df['val']=df[val]
    return(df)
