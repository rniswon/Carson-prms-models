
REM __________________________________________________________________________________________________

REM  Use layer 5 factor file and pilot points, plus PEST determined heads at each PP to interpolate "best" IC
REM  Use range of 33000 to smooth?

REM For Hydraulic conductivity of layers 2 - 5
REM ------------------------------------------

call 02_Sub.IC2Layer.bat     pp_lay%1_%2.txt.fac     pp_lay%1_%2.txt      ..\arrays\CV-wes-0005trans-ICA%1.dat  %1