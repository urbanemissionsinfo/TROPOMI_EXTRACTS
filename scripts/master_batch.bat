set /p pollutant=Enter pollutant: 

@REM call scripts\tropomi_extract.bat %pollutant%
call scripts\tropomi_regrid.bat %pollutant%
call scripts\composite.bat %pollutant%