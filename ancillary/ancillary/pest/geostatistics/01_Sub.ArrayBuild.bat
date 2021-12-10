
REM __________________________________________________________________________________________________

REM  This batch file creates file names for 02_Sub.PP2Layer.bat

REM  Next, specify the parameters required by the called upon batch file.
REM   %1    Enter name of interpolation factor file:                                 
REM   %2    Enter name of pilot points file [points.dat]:  ---  File altered by PEST 
REM   %3    Enter name for output real array file:           

REM For Hydraulic conductivity of layers 2 - 5
REM ------------------------------------------

call 02_Sub.PP2Layer.bat     pp_lay%1_%2.txt.fac     PP_lay%1_%2.txt      ..\arrays\CV-wes-8015trans-%2%1.lay  %1