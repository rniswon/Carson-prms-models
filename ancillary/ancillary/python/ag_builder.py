#adjust paramters for supplemental pumping based on input file
#read in values from .sup, .irr, .irs files to dictionaries
#write new .irs, .irr, .sup, and demand tabs

import datetime
import os
import pandas as pd
import numpy as np

relpath=''
swfdir=os.path.join(os.getcwd(),'swf')
#read in parameters
infile='sup_irr_input.txt'
with open(infile,'r') as f:
    lines=f.readlines()
par={}
for l in lines:
    if l[0]!='#' and len(l)>1:
        data=l.strip().split('=')
        k=data[0]
        if len(data)==2:
            v=data[1]
            par[k]=v
        else:
            par[k]=[]
#convert control file to params
confile=par['confile']
with open(confile,'r') as f:
    lines=f.readlines()
for i,line in enumerate(lines):
    if 'start_time' in line:
        simstart=datetime.date(int(lines[i+3]),int(lines[i+4]),int(lines[i+5]))
    if 'end_time' in line:
        simend=datetime.date(int(lines[i+3]),int(lines[i+4]),int(lines[i+5]))
    if 'modflow_time_zero' in line:
        sp=[datetime.date(int(lines[i+3]),int(lines[i+4]),int(lines[i+5]))]
    if 'modflow_name' in line:
        namfile=lines[i+3].strip()

icellfracfile=par['icellfracfile']
irrfile=par['irrfile']
modnam=namfile.split('.nam')[0]
doystartirr=float(par['doystartirr'])-1
doyendirr=float(par['doyendirr'])-1
doystartsup=float(par['doystartsup'])-1
doyendsup=float(par['doyendsup'])-1
futurepmp=bool(par['futurepmp'])
regfile=par['regfile']
transwr=[p for p in par['transwr'].split(',') if p!='']
print('Future pumping: {}'.format(futurepmp))

#get mar pars if applicable
if 'MAR' in os.getcwd().split('\\')[-1]:
    cumflowmaron=float(par['cumflowmaron'])
    #where you can stick it
    marfile='MARwr.txt'
    marwr=pd.read_csv(marfile)
    marwr.index=marwr.wr
    marwrlist=marwr.index.tolist()
    trigfile=par['trigfile']
    print(os.getcwd())
    print('using {} to trigger MAR for {} WRs'.format(trigfile,len(marwrlist)))

else:
    print('NO MAR')
    trigfile=''
    marwrlist=[]

#get additional info via .nam
swgageunit=[]
wellgageunit=[]
swetunit=[]
welletunit=[]
dmdunit=[]
with open(namfile,'r') as f:
    lines=f.readlines()
for line in lines:
    if relpath in line:
        line=line.replace(relpath,'')
    data=line.strip().split()
    if data[0].lower()=='dis':
        disfile=data[2]
    if data[0].lower()=='uzf':
        uzffile=data[2]
    if data[0].lower()=='gage':
        gagfile=data[2]
    if data[0].lower()=='ag':
        agfile=data[2]
    #get demand tabfile names from .nam
    if len(data)==3 and 'demand' in data[-1]   :
        pt=data[-1].split('demand-')[-1].lower()
        wrpt=pt.split('-')[0:-2]
        if len(wrpt)>1:
            wr=str(wrpt[0])
            for i in wrpt[1:]:
                wr=wr+'-'+str(i)
        else:
            wr=str(wrpt[0])
        dmdunit.append((wr,data[-1],data[1]))
    #get swgag files from .nam
    if len(data)==3 and data[-1].endswith('.swgag'):
        wr=data[-1].split('CV-wes-8015trans-')[-1].replace('.swgag','').lower()
        swgageunit.append((wr,data[-1],data[1]))
    #get wellgag files from .nam
    if len(data)==3 and data[-1].endswith('.wellgag'):
        junk=data[-1].split('CV-wes-8015trans-')[-1].replace('.wellgag','')
        if len(junk.split('-'))==3:
            wr=junk.split('-')[0]+'-'+junk.split('-')[2].lower()
            well=junk.split('-')[1].lower()
        elif len(junk.split('-'))==2:
            wr=junk.split('-')[0].lower()
            well=junk.split('-')[1].lower()
        else:
            donkey=derp
        wellgageunit.append((wr,well,data[-1],data[1]))
    if len(data)==3 and data[-1].endswith('.swet'):
        wr=data[-1].split('CV-wes-8015trans-')[-1].replace('.swet','').lower()
        swetunit.append((wr,data[-1],data[1]))
    #get wellgag files from .nam
    if len(data)==3 and data[-1].endswith('.wellet'):
        junk=data[-1].split('CV-wes-8015trans-')[-1].replace('.wellet','')
        if len(junk.split('-'))==3: #actually, no WR-WR have sup wells, so superfluous
            wr=junk.split('-')[0]+'-'+junk.split('-')[2].lower()
            well=junk.split('-')[1].lower()
        elif len(junk.split('-'))==2:
            wr=junk.split('-')[0].lower()
            well=junk.split('-')[1].lower()
        else:
            donkey=derp
        welletunit.append((wr,well,data[-1],data[1]))


#read in wr data
fname=irrfile
print('reading wr data from {}'.format(fname))
with open(fname,'r') as f:
    lines=f.readlines()
wr_dict={}
sup_dict={}
rnd=5
for line in lines:
    if '#' in line:
        header=line.replace('#','').strip().split()
    else:
        data=line.strip().split()
        if len(data)>0:
            wr=data[header.index('WRname')].lower()
            if wr not in wr_dict:
                wr_dict[wr]={}
            wr_dict[wr]['iseg']=int(data[header.index('iseg')])
            wr_dict[wr]['dpt']=round(float(data[header.index('dpt')]),rnd)
            # irrigation rates
            wr_dict[wr]['swu']=round(float(data[header.index('swu')]),rnd)
            wr_dict[wr]['swufrac']=round(float(data[header.index('swufrac')]),rnd)
            wr_dict[wr]['swr']=round(wr_dict[wr]['swu']*wr_dict[wr]['swufrac'],rnd)
            # irrigation efficiencies
            wr_dict[wr]['swfr']=round(float(data[header.index('swfr')]),rnd)
            wr_dict[wr]['swfrfrac']=round(float(data[header.index('swfrfrac')]),rnd)
            wr_dict[wr]['swfu']=round(wr_dict[wr]['swfr']*wr_dict[wr]['swfrfrac'],rnd)

            if data[header.index('wellnum')]!='NA':
                # python weirdness, can't pass str rep of float to int, but this works
                wellnum=int(float(data[header.index('wellnum')]))
                if wr not in sup_dict: #supnum, fracsupmax, pmp trust these values are appended in order?
                    sup_dict[wr]={}
                if wellnum not in sup_dict[wr]:
                    sup_dict[wr][wellnum]={'fracsupmax':(float(data[header.index('pctsup')]),data[header.index('realwell')].replace('APP-','').lower()),
                        'wellpos':(data[header.index('wellrow')],data[header.index('wellcol')],data[header.index('welllay')]),
                        'startyr':int(float(data[header.index('startyr')])),
                        'welleff':float(data[header.index('welleff')])}


# not dealing with rot for now
# for west fork rotation
wrrot=[('478-481', u'CA'), ('487', u'CA'), ('488-490', u'CA'), ('491', u'CA'),
        ('492-501', u'CA'), ('502-507', u'CA'), ('508', u'CA'), ('509-510', u'CA'),
        ('511', u'CA'), ('512', u'CA'), ('513-514', u'CA'), ('515', u'CA'), ('516-517', u'CA'),
        ('517A', u'CA'), ('518-519', u'CA'), ('520-522', u'CA'), ('523-527', u'CA'), ('528', u'CA'),
        ('529-531', u'CA'), ('532-533', u'CA'), ('534', u'CA'), ('535-536', u'CA'), ('537', u'NV'),
        ('537_rot', u'NV'), ('538', u'NV'), ('538_rot', u'NV'), ('539', u'NV'), ('539_rot', u'NV'),
        ('540', u'NV'), ('540A', u'NV'), ('540A_rot', u'NV'), ('540_rot', u'NV'), ('542', u'NV'),
        ('542_rot', u'NV'), ('543', u'NV'), ('543_rot', u'NV'), ('544', u'NV'), ('544_rot', u'NV'),
        ('545', u'NV'), ('545_rot', u'NV'), ('546', u'NV'), ('546_rot', u'NV'), ('553', u'NV'),
        ('553_rot', u'NV'), ('554', u'NV'), ('554_rot', u'NV'), ('555', u'NV'), ('555_rot', u'NV'),
        ('556', u'NV'), ('556_rot', u'NV'), ('557', u'NV'), ('557_rot', u'NV'), ('558', u'NV'),
        ('558_rot', u'NV'), ('559', u'NV'), ('559_rot', u'NV'), ('560', u'NV'), ('560_rot', u'NV'),
        ('561', u'NV'), ('561_rot', u'NV'), ('562', u'NV'), ('562_rot', u'NV'), ('563', u'NV'),
        ('563_rot', u'NV'), ('564', u'NV'), ('564_rot', u'NV'), ('565', u'NV'), ('565_rot', u'NV'),
        ('566', u'NV'), ('566_rot', u'NV'), ('567', u'NV'), ('567_rot', u'NV'), ('568', u'NV'),
        ('568_rot', u'NV'), ('578', u'NV'), ('578_rot', u'NV'), ('604', u'NV'), ('604_rot', u'NV')]
for wr in wrrot:
    try:
        wr_dict[wr[0].lower()]['rot']=wr[1]
    except:
        pass






#read in sp from dis
fname=disfile
with open(fname,'r') as f:
    lines=f.readlines()
for line in lines:
    if 'sp=' in line: #assume sufficient to identify stress period, date as last entry
        data=line.strip().split()
        d8=data[-1].split('-')
        sp.append(datetime.date(int(d8[0]),int(d8[1]),int(d8[2])))


# cell frac in pandas
celldf=pd.read_csv(os.path.join('Carson_Valley',icellfracfile))
celldf.columns=celldf.columns.str.lower()
celldf.wrname=celldf.wrname.str.lower()
celldf['row']=celldf['row']-1
celldf['col']=celldf['col']-1
for wr in wr_dict:
    wrbase=wr.replace('_rot','')
    wr_dict[wr]['acres']=celldf.loc[celldf['wrname']==wrbase,'wr_acres'].mean()

def make_pctarr(wr_dict,celldf):
    for wr in wr_dict:
        if 'rot' not in wr:
            pctarr=np.zeros((258,206))
            rows=tuple(celldf.loc[celldf['wrname']==wr,'row'].map(int))
            cols=tuple(celldf.loc[celldf['wrname']==wr,'col'].map(int))
            pcts=tuple(celldf.loc[celldf['wrname']==wr,'wr_frac'])
            if (len(rows)==0 or len(cols)==0 or len(pcts)==0):
                print ('{} has no cell data'.format(wr))
            pctarr[rows,cols]=pcts
            np.savetxt('Carson_Valley/arrays/wrarr/'+str(wr)+'-location.arr',pctarr,fmt='%.5g')
    return()
if not os.path.exists('Carson_Valley/arrays/wrarr'):
    os.mkdir('Carson_Valley/arrays/wrarr')
make_pctarr(wr_dict,celldf)

def get_finf(fname,wr_dict):
    pctarr={}
    pctmask={}
    #read uzf file, read finf arrays and finf_fact, determine ET from pcp for each WR
    print('reading finf arrays, calculating ET from precip')
    wrpcpmltdf=pd.DataFrame([[wr,wr_dict[wr]['dpt']] for wr in wr_dict],columns=['wrname','dpt'])
    wrpcpmltdf.index=wrpcpmltdf.wrname
    #finf data from uzf
    with open(fname,'r') as f:
        lines=f.readlines()

    for wr in wr_dict:
        wrbase=wr.replace('_rot','')
        pctarr[wr]=np.loadtxt('Carson_Valley/arrays/wrarr/'+str(wrbase)+'-location.arr')
        pctmask[wr]=np.where(pctarr[wr]>0,1,np.nan)

    for line in lines:
        if '.finf' in line.lower() and 'sp00' not in line.lower():
            data=line.strip().split()
            fname=data[1]
            finf_fact=float(data[2])
            dum=fname.split('-')
            sptxt=[d for d in dum if 'sp' in d]
            s=int(sptxt[0].split('sp')[-1])
            if simstart<=sp[s]<=simend:
                pcparr=np.loadtxt(fname)/1000
                print(fname)
                for wr in wr_dict:
                    #pctarr=np.loadtxt('arrays/wrarr/'+str(wrbase)+'-location.arr')
                    if np.any(pctarr[wr]>0):
                        pcpsp=np.nanmean(pctmask[wr]*pcparr) #take mean precip depth of any cells within WR, this is L/T no need for percent cell (see below)
                    else:
                        pcpsp=0
                        #print('{} has no cells or no precip in {}'.format(wr,s))
                    wrpcpmltdf.loc[wr,'pcp_'+str(s)]=pcpsp #need for pmult calc

                    pcpetsp=round(np.multiply(pcparr,pctarr[wr]).sum()*(1-finf_fact*1000)*550*550,rnd) #finf_fact goes into GW, 1-finf_fact is ET, sum for all WR cell fractions, convert to cfd
                    wrpcpmltdf.loc[wr,'pcpet_'+str(s)]=pcpetsp
    #write precip and et to file for post-proc
    for wr in wr_dict:
        pcp=[]
        if not os.path.exists('pcpet'):
            os.mkdir('pcpet')
        pcpout=r'pcpet/CV-wes-8015trans-'+wr.lower()+'.pcpet'
        for s in range(sp.index(simstart),sp.index(simend)+1):
            c='pcpet_'+str(s)
            if c in wrpcpmltdf.columns:
                pcpet=round(float(wrpcpmltdf.loc[wrpcpmltdf['wrname']==wr,'pcpet_'+str(s)]),5)
            else:
                pcpet=0
            pcp.append([(sp[s]-sp[0]).days,s,pcpet])
        df=pd.DataFrame(pcp,columns=['TIME','KPER','ETpcp'])
        df.sort_values(by='TIME',inplace=True)
        df.to_csv(pcpout,sep=' ',index=False)

    #linear function for demand multiplier based on demand precip threshold (dpt) parameter and precip (pcp
    for c in [pmc for pmc in wrpcpmltdf.columns if 'pcp_' in pmc]:
        newcol=c.replace('pcp_','pmlt_')
        wrpcpmltdf['extra']=(-1/wrpcpmltdf['dpt'])*wrpcpmltdf[c]+1
        wrpcpmltdf[newcol]=np.where(wrpcpmltdf['extra']>0,wrpcpmltdf['extra'],0)
    wrpcpmltdf.to_csv('wrpcpmltdf.csv')
    return(wrpcpmltdf)

def get_flows(fname):
    #flow ts in pandas to determine demand/irrigation/mar rates
    efflow=[]
    print('reading flows from {}'.format(fname))
    df=pd.read_csv(fname,delim_whitespace=True,names=['simdays','flow'])
    df['start']=pd.to_datetime(sp[0])
    df['date']=df['start']+pd.to_timedelta(df['simdays'],unit='D')
    df['date']=pd.to_datetime(df['date'])
    df.set_index('date',inplace=True)
    df.resample('D').interpolate('linear',inplace=True)
    df.drop(['simdays','start'],inplace=True,axis=1)
    return(df)


def irrate_sp(wr,df,wrpcpmltdf,sp,pmltbool=True):
    #calc irrate for each sp, adjust for precip
    ratelist=[[0,sp[0],0]]
    efflist=[[0,sp[0],0]]
    for i in range(sp.index(simstart)+1,sp.index(simend)+1):
        if 'pmlt_'+str(i) in wrpcpmltdf.columns and pmltbool==True:
            mlt=wrpcpmltdf.loc[wr,'pmlt_'+str(i)]
        else:
            mlt=1.0
        #consolidate into sp data
        ratelist.append([(sp[i-1]-sp[0]).days+1,sp[i-1]+datetime.timedelta(days=1),df[sp[i-1]+datetime.timedelta(days=1):sp[i]]['irrate'].mean()*mlt])
        ratelist.append([(sp[i]-sp[0]).days,sp[i],df[sp[i-1]+datetime.timedelta(days=1):sp[i]]['irrate'].mean()*mlt])
        efflist.append([(sp[i-1]-sp[0]).days+1,sp[i-1]+datetime.timedelta(days=1),df[sp[i-1]+datetime.timedelta(days=1):sp[i]]['swf'].mean()*mlt])
        efflist.append([(sp[i]-sp[0]).days,sp[i],df[sp[i-1]+datetime.timedelta(days=1):sp[i]]['swf'].mean()*mlt])
    return(ratelist,efflist)

def calc_irrate(regdf,wr_dict,wrpcpmltdf,marwrlist="",trigfile="",cumflowmaron=0):
    #calc irrate for every day in pandas based on ef flows
    print('calculating irrigation rates and efficiency factors')
    df=regdf.copy(deep=True)
    df['month']=df.index.month
    df['irr']=1
    df['irr'].where((df['month']>=4) & (df['month']<=9),0,inplace=True)# & (df['month']<=9) #& is bitwise operator in pandas, paren needed
    df['reg']=1
    df['reg'].where(df['flow']<=200*86400,0,inplace=True)
    #calc irrates, reg and unreg, adjust for precip
    if 'MAR' in os.getcwd().split('\\')[-1]:
        trigdf=get_flows(trigfile)
    for wr in sorted(list(wr_dict.keys())):
        df['rot']=df['irr'] #all on for non-rot WR
        df['irrate']=0
        # do WF rotational
        if 'rot' in wr_dict[wr]:
            for divyear in range(simstart.year,simend.year+1):
                for rotmo in [4,5,6,7,8,9]:
                    lastday=datetime.date(divyear,rotmo+1,1)-datetime.timedelta(days=1)
                    if wr_dict[wr]['rot']=='CA':
                        df.loc[datetime.date(divyear,rotmo,8):datetime.date(divyear,rotmo,15),'rot']=0 #8 days
                        df.loc[datetime.date(divyear,rotmo,24):lastday,'rot']=0 #7 or 8 days
                    elif wr_dict[wr]['rot']=='NV':
                        if 'rot' in wr: #jr WR, leave on when CA on, turn off when CA off
                            df.loc[datetime.date(divyear,rotmo,8):datetime.date(divyear,rotmo,15),'rot']=0 #8 days
                            df.loc[datetime.date(divyear,rotmo,24):lastday,'rot']=0 #7 or 8 days
                        else: # senior WR turn off when CA is on
                            df.loc[datetime.date(divyear,rotmo,1):datetime.date(divyear,rotmo,7),'rot']=0 #7 days
                            df.loc[datetime.date(divyear,rotmo,16):datetime.date(divyear,rotmo,23),'rot']=0 # 8 days
        df.loc[df['reg']==1,'irrate']=df['rot'] * df['irr'] * df['reg'] * wr_dict[wr]['swr'] * wr_dict[wr]['acres']*43560
        df.loc[df['reg']==0,'irrate']=df['rot'] * df['irr'] * wr_dict[wr]['swu'] * wr_dict[wr]['acres']*43560
        df.loc[df['reg']==1,'swf']=df['rot'] * df['irr'] * df['reg'] * wr_dict[wr]['swfr']
        df.loc[df['reg']==0,'swf']=df['rot'] * df['irr'] * wr_dict[wr]['swfu']
        df['irrate'].fillna(value=0,inplace=True)
        df['swf'].fillna(value=0,inplace=True)

        #calc irrate for each sp, adjust for precip
        ratelist,efflist=irrate_sp(wr,df,wrpcpmltdf,sp)
        sprdf=pd.DataFrame(ratelist,columns=['simday','date','irrate'])
        sprdf.set_index('date',inplace=True)
        sprdf.sort_index(inplace=True)
        wr_dict[wr]['irrate']=sprdf
        spfdf=pd.DataFrame(efflist,columns=['simday','date','swf'])
        spfdf.set_index('date',inplace=True)
        spfdf.sort_index(inplace=True)
        wr_dict[wr]['swf']=spfdf
        if 'MAR' in os.getcwd().split('\\')[-1] and wr in marwrlist:
            print('doing MAR')
            wr_dict=calc_mar(wr,wr_dict,marwrlist,trigdf,cumflowmaron)
        write_dmd(wr,wr_dict[wr]['irrate'],dmdunit)
        write_swf(wr,wr_dict[wr]['swf'],swfdir)
    return(wr_dict)

def ag2muni(wr_dict,transwr,celldf):
    wrlist=[w.lower() for w in transwr]
    dmd=float(par['demand'])
    swf=float(par['efficiency'])
    effname=par['effname'].lower()
    for wr in wrlist:
        print('Transfering WR from {} to muni with demand {}.'.format(wr,round(dmd,4)))
        print('Resulting effluent applied to {} with efficiency {}.'.format(effname,round(swf,4)))
        #relatively simple irrate and swf: 40,40,20 for April,May,June
        df=wr_dict[wr]['irrate'].copy(deep=True)
        df['month']=df.index.month
        df['irr']=0
        df['irr'].where((df['month']!=4),0.4/30,inplace=True)
        df['irr'].where((df['month']!=5),0.4/31,inplace=True)
        df['irr'].where((df['month']!=6),0.2/30,inplace=True)
        df['irrate']=df['irr'] * dmd * wr_dict[wr]['acres']*43560
        df['irrate'].fillna(value=0,inplace=True)
        df['sw']=0
        df['sw'].where((df['month']!=4) & (df['month']!=5) & (df['month']!=6),1,inplace=True)
        df['swf']= df['sw'] * swf
        df['swf'].fillna(value=0,inplace=True)
        ratelist,efflist=irrate_sp(wr,df,wrpcpmltdf,sp,pmltbool=False)
        sprdf=pd.DataFrame(ratelist,columns=['simday','date','irrate'])
        sprdf.set_index('date',inplace=True)
        sprdf.sort_index(inplace=True)
        wr_dict[wr]['irrate']=sprdf
        spfdf=pd.DataFrame(efflist,columns=['simday','date','swf'])
        spfdf.set_index('date',inplace=True)
        spfdf.sort_index(inplace=True)
        wr_dict[wr]['swf']=spfdf
        write_dmd(wr,wr_dict[wr]['irrate'],dmdunit)
        write_swf(wr,wr_dict[wr]['swf'],swfdir)

        #update where effluent goes
        didx=[c for c in celldf.index if celldf.loc[c,'wrname']==wr]
        celldf.drop(didx,inplace=True)
        aidx=[c for c in celldf.index if celldf.loc[c,'wrname'].lower()==effname]
        temp=celldf.loc[aidx,:].copy(deep=True)
        temp['wrname']=wr
        celldf=celldf.append(temp,sort=True,ignore_index=True)
    return(wr_dict,celldf)



def calc_mar(wr,wr_dict,marwrlist,trigdf,cumflowmaron):
    #Flow value triggers for MAR
    #divides flow among all mar acres
    print('calculating MAR rates for {}'.format(wr))
    marlist=[]
    df=trigdf.copy(deep=True)
    #turn on mar after cumflowmaron met between [Oct and April)
    df['marcum']=0
    for yr in range(simstart.year+1,simend.year+1):
        marstart=datetime.date(yr-1,10,1)
        marend=datetime.date(yr,3,31)
        marts=df[marstart:marend].flow.cumsum()
        df['marcum']=marts.add(df['marcum'],fill_value=0)
    df['mar']=0
    df['mar'].where(df.marcum<cumflowmaron,1,inplace=True)
    #set to all flow once cumflowmaron reached, divide by total acres
    marrate=(df['flow']*df['mar'])/sum([wr_dict[w]['acres'] for w in marwrlist]) #cfd/acre
    #consolidate into sp data
    for i in range(sp.index(simstart)+1,sp.index(simend)+1):
        marlist.append([(sp[i-1]-sp[0]).days+1,sp[i-1]+datetime.timedelta(days=1),marrate[sp[i-1]+datetime.timedelta(days=1):sp[i]].mean()])
        marlist.append([(sp[i]-sp[0]).days,sp[i],marrate[sp[i-1]+datetime.timedelta(days=1):sp[i]].mean()])
    marrate=pd.DataFrame(marlist,columns=['simday','date','irrate'])
    marrate.set_index('date',inplace=True)
    #add to irrate
    wr_dict[wr]['irrate']['irrate']=wr_dict[wr]['irrate']['irrate'].add(wr_dict[wr]['acres']*marrate['irrate'],fill_value=0)
    #impose min
    wr_dict[wr]['irrate']['irrate']=wr_dict[wr]['irrate']['irrate'].apply(lambda x: min(x,wr_dict[wr]['swu']*wr_dict[wr]['acres']*43560))
    return(wr_dict)

def write_dmd(wr,sprdf,dmdunit):
    #write demand tabfiles
    print('writing demand files for {}'.format(wr))
    dum=[]
    fname=[r[1] for r in dmdunit if wr.lower()==r[0].lower()][0]
    df=sprdf.copy(deep=True)
    df['date']='# '+df.index.map(str)
    df.set_index('simday',inplace=True)
    dmax=int(max(df.index))
    for i in range(1,5001-len(df)):
        dum.append(['# '+str(sp[0]+datetime.timedelta(days=dmax+i)),0,dmax+i])
    dumdf=pd.DataFrame(dum,columns=['date','irrate','simday'])
    dumdf.set_index('simday',inplace=True)
    df=df.append(dumdf,sort=True)
    df.to_csv(fname,sep=' ',columns=['irrate','date'],header=False,quotechar=' ')
    return()

def read_irrate(wr_dict,dmdunit):
    print('reading irrigation rates')
    for wr in wr_dict:
        for dmd in [d for d in dmdunit if d[0]==wr]:
            wr_dict[wr]['irrate']=pd.read_csv(dmd[1],delim_whitespace=True,index_col=0,usecols=[0,1,3],names=['simday','irrate','date'])
            wr_dict[wr]['irrate'].set_index(pd.to_datetime(wr_dict[wr]['irrate']['date']),inplace=True)
    return(wr_dict)

def write_swf(wr,sprdf,swfdir):
    #write swf tabfiles
    if not os.path.exists(swfdir):
        os.mkdir(swfdir)
    print('writing swf files for {}'.format(wr))
    dum=[]
    fname='swf-'+wr+'.txt'
    df=sprdf.copy(deep=True)
    df['date']='# '+df.index.map(str)
    df.set_index('simday',inplace=True)
    dmax=int(max(df.index))
    for i in range(1,5001-len(df)):
        dum.append(['# '+str(sp[0]+datetime.timedelta(days=dmax+i)),0,dmax+i])
    dumdf=pd.DataFrame(dum,columns=['date','swf','simday'])
    dumdf.set_index('simday',inplace=True)
    df=df.append(dumdf,sort=True)
    df.to_csv(os.path.join(swfdir,fname),sep=' ',columns=['swf','date'],header=False,quotechar=' ')
    return()

def read_swf(wr_dict,swfdir):
    print('reading surface water efficiencies')
    for wr in wr_dict:
        for f in os.listdir(swfdir):
            if f=='swf-'+wr+'.txt':
                wr_dict[wr]['swf']=pd.read_csv(os.path.join(swfdir,f),delim_whitespace=True,index_col=0,usecols=[0,1,3],names=['simday','swf','date'])
                wr_dict[wr]['swf'].set_index(pd.to_datetime(wr_dict[wr]['swf']['date']),inplace=True)
    return(wr_dict)

def write_ag(agfile,wr_dict,sup_dict):
    #write .ag file
    #keeping all wells as supplemental, even gwonly that iupseg from ghost
    print('writing '+agfile+' file\n')
    sups=[]
    for wr in sup_dict:
        for w in sup_dict[wr]:
            sups.append(w)
    supsort=sorted(list(set(sups))) #supplemental wells
    wrsupsort=sorted(list(set(sup_dict.keys()))) #wr with sup
    wrsort=sorted(list(set(wr_dict.keys()))) #wr
    wrsortnorot=sorted(list(set([w for w in wrsort if '_rot' not in w and w+'_rot' not in wrsort])))
    with open(agfile,'w+') as f:
        f.write('# AG options\noptions\n')
        f.write('irrigation_diversion '+str(len(wr_dict))+' '+str(max([len(celldf.loc[celldf['wrname']==wr,'wr_acres']) for wr in wrsort]))+'\n')
        f.write('supplemental_well '+str(len(supsort))+' 1\n')
        f.write('irrigation_well '+str(len(supsort))+' '+str(max([len(celldf.loc[celldf['wrname']==wr,'wr_acres']) for wr in wrsupsort]))+'\n')
        f.write('maxwells '+str(len(supsort))+'\n')
        f.write('timeseries_diversion\n')# '+str(len(swgageunit))+'\n')
        f.write('timeseries_well\n')# '+str(len(gwgageunit))+'\n')
        f.write('timeseries_diversionet\n')# '+str(len(swgageunit))+'\n')
        f.write('timeseries_wellet\n')# '+str(len(gwgageunit))+'\n')
        f.write('welllist  11\n')
        f.write('end\n')

        #output option
        f.write('# ag time series: DIVERSION seg/wellnum fileunit\n')
        f.write('time series\n')
        for wr in wrsort:
            for sw in sorted(swgageunit):
                if wr==sw[0]:
                    f.write('DIVERSION '+str(wr_dict[wr]['iseg'])+' '+str(sw[2])+'\n')
        for wr in wrsort:
            for sw in sorted(swetunit):
                if wr==sw[0]:
                    f.write('DIVERSIONET '+str(wr_dict[wr]['iseg'])+' '+str(sw[2])+'\n')
        for wr in wrsupsort:
            for well in sorted(wellgageunit):
                if well[0]==wr:
                    for wellnum in sorted(sup_dict[wr]):
                        if sup_dict[wr][wellnum]['fracsupmax'][1]==well[1]:
                            f.write('WELL '+str(wellnum)+' '+str(well[3])+'\n')
        for wr in wrsupsort:
            for well in sorted(welletunit):
                if well[0]==wr:
                    for wellnum in sup_dict[wr]:
                        if sup_dict[wr][wellnum]['fracsupmax'][1]==well[1]:
                            f.write('WELLET '+str(wellnum)+' '+str(well[3])+'\n')
        f.write('END\n')

        #segment list, segs used for irrigation, new 6/23/2019
        f.write('SEGMENT LIST\n')
        for wr in wrsort:
            f.write(str(wr_dict[wr]['iseg'])+'  # segment used for irritaiton of '+str(wr)+'\n')
        f.write('END\n')


        #well list, supplemental wells go here, not in .wel package
        #order is implicit so do by supsort
        f.write('WELL LIST\n')
        for wellnum in supsort:
            for wr in wrsupsort:
                if wellnum in sup_dict[wr]:
                    maxpmp=-round(celldf.loc[celldf['wrname']==wr,'wr_acres'].mean()*9.0*43560/(doyendsup-doystartsup),4)
                    pos=sup_dict[wr][wellnum]['wellpos']
                    f.write(pos[2]+' '+pos[0]+' '+pos[1]+' '+str(maxpmp)+'  # well number '+str(wellnum)+', aka '+str(sup_dict[wr][wellnum]['fracsupmax'][1])+' for '+str(wr)+'\n')
        f.write('END\n')


        #stress period data
        irrsfr=0
        marsfr=0
        irrwell=0
        effmar=0.1 #10% efficiency (ET) for winter MAR
        for ss,d in enumerate(sp[1:]): # derp, index s is offset, sp[s]!=d
            s=ss+1
            yr=d.year



            #
            #simstart<=d should cause stress period block irrsfr=0 for 2000-09-18
            #but still getting partial .ag file with 0 values in 2000-09-18 on cluster,
            #says 2000-09-18 not in index
            #Not getting anything here, because 1995-09-25<=simstart

            #also, this crap is writing "STRESS PERIOD  0 # stress period 1979-07-02
            #should be skipping since enumerate(sp[1:])


            if simstart<d<=simend:
                if 'MAR' in os.getcwd().split('\\')[-1]: #MAR
                    if marsfr==0: #turn mar on from the start
                        marsfr=len(marwr.index)
                    else: #leave mar as it was
                        marsfr=-1
                if (datetime.date(yr,1,1)+datetime.timedelta(days=doystartirr))<d<=(datetime.date(yr,1,1)+datetime.timedelta(days=doyendirr)): #irrigation season
                    marsfr=0 #turn off mar
                    if irrsfr==0:
                        irrsfr=len(wr_dict) #turn irrigaiton on
                    else: #check if previous swf same as current
                        irrsfr=len(wr_dict) #default write new entry
                        for wr in wrsort:
                            peff=wr_dict[wr]['swf'].loc[sp[s-1],'swf']#previous efficiency
                            ceff=wr_dict[wr]['swf'].loc[sp[s],'swf']#current efficiency
                            if peff==ceff:
                                irrsfr=-1
                                #Implement the following for the next calibration
                                #final WftS calibration used previous based on swf for watercan only
##                    else: #check if previous swf same as current
##                        irrsfr=len(wr_dict) #default write new entry
##                        bools=[]
##                        for wr in wrsortnorot:
##                            peff=wr_dict[wr]['swf'].loc[sp[s-1],'swf']#previous efficiency
##                            ceff=wr_dict[wr]['swf'].loc[sp[s],'swf']#current efficiency
##                            if peff==ceff:
##                                irrsfr=-1
##                                bools.append(wr)
##                        if len(bools)==len(wrsortnorot): #all efficiencies (except _rot) are the same
##                            irrsfr=-1 #use previous sp info
                else:
                    irrsfr=0 #turn off irrigation
                #sup pmp
                if (datetime.date(yr,1,1)+datetime.timedelta(days=doystartsup))<d<=(datetime.date(yr,1,1)+datetime.timedelta(days=doyendsup)):
                    if irrwell==0:
                        irrwell=len(supsort)
                    else:
                        irrwell=-1
                else:
                    irrwell=0
            else:
                marsfr=0
                irrsfr=0
                irrwell=0

            f.write('STRESS PERIOD  '+str(s)+' # stress period '+str(sp[s])+'\n')
            f.write('IRRDIVERSION\n')
            #irr and diversions
            if irrsfr>0: #irrsfr has priority to get all wr
                f.write(str(irrsfr)+' #NUMIRRSEGSP\n')
                for wr in wrsort:
                    basewr=wr.replace('_rot','')
                    f.write(str(wr_dict[wr]['iseg'])+' '+str(len(celldf.loc[celldf['wrname']==basewr,'wr_frac']))+' ')#old line, see 2n part of new below #SEGID NUMCELLSEG\n')
                    # new pars, see input_instructions_AG.docx
                    f.write('0.0 0.0 #SEGID NUMCELLSEG IRRPERIODSEG TRIGGERFACTSEG\n')
                    for i,(r,c,p) in enumerate(zip(celldf.loc[celldf['wrname']==basewr,'row'].tolist(),celldf.loc[celldf['wrname']==basewr,'col'].tolist(),celldf.loc[celldf['wrname']==basewr,'wr_frac'].tolist())):
                        if i==0:
                            com=' #IRRROW IRRCOL EFF_FACT FIELD_FACT'
                        else:
                            com=''
                        f.write(str(int(r))+' '+str(int(c))+' '+str(round(wr_dict[wr]['swf'].loc[sp[s],'swf'],4))+' '+str(round(p,4))+com+'\n')
            elif irrsfr<0:
                f.write(str(irrsfr)+' #NUMIRRSEGSP cont regular irr\n')
            else:
                if marsfr>0: #second priority is turning on mar
                    f.write(str(marsfr)+' #NUMIRRSEGSP mar\n')
                    for wr in marwr.index: #already sorted
                        basewr=wr.replace('_rot','')
                        f.write(str(wr_dict[wr]['iseg'])+' '+str(len(celldf.loc[celldf['wrname']==basewr,'wr_frac']))+' ')#old line, see 2n part of new below #SEGID NUMCELLSEG\n')
                        # new pars, see input_instructions_AG.docx
                        f.write('0.0 0.0 #SEGID NUMCELLSEG IRRPERIODSEG TRIGGERFACTSEG\n')
                        for i,(r,c,p) in enumerate(zip(celldf.loc[celldf['wrname']==basewr,'row'].tolist(),celldf.loc[celldf['wrname']==basewr,'col'].tolist(),celldf.loc[celldf['wrname']==basewr,'wr_frac'].tolist())):
                            if i==0:
                                com=' #IRRROW IRRCOL EFF_FACT FIELD_FACT'
                            else:
                                com=''
                            f.write(str(r)+' '+str(c)+' '+str(round(effmar,4))+' '+str(p)+com+'\n')
                elif marsfr<0:
                    f.write(str(marsfr)+' #NUMIRRSEGSP cont mar\n')
                elif marsfr==0 and irrsfr==0:
                    f.write(str(0)+' #NUMIRRSEGSP\n')
                else:
                    print(irrsfr,marsfr)
                    donkey=derp

            #irrwell, wells only associated with original wr not rot
            f.write('IRRWELL\n'+str(irrwell)+' #IRRWELLSP\n')
            if irrwell>0:
                for wr in wrsupsort:
                    for wellnum in sorted(sup_dict[wr]):
                        f.write(str(wellnum)+' '+str(len(celldf.loc[celldf['wrname']==wr,'wr_frac']))+' ')# old line, see below for new #WELLID NUMCELLSEG')

                        #dummy variables not being used, same line as above, see input_instructions_AG.docx
                        f.write('0.0 0.0 #WELLID NUMCELLSEG IRRPERIODWEL TRIGGERFACTWEL\n')

                        for i,(r,c,p) in enumerate(zip(celldf.loc[celldf['wrname']==wr,'row'].tolist(),celldf.loc[celldf['wrname']==wr,'col'].tolist(),celldf.loc[celldf['wrname']==wr,'wr_frac'].tolist())):
                            if i==0:
                                com=' #IRRROW IRRCOL EFF_FACT FIELD_FACT'
                            else:
                                com=''
                            f.write(str(r)+' '+str(c)+' '+str(min(1.0,round(sup_dict[wr][wellnum]['welleff'],4)))+' '+str(round(p,4))+com+'\n')      #edit here for GWEFF for each sup
            #supwell
            f.write('SUPWELL\n'+str(irrwell)+'\n')# #keeping all irrigation wells (even gwonly) supplemental durring irrigation season
            if irrwell>0:
                for wr in wrsupsort:
                    for wellnum in sorted(sup_dict[wr]):
                        if futurepmp==True:
                            f.write(str(wellnum)+' '+str(1)+'\n') #supwellnum, numsegs... only 1 segment per supwell at this point
                            f.write(str(wr_dict[wr]['iseg'])+' 1.0  '+str(sup_dict[wr][wellnum]['fracsupmax'][0])+' #SEGWELLID FRACSUP FRACSUPMAX\n')
                        else:
                            if sup_dict[wr][wellnum]['startyr']<=yr:
                                f.write(str(wellnum)+' '+str(1)+'\n') #supwellnum, numsegs... only 1 segment per supwell at this point
                                f.write(str(wr_dict[wr]['iseg'])+' 1.0  '+str(sup_dict[wr][wellnum]['fracsupmax'][0])+' #SEGWELLID FRACSUP FRACSUPMAX\n')
                            else: #not pumping yet
                                f.write(str(wellnum)+' '+str(1)+'\n') #supwellnum, numsegs... only 1 segment per supwell at this point
                                f.write(str(wr_dict[wr]['iseg'])+' 0.0  0.0 '+' #SEGWELLID FRACSUP FRACSUPMAX\n')
            f.write('END\n')
    return()


#the first line is slow, is independent, and writes wrpcpmltdf.csv
#if wrpcpmltdf.csv exists, the second line saves much time
wrpcpmltdf=get_finf(uzffile,wr_dict)
#wrpcpmltdf=pd.read_csv('wrpcpmltdf.csv',index_col=0)


#get flows if basing stuff on inflow or mar
#not necessary if reading existing irrate and swf
regdf=get_flows(regfile)

#irrigation rates and efficiencies as a function of regulation and precip
wr_dict=calc_irrate(regdf,wr_dict,wrpcpmltdf,marwrlist,trigfile=trigfile,cumflowmaron=0) #also calcs efficiency rates, needed to write_ag
#wr_dict=read_irrate(wr_dict,dmdunit)
#wr_dict=read_swf(wr_dict,swfdir)

#change wr_dict[wr] to reflect ag to muni
#wr_dict,celldf=ag2muni(wr_dict,transwr,celldf)

write_ag(agfile,wr_dict,sup_dict)