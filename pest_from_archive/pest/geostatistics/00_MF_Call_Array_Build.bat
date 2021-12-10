@echo off
echo colrow=no           > settings.fig
echo date=mm/dd/yyyy    >> settings.fig

REM __________________________________________________________________________________________________
REM
REM  

REM                                %1     %2
REM                                --     --
call 01_Sub.ArrayBuild.bat        2    HK
call 01_Sub.ArrayBuild.bat        3    HK
call 01_Sub.ArrayBuild.bat        4    HK
call 01_Sub.ArrayBuild.bat        5    HK
call 01_Sub.ArrayBuild.bat        2    VA
call 01_Sub.ArrayBuild.bat        3    VA
call 01_Sub.ArrayBuild.bat        4    VA
call 01_Sub.ArrayBuild.bat        5    VA
call 01_Sub.ArrayBuild.bat        2    SY
call 01_Sub.ArrayBuild.bat        3    SY
call 01_Sub.ArrayBuild.bat        4    SY
call 01_Sub.ArrayBuild.bat        5    SY
call 01_Sub.ArrayBuild.bat        2    SS
call 01_Sub.ArrayBuild.bat        3    SS
call 01_Sub.ArrayBuild.bat        4    SS
call 01_Sub.ArrayBuild.bat        5    SS



echo .
echo *********************************************
echo Finished Interpolating Pilot Points to Arrays
echo *********************************************
echo .
