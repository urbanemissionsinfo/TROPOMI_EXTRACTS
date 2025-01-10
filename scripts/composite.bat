@echo off
@REM echo %1
for /f %%i in ('powershell -command "(\"%pollutant%\").ToUpper()"') do set uppercasePollutant=%%i

CALL venv/Scripts/activate
start python scripts/extent_grids_composite.py INDIA %uppercasePollutant% monthly
