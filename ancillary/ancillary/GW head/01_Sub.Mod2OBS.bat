@echo off

REM  Extract water-levels/drawdowns from unformatted head file
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

REM ___________________________ call observation batch file ___________________________________________

echo %1        > m2o_input.txt
rem Enter name of grid specification file:
echo %2    >> m2o_input.txt
rem Enter name of bore coordinates file:
echo %3     >> m2o_input.txt
rem Enter name of bore listing file:
echo %4    >> m2o_input.txt
rem Enter name of bore sample file:
echo %5    >> m2o_input.txt
rem Enter name of unformatted model-generated file:
echo f             >> m2o_input.txt
rem Is this a MODFLOW or MT3D file? [f/t]:
echo 1E+20     >> m2o_input.txt
rem Enter inactive threshold value for numbers in this file:
echo d             >> m2o_input.txt
rem Enter time units used by model (yr/day/hr/min/sec) [y/d/h/m/s]:
echo %6     >> m2o_input.txt
rem Enter simulation starting date [mm/dd/yyyy]:
echo %7     >> m2o_input.txt
rem Enter simulation starting time [hh:mm:ss]:
echo %8             >> m2o_input.txt
rem How many layers in the model?
echo 1.             >> m2o_input.txt
rem Enter extrapolation limit in days (fractional if necessary):
echo %9   >> m2o_input.txt
rem Enter name for bore sample output file:
echo               >> m2o_input.txt

mod2obs < m2o_input.txt   > m2o_echo.txt

rem m2o_input.txt  > nul
      