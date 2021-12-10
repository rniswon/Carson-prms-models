#extract water year pumpage from list file
#requires list of  wells in each subregion
#output a table to be read by PEST using .ins file

import datetime

##infile=raw_input('Enter file containing input information:')
##if infile=='':
infile='sim_list_input.txt'

print('Reading '+infile+'\n')
#read in parameters
with open(infile,'r') as f:
    lines=f.readlines()
par={}
for line in lines:
    if line[0]!='#' and len(line)>1:
        print(line)
        data=line.strip().split('=')
        if len(data)==2:
            k=data[0]
            v=data[1]
            par[k]=v
#convert to params
disname=par['disname']
listname=par['listname']
irrname=par['irrname']
outname=par['outname']
recyrs=[int(yr) for yr in par['recyrs'].split(',')]


#read in wells from each subarea
if '.txt' in irrname:
    fname=irrname
else:
    fname=irrname+'.txt'
with open(fname,'r') as f:
    lines=f.readlines()
well_dict={}
for line in lines:
    if '#' != line.strip()[0]:
        data=line.strip().split()
        wellnum=data[3]
        if wellnum!='NA':
            if wellnum not in well_dict:
                well_dict[wellnum]={'realwell':[]}
            well_dict[wellnum]['realwell'].append(data[12])

#read in sp from dis
if '.dis' in disname:
    fname=disname
else:
    fname=disname+'.dis'
with open(fname,'r') as f:
    lines=f.readlines()
sp=[]
dt=[]
for line in lines:
    if 'sp=' in line: #assume sufficient to identify stress period, date as last entry
        data=line.strip().split()
        dt.append(int(data[0]))
        yr=int(data[-1].split('-')[0])
        mo=int(data[-1].split('-')[1])
        day=int(data[-1].split('-')[2])
        sp.append(datetime.date(yr,mo,day))
        for d in data:
            if 'sp=' in d:
                nsp=d.split('=')[-1]
if len(sp)==int(nsp):
    sp.append(sp[0]-datetime.timedelta(days=dt[0])) #add in sp[0] start of simulation
sp=sorted(sp)

#get .list information
if '.list' in listname:
    fname=listname
else:
    fname=listname+'.list'
wellout={}
totpmp={}
pdis={}
nwtin={}
nwtout={}
tstep={}
spnum=0
lin=0
with open (listname,'r') as f:
    lines=f.readlines()
while lin < len(lines)-1:
    lin=lin+1
    line=lines[lin]
    if 'STRESS PERIOD NO' in line:
        spnum=int(line.strip().split()[3].replace(',',''))
        if spnum not in tstep:
            tstep[spnum]={}
            nwtout[spnum]={}
            nwtin[spnum]={}
            totpmp[spnum]={}
            pdis[spnum]={}
    if 'SOLVING FOR HEAD' in line:
        nout=0
        nin=0
        while 'OUTPUT CONTROL FOR STRESS PERIOD' not in line:
            lin=lin+1
            line=lines[lin]
            if 'NWT REQUIRED' in line and 'OUTER ITERATIONS' in line:
                nout=nout+int(line.strip().split()[2])
            if 'AND A TOTAL OF' in line and 'INNER ITERATIONS' in line:
                nin=nin+int(line.strip().split()[4])
        if 'OUTPUT CONTROL FOR STRESS PERIOD' in line:
            if spnum==int(line.strip().split()[-4]):
                ts=int(line.strip().split()[-1])
                nwtout[spnum][ts]=nout
                nwtin[spnum][ts]=nin
##        #get awu pump rates, all awu rates are 0 except last sp, missing something?
##        if 'AG' in line and 'WELLS' in line and 'PERIOD' in line and 'STEP' in line:
##            while 'VOLUMETRIC BUDGET FOR ENTIRE MODEL AT END OF TIME STEP' not in line:
##                lin=lin+1
##                line=lines[lin]
##                data=line.strip().split()
##                if len(data)>1 and data[0]=='AG' and data[1]=='WELL':
##                    wellnum=data[2]
##                    if wellnum in well_dict:
##                        if wellnum not in wellout:
##                            wellout[wellnum]={}
##                        if spnum not in wellout[wellnum]:
##                            wellout[wellnum][spnum]={}
##                        wellout[wellnum][spnum][ts]=-float(data[-1]) #positive pumpage reported as negative in list
        # read budget table, use cumulative
        if 'VOLUMETRIC BUDGET FOR ENTIRE MODEL AT END OF TIME STEP' in line:
            if spnum==int(line.strip().replace('PERIOD','').split()[-1]): #check stress period
                #get cumulative AG pumpage, keep overwriting, use last one for sp
                while 'PERCENT DISCREPANCY' not in line: #3/8/2018 budget table for AG and entire have same header. AG pump reported as "IN" in first budget table, same value as "OUT" in second table
                    lin=lin+1
                    line=lines[lin]
                    if 'IN:' in line:
                        while 'TOTAL IN' not in line:
                            lin=lin+1
                            line=lines[lin]
                            if 'AG' in line and  'WELLS' in line:
                                data=line.strip().split()
                                dx=data.index('=') #takes first occurance
                                totpmp[spnum][ts]=float(data[dx+1].replace('AG','')) #gets cumulative value, use dif in procper
                #rip through the rest of the awu budget table
                while 'VOLUMETRIC BUDGET FOR ENTIRE MODEL AT END OF TIME STEP' not in line: #second budget table, bet percent dis
                    lin=lin+1
                    line=lines[lin]
                #get cumulative pdis, keep overwriting, use last one for sp
                while 'TIME SUMMARY AT END OF TIME STEP' not in line:
                    lin=lin+1
                    line=lines[lin]
                    if 'PERCENT' in line and 'DISCREPANCY' in line:
                        if ts not in pdis[spnum]:
                            pdis[spnum][ts]={}
                        data=line.strip().split()
                        pdis[spnum][ts]=float(data[-1])
            else:
                print('this is not the stress period you are looking for')
                donkeys==derp
        if 'TIME SUMMARY AT END OF TIME STEP' in line:
            if spnum==int(line.strip().split()[-1]) and ts==int(line.strip().split()[7]): #check stress period
                lin=lin+5
                line=lines[lin]
                data=line.strip().split()
                tstep[spnum][ts]=sp[0]+datetime.timedelta(days=float(data[5]))
            else:
                print('this is not the stress period and time step you are looking for')
                donkeys==derp


##    if ' Elapsed run time:' in line: #in minutes
##        simmin=0
##        tstring=line.strip().split(':')[1]
##        #print('MODFLOW run took ',tstring)
##        for data in tstring.split(','):
##            if 'hours' in data.lower():
##                simmin=float(data.split()[0])*60
##            if 'minutes' in data.lower():
##                simmin=simmin+float(data.split()[0])
##            if 'seconds' in data.lower():
##                simmin=simmin+float(data.split()[0])/60

def conv(tstep={},Q={}):
    #annual rates, calendar year NOT WY
    Qlist=[]
    for s in tstep:
        for t in tstep[s]:
            if t in Q[s]:
                Qlist.append((tstep[s][t],Q[s][t]))
    Qlist=sorted(Qlist)
    return(Qlist)
def procper(Q,recyrs,meth='cum'):
    procQ={}
    for yr in recyrs:
        startdate=datetime.date(yr,1,1)
        enddate=datetime.date(yr,12,31)
        maxt=max([rec[0] for rec in Q if startdate<=rec[0]<=enddate])
        mint=min([rec[0] for rec in Q if (maxt-datetime.timedelta(days=365.25))<=rec[0]<=enddate])
        if meth=='cum': #assume rates reported in cfd
            temp=[]
            for i, rec in enumerate(Q):
                if mint<rec[0]<=maxt:
                    temp.append(float(rec[1]*(Q[i][0]-Q[i-1][0]).days)) #cum vol
            procQ[yr]=sum(temp)
        if meth=='dif': #assume value in cf
            #print(mint,maxt)
            #print([rec[1] for rec in Q if rec[0]==maxt])
            procQ[yr]=float([rec[1] for rec in Q if rec[0]==maxt][0])-float([rec[1] for rec in Q if rec[0]==mint][0])
    return(procQ)

###convert to list of tup (date,val)
##Qtotpmp=conv(tstep=tstep,Q=totpmp)
##Qwellout={}
##for well in wellout:
##    Qwellout[well]=conv(tstep=tstep,Q=wellout[well])
##
###get list of real wells
##welllist=[]
##for well in well_dict:
##    for rwell in well_dict[well]['realwell']:
##        welllist.append(rwell)
##swelllist=sorted(list(set(welllist)))
### get simulated pumpage for all real wells
##real_wellyr={}
##for realwell in swelllist:
##    real_wellyr[realwell]={}
##    for well in well_dict:
##        if realwell in well_dict[well]['realwell']:
##            tempyr=procper(Qwellout[well],recyrs,meth='cum') #returns dict[yr]=Q
##            for yr in tempyr: #sum all real wells
##                if yr not in real_wellyr[realwell]:
##                    real_wellyr[realwell][yr]=tempyr[yr]
##                else:
##                    real_wellyr[realwell][yr]=real_wellyr[realwell][yr]+tempyr[yr]
### annual ag pump rates, dif
##totpmpyr=procper(Qtotpmp,recyrs,meth='dif')

#nwt required
nwtoutsp={}
nwtinsp={}
for s in tstep:
    nwtoutsp[s]=sum([nwtout[s][t] for t in nwtout[s]])
    nwtinsp[s]=sum([nwtin[s][t] for t in nwtin[s]])

#pdis for sp
pdissp={}
for s in tstep:
    pdissp[s]=sum([pdis[s][t] for t in pdis[s]])

#write data table
with open(outname,'w+') as f:
##    for realwell in sorted(real_wellyr):
##        for yr in sorted(real_wellyr[realwell]):
##            line=(realwell.replace('APP-','')+'_'+str(yr).replace('19','').replace('20',''),str(round(real_wellyr[realwell][yr],8)))
##            f.write('%20s'*len(line) %line)
##            f.write('\n')
##    for yr in sorted(totpmpyr):
##        line=('WYPMP'+str(yr),round(totpmpyr[yr],8))
##        f.write('%20s'*len(line) %line)
##        f.write('\n')
    for s in sorted(pdissp):
        line=('pdis'+str(s),str(pdissp[s]))
        f.write('%20s'*len(line) %line)
        f.write('\n')
    for s in sorted(nwtoutsp):
        line=('nwtout'+str(s),str(nwtoutsp[s]))
        f.write('%20s'*len(line) %line)
        f.write('\n')
    for s in sorted(nwtinsp):
        line=('nwtin'+str(s),str(nwtinsp[s]))
        f.write('%20s'*len(line) %line)
        f.write('\n')
    line=('simtime',str(99999))
    f.write('%20s'*len(line) %line)