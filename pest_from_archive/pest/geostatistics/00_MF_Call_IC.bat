@echo off
echo colrow=no           > settings.fig
echo date=mm/dd/yyyy    >> settings.fig

REM __________________________________________________________________________________________________
REM
REM  

REM                                %1     %2
REM                                --     --
call 01_Sub.ICBuild.bat        2    ic
call 01_Sub.ICBuild.bat        3    ic
call 01_Sub.ICBuild.bat        4    ic
call 01_Sub.ICBuild.bat        5    ic



echo .
echo *********************************************
echo Finished Interpolating Pilot Points to Arrays
echo *********************************************
echo .
