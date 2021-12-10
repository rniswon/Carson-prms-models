@echo off
echo colrow=no           > settings.fig
echo date=mm/dd/yyyy    >> settings.fig

REM __________________________________________________________________________________________________
REM
REM  

REM                                %1     %2
REM                                --     --
call 01_Sub.LBBuild.bat        2    lb
call 01_Sub.LBBuild.bat        3    lb
call 01_Sub.LBBuild.bat        4    lb
call 01_Sub.LBBuild.bat        5    lb



echo .
echo *********************************************
echo Finished Interpolating Pilot Points to Arrays
echo *********************************************
echo .
