#get GWET from cbc, crop consump from SW and crop consump from GW
# sum for annual ET from each WR as calibration target

import time

import os
import flopy.utils.binaryfile as bf
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import CV_tools

cdir=os.getcwd()
os.chdir(cdir)
os.chdir(r'..\..')
cdir=os.getcwd()

def wr_cbc2ts(cbc,name,wrlist,celldf,stpsperlist):
    gwet={}
    #get entire model gwet array
    val=[]
    for stpsper in stpsperlist:
        #make list of 2 array sum of all layers for each stpsper
        val.append(cbc.get_data(kstpkper=stpsper,text=name)[0].sum(axis=0))
    #stack into seasonal array, sum, and multiply by days
    annval=np.dstack(val).sum(axis=2)*7 #stupid hardwired, should get sp from somewhere and pass it with stpsperlist
    #get wr cells
    for wr in wrlist:
        #wr=celldf.loc[idx,'wrname']
        farr=np.zeros((258,206))
        rows=tuple(celldf.loc[celldf['wrname']==wr,'row'].map(int))
        cols=tuple(celldf.loc[celldf['wrname']==wr,'col'].map(int))
        pcts=tuple(celldf.loc[celldf['wrname']==wr,'frac_cell_irr'])
        farr[rows,cols]=pcts
        #print('wr {} has bits in {} cells'.format(wr,np.count_nonzero(farr)))
        gwet[wr]=(annval*farr).sum() #in cfd
        model_tot=annval.sum()
    return(gwet,model_tot)

dTscenlist=['0C']#['hist','0C','1C','2C','3C','4C','5C']
for dTscen in dTscenlist:
    trun=time.time()
    print(dTscen)

    extdir=os.path.join(cdir,'model','external_files','Carson_Valley')
    modir=os.path.join(cdir,'model','MSGSF_'+dTscen)
    outdir=os.path.join(cdir,'output','output_MSGSF_'+dTscen)
    print(extdir)
    print(modir)
    print(outdir)

    gwet={}
    wrdf={}

    #read in parameters, use sup_irr_input
    infile=os.path.join(modir,'sup_irr_input.txt')
    with open(infile,'r') as f:
        lines=f.readlines()

    par={}
    for l in lines:
        if l[0]!='#' and len(l)>1:
            data=l.strip().split('=')
            k=data[0]
            v=data[1]
            par[k]=v

    #convert to params
    confile=par['confile']
    with open(os.path.join(modir,confile),'r') as f:
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
    modnam=namfile.split('.nam')[0]
    doystartirr=float(par['doystartirr'])-1
    doyendirr=float(par['doyendirr'])-1
    firstyr=int(par['firstyr'])
    lastyr=int(par['lastyr'])

    #start date
    t0=sp[0]

    #read in sp from dis
    # in dummy world sp[0]=7/2/1979, but first kstpkper=(0,0) is 7/9/1979 in flopy, should be consistent here
    # don't pre-populate sp with 7/2/1979
    sp=[]
    fname='CV-wes-8015trans.dis'
    with open(os.path.join(extdir,fname),'r') as f:
        lines=f.readlines()

    for line in lines:
        if 'sp=' in line: #assume sufficient to identify stress period, date as last entry
            data=line.strip().split()
            d8=data[-1].split('-')
            sp.append(datetime.date(int(d8[0]),int(d8[1]),int(d8[2])))



    #get cell pos and fractions for each wr (R,C,Frac), make 0 based
    celldf=pd.read_csv(os.path.join(extdir,icellfracfile))
    celldf.columns=celldf.columns.str.lower()
    celldf['row']=celldf['row']-1
    celldf['col']=celldf['col']-1



    wracres=celldf.loc[:,['wrname','cell_acres']].groupby('wrname').sum()
    wracres.index=wracres.index.str.lower()

    cbcfile=os.path.join(outdir,'CV-wes-8015trans-closest-'+dTscen+'.cbc')
    cbc=bf.CellBudgetFile(cbcfile)
    recs=cbc.get_unique_record_names()
    for rec in recs:
        if 'GW' in str(rec) and 'ET' in str(rec):
            gwetname=rec

    #get list of wells from name file
    welldic={} #welldic={wr-well:wr}
    with open(os.path.join(modir,namfile),'r') as f:
        lines=f.readlines()
    for line in lines:
        if '.wellgag' in line:
            data=line.strip().lower().replace('.wellgag','').split('-')
            well=data[-1]
            d=data[3:-1] #assumes 'CV-wes-8015trans-'
            if len(d)>=1:
                if 'jobs' not in d:
                    wr=d[0].replace('obs','')
                else:
                    wr=d[0]
                for w in d[1:]:
                    wr=wr+'-'+w
                nwr=wr+'-'+well
            welldic[nwr]=wr #wr-well combo with wr

    tread=time.time()
    print('read input: {}'.format(round(tread-trun,2)))

    #get gwet for (stp,per) of interest for each wr
    #function of doystart and doystop irr, but not interpolated
    gwet={}
    model_gwet={}
    wrlist=sorted(list(set(celldf.wrname.str.lower().tolist())))
    yrlist=[i for i in range(firstyr,lastyr+1)]
    for yr in yrlist:
        d8start=datetime.date(yr-1,10,1)#+datetime.timedelta(days=doystartirr)
        d8stop=datetime.date(yr,9,30)#+datetime.timedelta(days=doyendirr-1)
        stpsperlist=[]
        for i,s in enumerate(sp):
            if s.year==yr and d8start<s<d8stop:
                stpsperlist.append((0,i)) #assuming always first timestep
        gwet[yr],model_gwet[yr]=wr_cbc2ts(cbc,gwetname,wrlist,celldf,stpsperlist)


    #make dataframe because why not
    data=[]
    for yr in gwet:
        data.append(pd.DataFrame(gwet[yr],index=[yr]))
    gwetdf=pd.concat(data)
    #make df for model wide gwet
    model_gwetdf=pd.Series(model_gwet,name='model_gwet')

    tgwet=time.time()
    print('gwet: {}'.format(round(tgwet-tread,2)))




    swetdf={}
    welletdf={}
    wrwelldf={}
    swgagdf={}
    swdmddf={}
    pcpetdf={}
    for wr in wrlist: #get ET and sw delivery output from AG package time series
        try:
            swetdf[wr]=CV_tools.ts2df(wr,'.swet',t0,rpath=outdir,val='eta')
        except:
            pass#print('{} does not have surface water right, so no swet'.format(wr))
        try:
            swgagdf[wr]=CV_tools.ts2df(wr,'.swgag',t0,rpath=outdir,val='sw-diversion')
        except:
            pass#print('{} does not have surface water gage'.format(wr))
        try:
            swdmddf[wr]=CV_tools.ts2df(wr,'.swgag',t0,rpath=outdir,val='sw-right')
        except:
            pass#print('{} does not have surface water gage'.format(wr))
        try:
            pcpetdf[wr]=CV_tools.ts2df(wr,'.pcpet',t0,rpath=os.path.join(modir,'pcpet'),val='etpcp')
        except:
            print('failed on {} {}'.format(wr,os.path.join(modir,'pcpet')))

        # now sw for rot
        nwr=wr+'_rot'
        try:
            swetdf[nwr]=CV_tools.ts2df(nwr,'.swet',t0,rpath=outdir,val='eta')
        except:
            pass
        try:
            swgagdf[nwr]=CV_tools.ts2df(nwr,'.swgag',t0,rpath=outdir,val='sw-diversion')
        except:
            pass#print('{} does not have surface water gage'.format(wr))
        try:
            swdmddf[nwr]=CV_tools.ts2df(nwr,'.swgag',t0,rpath=outdir,val='sw-right')
        except:
            pass#print('{} does not have surface water gage'.format(wr))

    print('{} swet gages read'.format(len(swetdf)))
    print('{} swgag gages read'.format(len(swgagdf)))
    print('{} pcpet gages read'.format(len(pcpetdf)))


    #need to get each wells for many wr ts2df can take wr-well for site
    for w in welldic:
        try:
            wrwelldf[w]=CV_tools.ts2df(w,'.wellgag',t0,rpath=outdir,val='gw-pumped')
        except:
            pass#print('{} does not have a well'.format(w))
        try:
            welletdf[w]=CV_tools.ts2df(w,'.wellet',t0,rpath=outdir,val='eta')
        except:
            pass#print('{} does not have a well, so no wellet'.format(w))
    print('{} wellet gages read'.format(len(welletdf)))
    print('{} wellgag gages read'.format(len(wrwelldf)))


    #add all vals for each real well
    welldf={}
    for w in wrwelldf:
        rwell=w.split('-')[-1]
        if rwell not in welldf:
            welldf[rwell]=wrwelldf[w].copy()
        else:
            #print(rwell)
            #print(welldf[rwell].tail(10))
            welldf[rwell].val=welldf[rwell].val+wrwelldf[w].val
            welldf[rwell].well=rwell
            #print(rwell)
            #print(welldf[rwell].tail(10))

    tts=time.time()
    print('read time-series: {}'.format(round(tts-tgwet,2)))

    swgag={}
    swdmd={}
    swet={}
    wellet={}
    welldel={}
    well={}
    pcpet={}
    for yr in yrlist:
        swgag[yr]={}
        swdmd[yr]={}
        swet[yr]={}
        wellet[yr]={}
        welldel[yr]={}
        well[yr]={}
        pcpet[yr]={}
        d8start=datetime.date(yr-1,10,1)#+datetime.timedelta(days=doystartirr)
        d8stop=datetime.date(yr,9,30)#+datetime.timedelta(days=doyendirr-1)
        spstart=0
        spstop=0
        for s in range(0,len(sp)-1):
            if sp[s]<d8start<=sp[s+1]:
                spstart=sp[s]+datetime.timedelta(days=1)
            elif sp[s]<d8stop<=sp[s+1]:
                spstop=sp[s+1]
            elif s==len(sp)-2 and spstart!=0: #make spstop==end of sim
                spstop=sp[-1]
        #only interpolate values within a month of start and stop
        substart=d8start-datetime.timedelta(days=30)
        substop=d8stop+datetime.timedelta(days=30)

        #et by wr
        for wr in list(swetdf.keys()):
            nwr=wr.replace('_rot','')
            if nwr not in swet[yr]:#don't overwrite those with _rot
                swet[yr][nwr]=swetdf[nwr][substart:substop].resample('D').fillna(method='backfill')[spstart:spstop]['val'].sum()
            if '_rot' in wr: #combine with wr
                rswet=swetdf[wr][substart:substop].resample('D').fillna(method='backfill')[spstart:spstop]['val'].sum()
                swet[yr][nwr]=swet[yr][nwr]+rswet



            # ET from wells by wr, keep
            if wr not in wellet[yr]:
                wellet[yr][wr]=[]
            wellwr=[w for w in wrwelldf if welldic[w]==wr]
            for w in wellwr:
                wellet[yr][wr].append(welletdf[w][substart:substop].resample('D').fillna(method='backfill')[spstart:spstop]['val'].sum())

            # well deliveries by wr rather than well
            if wr not in welldel[yr]:
                welldel[yr][wr]=[]
            wellwr=[w for w in wrwelldf if welldic[w]==wr]
            for w in wellwr:
                welldel[yr][wr].append(wrwelldf[w][substart:substop].resample('D').fillna(method='backfill')[spstart:spstop]['val'].sum())

        #sum by wr
        for wr in wellet[yr]:
            wellet[yr][wr]=sum(wellet[yr][wr])
        for wr in welldel[yr]:
            welldel[yr][wr]=sum(welldel[yr][wr])

        #do wells
        for w in welldf:
            if w not in well[yr]:
                well[yr][w]=welldf[w][substart:substop].resample('D').fillna(method='backfill')[spstart:spstop]['val'].sum()

        # do swgages
        for wr in list(swgagdf.keys()): #190930 changed from rotdf=pd.concat([swetdf to swgag
            nwr=wr.replace('_rot','')
            if nwr not in swgag[yr]: #don't overwrite those with _rot
                swgag[yr][nwr]=swgagdf[nwr][substart:substop].resample('D').fillna(method='backfill')[spstart:spstop]['val'].sum()
            if '_rot' in wr: #combine with wr
                rswgag=swgagdf[wr][substart:substop].resample('D').fillna(method='backfill')[spstart:spstop]['val'].sum()
                swgag[yr][nwr]=swgag[yr][nwr]+rswgag

         # do swdmd
        for wr in list(swdmddf.keys()): #190930 changed from rotdf=pd.concat([swetdf to swgag
            nwr=wr.replace('_rot','')
            if nwr not in swdmd[yr]: #don't overwrite those with _rot
                swdmd[yr][nwr]=swdmddf[nwr][substart:substop].resample('D').fillna(method='backfill')[spstart:spstop]['val'].sum()
            if '_rot' in wr: #combine with wr
                rswdmd=swdmddf[wr][substart:substop].resample('D').fillna(method='backfill')[spstart:spstop]['val'].sum()
                swdmd[yr][nwr]=swdmd[yr][nwr]+rswgag




        # do pcpet
        for wr in list(pcpetdf.keys()):
            if '_rot' not in wr:
                pcpet[yr][wr]=pcpetdf[wr][substart:substop].resample('D').fillna(method='backfill')[spstart:spstop]['val'].sum()


    tpts=time.time()
    print('process time-series: {}'.format(round(tpts-tts,2)))

    #write ET
    model_gwetdf.to_csv(os.path.join(outdir,'sim_model_gwet.csv'))
    totwret={}
    with open(os.path.join(outdir,'sim_wret_ts.txt'),'w+') as f:
        f.write('{0} {1} {2} {3} {4} {5}\n'.format('obnme','total_wr_et','gwet','wellet','swet','pcpet'))
        for yr in yrlist:
            totwret[yr]={}
            for wr in sorted(list(set(swet[yr]))): #leaves out GW only water rights
                et=[swet[yr][wr]]
                if wr in gwet[yr]:
                    et.append(abs(gwet[yr][wr]))
                else:
                    et.append(0)
                if wr in wellet[yr]:
                    et.append(wellet[yr][wr])
                else:
                    et.append(0)
                if wr in pcpet[yr]:
                    et.append(pcpet[yr][wr])
                else:
                    et.append(0)
                obnme='et_'+str(wr)+'_'+str(yr)[-2:]
                #print('{}: swet {}, gwet {}, wellet {}'.format(obnme,et[0],et[1],et[2]))
                #print('{} {}\n'.format(obnme,sum(et)))
                totwret[yr][wr]=sum(et)
                f.write('{0} {1} {2} {3} {4} {5}\n'.format(obnme,totwret[yr][wr],abs(gwet[yr][wr]),wellet[yr][wr],swet[yr][wr],pcpet[yr][wr]))
    #convert to rates and make new file
    with open(os.path.join(outdir,'sim_wrrt_ts.txt'),'w+') as f:
        f.write('{0} {1}\n'.format('obnme','et_rate'))
        for yr in yrlist:
            for wr in sorted(list(set(totwret[yr]))):
                obnme='rt_'+str(wr)+'_'+str(yr)[-2:]
                rate=totwret[yr][wr]/43560/wracres.loc[wr,'cell_acres']
                f.write('{} {}\n'.format(obnme,rate))
    #just a repeat for less than obs
    with open(os.path.join(outdir,'sim_lesswrrt_ts.txt'),'w+') as f:
        f.write('{0} {1}\n'.format('obnme','et_rate'))
        for yr in yrlist:
            for wr in sorted(list(set(totwret[yr]))):
                obnme='lrt_'+str(wr)+'_'+str(yr)[-2:]
                rate=totwret[yr][wr]/43560/wracres.loc[wr,'cell_acres']
                f.write('{} {}\n'.format(obnme,rate))

    with open(os.path.join(outdir,'sim_pmp_ts.txt'),'w+') as f:
        f.write('{0} {1}\n'.format('obnme','wypmp'))
        for yr in yrlist:
            wypmp=[]
            for w in sorted(list(set(well[yr]))): #leaves out wr with gw only
                obnme=str(w)+'_'+str(yr)[-2:]
                f.write('{} {}\n'.format(obnme,well[yr][w]))
                wypmp.append (well[yr][w])
            obnme='wypmp_'+str(yr)[-2:]
            f.write('{0} {1}\n'.format(obnme,sum(wypmp)))

    with open(os.path.join(outdir,'sim_swgag_ts.txt'),'w+') as f:
        f.write('{0} {1} {2} {3} {4}\n'.format('obnme','tot_del','sw_del','sw_dmd','well_del'))
        for yr in yrlist:
            for wr in sorted(list(set(swgag[yr]))): #leaves out wr with gw only
                obnme='del_'+str(wr)+'_'+str(yr)[-2:]
                f.write('{0} {1} {2} {3} {4}\n'.format(obnme,sum([swgag[yr][wr],welldel[yr][wr]]),swgag[yr][wr],swdmd[yr][wr],welldel[yr][wr]))

    tdone=time.time()

    print('total: {}'.format(round(tdone-trun,2)))