This directory includes a subdirectory containing files used for calibration (pest) and scripts for pre-processing data to create input files and post-processing model results.

    pest:
    
        This directory contains files used for history matching using the
        iterative ensemble smoother process in the PESTPP suite, ipestpp-
        ies.exe version 4.2.14 (found in \bin), including a pest control files.
        The subdirectories include: instruction files (ins), template files
        (tpl), initial and final observation ensembles (obs), and initial and
        final parameter ensembles (pars).
        
    python:
    
        This directory contains python scripts and ipython notebooks for pre-
        and post-processing data. All python scripts and ipython notebooks were
        written in python 3.6.6 with pandas 0.25.0.
            
        ag_builder.py: 
    
            creates input files for the AG package from an input file (CV-wes-
            8015trans-irrigation.txt) describing irrigation practices such as
            water demand, priority year, and supplemental pumping. Requires
            CV_tools.py to process the time series using pandas
            
        sim_*:
        
            post processing scripts to convert data from water rights (wrts),
            stream flows (flows), and the budget printed to the listing file
            (list). Requires CV_tools.py to process the time series data using
            pandas.
            
        Maps_0.ipynb:
        
            ipython notebook used to create maps (and raster data) of head and
            drawdown for each scenario.
            
        post_proc_dT_0.ipynb:
            
            ipython notebook used to process results for each water right and
            stream flows into and out of Carson Valley for each temperature
            scenario.
            
    Carson Valley:
    
        subdirectory containing shapefiles for the integrated Carson Valley MODSIM-GSFLOW model domain
        
    East Fork:
        subdirectory containing shapefiles for the East Fork GSFLOW model domain
        
    West Fork:
        subdirectory containing shapefiles for the West Fork GSFLOW model domain