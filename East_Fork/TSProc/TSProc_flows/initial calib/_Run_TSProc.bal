REM At some point, add the command for executing PRMS next
REM prms.exe westfork.control

REM move the model output to the tsproc folder
copy D:/CarsonRiv/West_Fork/PRMS/statvar.dat D:/Common/TSProc/WstFrk_statvar.dat

REM run TSProc to get the latest NSE, VE, etc. etc.
call TSProc.exe  TSProc.in TSProc.out