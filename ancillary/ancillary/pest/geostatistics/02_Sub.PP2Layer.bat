@echo off
REM
REM  ____________________ Interpolate from PP to a 2D arrays___________________________________
REM                     PP were translated to factors by node   
REM
REM  Program FAC2REAL carries out spatial interpolation based on interpolation
REM  factors calculated by PPK2FAC and pilot point values contained in a pilot
REM  points file.

REM  The following is a key for the parameters that were passed to this file.
REM  %1 :: pp_%1_HK.txt.fac
REM  %2 :: PP_%1_HK.txt
REM  %3 :: ..\upw\CV-wes-8015trans-%1%2.lay

REM  Enter name of interpolation factor file:
echo %1                                                                               > Temp_Control_%1.txt
REM  Is this a formatted or unformatted file? [f/u]:
echo f                                                                               >> Temp_Control_%1.txt
REM  Enter name of pilot points file [points.dat]:
echo %2                                                                              >> Temp_Control_%1.txt
REM  Supply lower interpolation limit as an array or single value? [a/s]:
echo s                                                                               >> Temp_Control_%1.txt
REM  Enter lower interpolation limit:
echo 1e-4                                                                            >> Temp_Control_%1.txt
REM  Supply upper interpolation limit as an array or single value? [a/s]:
echo s                                                                               >> Temp_Control_%1.txt
REM  Enter upper interpolation limit:
echo 1e4                                                                             >> Temp_Control_%1.txt
REM  Enter name for output real array file:
echo %3                                                                              >> Temp_Control_%1.txt
REM  Is this a formatted or unformatted file? [f/u]:
echo f                                                                               >> Temp_Control_%1.txt
REM  Enter value for elements to which no interpolation takes place:
echo 0.000                                                                           >> Temp_Control_%1.txt


fac2real  < Temp_Control_%1.txt > screen_out_%1.txt