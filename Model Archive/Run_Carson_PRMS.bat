REM Running the Upper Carson River PRMS models 

REM PRMS East Fork historical 
copy bin\gsflow.exe .
copy model\EastFork\input\historical\east_fork.param .
copy model\EastFork\input\historical\eastfork_hist.control .
copy model\EastFork\input\historical\upper_carson_hist.data .

gsflow.exe eastfork_hist.control

del upper_carson_hist.data
del eastfork_hist.control
del east_fork.param
del gsflow.exe

xcopy gsflow.log .\model\EastFork\output\historical /y
xcopy statvar_hist.dat .\model\EastFork\output\historical /y
xcopy prms_hist.out .\model\EastFork\output\historical /y

del gsflow.log
del prms_ic.out
del prms_hist.out
del statvar_hist.dat

pause

REM PRMS East Fork historical with warming
copy bin\gsflow.exe .
copy model\EastFork\input\historical_warm\east_fork.param .
copy model\EastFork\input\historical_warm\eastfork_hist4.3.control .
copy model\EastFork\input\historical_warm\upper_carson_hist4.3.data .

gsflow.exe eastfork_hist4.3.control

del upper_carson_hist4.3.data
del eastfork_hist4.3.control
del east_fork.param
del gsflow.exe

xcopy gsflow.log .\model\EastFork\output\historical_warm /y
xcopy statvar_hist_warm.dat .\model\EastFork\output\historical_warm /y
xcopy prms_hist_warm.out .\model\EastFork\output\historical_warm /y

del gsflow.log
del prms_ic.out
del prms_hist_warm.out
del statvar_hist_warm.dat

pause

REM PRMS East Fork future hi freq
copy bin\gsflow.exe .
copy model\EastFork\input\future_highfreq\hifreq\east_fork.param .
copy model\EastFork\input\future_highfreq\hifreq\eastfork_hifreq.control .
copy model\EastFork\input\future_highfreq\hifreq\upperCarson_highfreq.data .

gsflow.exe eastfork_hifreq.control

del upperCarson_highfreq.data
del eastfork_hifreq.control
del east_fork.param
del gsflow.exe

xcopy gsflow.log .\model\EastFork\output\future_highfreq\hifreq /y
xcopy statvar_hifreq.dat .\model\EastFork\output\future_highfreq\hifreq /y
xcopy prms_hifreq.out .\model\EastFork\output\future_highfreq\hifreq /y

del gsflow.log
del prms_ic.out
del prms_hifreq.out
del statvar_hifreq.dat

REM PRMS East Fork future lo freq
copy bin\gsflow.exe .
copy model\EastFork\input\future_highfreq\lofreq\east_fork.param .
copy model\EastFork\input\future_highfreq\lofreq\eastfork_lofreq.control .
copy model\EastFork\input\future_highfreq\lofreq\upperCarson_lowfreq.data .

gsflow.exe eastfork_lofreq.control

del upperCarson_lowfreq.data
del eastfork_lofreq.control
del east_fork.param
del gsflow.exe

xcopy gsflow.log .\model\EastFork\output\future_highfreq\lofreq /y
xcopy statvar_lofreq.dat .\model\EastFork\output\future_highfreq\lofreq /y
xcopy prms_lofreq.out .\model\EastFork\output\future_highfreq\lofreq /y

del gsflow.log
del prms_ic.out
del prms_lofreq.out
del statvar_lofreq.dat

pause

REM PRMS East Fork future low freq orig?
copy bin\gsflow.exe .
copy model\EastFork\input\future_lowfreq_orig\east_fork.param .
copy model\EastFork\input\future_lowfreq_orig\eastfork_scen2_lofreq.control .
copy model\EastFork\input\future_lowfreq_orig\upperCarson_scen2_lowfreq.data .

gsflow.exe eastfork_scen2_lofreq.control

del upperCarson_scen2_lowfreq.data
del eastfork_scen2_lofreq.control
del east_fork.param
del gsflow.exe

xcopy gsflow.log .\model\EastFork\output\future_lowfreq_orig /y
xcopy statvar_scen2_lowfreq.dat .\model\EastFork\output\future_lowfreq_orig /y
xcopy prms_scen2_lowfreq.out .\model\EastFork\output\future_lowfreq_orig /y

del gsflow.log
del prms_ic.out
del prms_scen2_lowfreq.out
del statvar_scen2_lowfreq.dat

pause


REM PRMS West Fork historical 
copy bin\gsflow.exe .
copy model\WestFork\input\historical\west_fork.param .
copy model\WestFork\input\historical\westfork_hist.control .
copy model\WestFork\input\historical\upper_carson_hist.data .

gsflow.exe westfork_hist.control

del upper_carson_hist.data
del westfork_hist.control
del west_fork.param
del gsflow.exe

xcopy gsflow.log .\model\WestFork\output\historical /y
xcopy statvar_hist.dat .\model\WestFork\output\historical /y
xcopy prms_hist.out .\model\WestFork\output\historical /y

del gsflow.log
del prms_ic.out
del prms_hist.out
del statvar_hist.dat

pause

REM PRMS West Fork historical with warming
copy bin\gsflow.exe .
copy model\WestFork\input\historical_warm\west_fork.param .
copy model\WestFork\input\historical_warm\westfork_hist_warm.control .
copy model\WestFork\input\historical_warm\upper_carson_hist_warm.data .

gsflow.exe westfork_hist_warm.control

del upper_carson_hist_warm.data
del westfork_hist_warm.control
del west_fork.param
del gsflow.exe

xcopy gsflow.log .\model\WestFork\output\historical_warm /y
xcopy statvar_hist_warm.dat .\model\WestFork\output\historical_warm /y
xcopy prms_hist_warm.out .\model\WestFork\output\historical_warm /y

del gsflow.log
del prms_ic.out
del prms_hist_warm.out
del statvar_hist_warm.dat

pause

REM PRMS West Fork future hi freq 
copy bin\gsflow.exe .
copy model\WestFork\input\future_highfreq\hifreq\west_fork.param .
copy model\WestFork\input\future_highfreq\hifreq\westfork_hifreq.control .
copy model\WestFork\input\future_highfreq\hifreq\upperCarson_highfreq.data .

gsflow.exe westfork_hifreq.control

del upperCarson_highfreq.data
del westfork_hifreq.control
del west_fork.param
del gsflow.exe

xcopy gsflow.log .\model\WestFork\output\future_highfreq\hifreq /y
xcopy statvar_hifreq.dat .\model\WestFork\output\future_highfreq\hifreq /y
xcopy prms_hifreq.out .\model\WestFork\output\future_highfreq\hifreq /y

del gsflow.log
del prms_ic.out
del prms_hifreq.out
del statvar_hifreq.dat

pause

REM PRMS West Fork future lo freq 
copy bin\gsflow.exe .
copy model\WestFork\input\future_highfreq\lofreq\west_fork.param .
copy model\WestFork\input\future_highfreq\lofreq\westfork_lofreq.control .
copy model\WestFork\input\future_highfreq\lofreq\upperCarson_lofreq.data .

gsflow.exe westfork_lofreq.control

del upperCarson_lofreq.data
del westfork_lofreq.control
del west_fork.param
del gsflow.exe

xcopy gsflow.log .\model\WestFork\output\future_highfreq\lofreq /y
xcopy statvar_lofreq.dat .\model\WestFork\output\future_highfreq\lofreq /y
xcopy prms_lofreq.out .\model\WestFork\output\future_highfreq\lofreq /y

del gsflow.log
del prms_ic.out
del prms_lofreq.out
del statvar_lofreq.dat

pause

REM PRMS West Fork future low freq orig
copy bin\gsflow.exe .
copy model\WestFork\input\future_lowfreq_orig\west_fork.param .
copy model\WestFork\input\future_lowfreq_orig\westfork_scen2.control .
copy model\WestFork\input\future_lowfreq_orig\upperCarson_scen2_lowfreq.data .

gsflow.exe westfork_scen2.control

del upperCarson_scen2_lowfreq.data
del westfork_scen2.control
del west_fork.param
del gsflow.exe

xcopy gsflow.log .\model\WestFork\output\future_lowfreq_orig /y
xcopy statvar_lowfreq.dat .\model\WestFork\output\future_lowfreq_orig /y
xcopy prms_lowfreq.out .\model\WestFork\output\future_lowfreq_orig /y

del gsflow.log
del prms_ic.out
del prms_lowfreq.out
del statvar_lowfreq.dat

pause




