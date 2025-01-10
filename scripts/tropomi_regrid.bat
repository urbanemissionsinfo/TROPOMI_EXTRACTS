@echo off
for /f %%i in ('powershell -command "(\"%pollutant%\").ToUpper()"') do set uppercasePollutant=%%i

CALL conda activate gdal
start /wait python scripts/regrid.py INDIA %uppercasePollutant% monthly
conda deactivate