@echo off

REM ___________________________ call observation batch file ___________________________________________
REM
REM   %1 is name of grid specification file *.spc.txt
REM   %2 is name of bore coordinates file:
REM   %3 is name of bore listing file:
REM   %4 is name of bore sample file:
REM   %5 is name of unformatted model-generated file:
REM   %6 is  simulation starting date [mm/dd/yyyy]:
REM   %7 is simulation starting time [hh:mm:ss]:
REM   %8 is number of layers in the model?
REM   %9 is name for bore sample output file:

call 01_Sub.Mod2OBS.bat CV-gridspec.txt CV-wes-8015trans-obswellcoord.txt CV-wes-8015trans-obslisting.txt CV-wes-8015trans-headmod2obs.txt ../../output/output_MSGSF_hist/CV-wes-8015trans-closest-hist.bheds 07/02/1979 12:00:00 5 ../../output/output_MSGSF_hist/CV-wes-8015trans-headsim.txt

REM  ---- Extract area-weighted & depth integrated transmissivity values from model  
REM
REM   %1 is name of MODFLOW name file 
REM   %2 is name of the node-fraction file that was created by T-COMP_Extract 
REM   %3 is name of simulated transmissivity output file from T-COMP_Simulated:

REM call 01_Sub.TranOBS.bat INPUT_DV3-05_.NAME.txt  Pcomp_DV3-05_.Tcomp_Node-Fractions.txt  Pcomp_DV3-05_.TRANsimulated.txt

