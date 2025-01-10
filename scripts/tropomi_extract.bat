@echo off
@REM echo %1
for /f %%i in ('powershell -command "(\"%pollutant%\").ToUpper()"') do set uppercasePollutant=%%i

CALL venv/Scripts/activate
start python scripts/tropomi_extract_monthly.py  %uppercasePollutant% 2019
start python scripts/tropomi_extract_monthly.py  %uppercasePollutant% 2020
start python scripts/tropomi_extract_monthly.py  %uppercasePollutant% 2021
start python scripts/tropomi_extract_monthly.py  %uppercasePollutant% 2022
start python scripts/tropomi_extract_monthly.py  %uppercasePollutant% 2023
start python scripts/tropomi_extract_monthly.py  %uppercasePollutant% 2024
call deactivate

:wait
tasklist | find /i "python.exe" >nul
if %errorlevel%==0 (
    timeout /t 1 >nul
    goto wait
)

exit
@REM # conda activate gdal
@REM # python scripts/regrid.py INDIA NO2 monthly
@REM # conda deactivate
@REM # venv\Scripts\activate
@REM # python scripts/extent_grids_composite.py INDIA NO2 monthly
@REM # python scripts/grid_maps.py INDIA NO2 monthly