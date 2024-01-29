; Regrids NO2 columns to a 0.01 x 0.01 degree  grid
;-----------------------------------------------------------------------------------
;Define Input variables

input_directory='/home/krishna/UEInfo/TROPOMI_EXTRACTS/data/GDL_Data'  ;MUST change this directory!
output_directory='/home/krishna/UEInfo/TROPOMI_EXTRACTS/data/GDL_Data' ;MUST change this directory!

domain_name='India'
gridsize=0.01   ;Must be smaller than 0.04, ideally equal to or smaller than 0.01
min_lat_domain=7
max_lat_domain=39
min_lon_domain=67
max_lon_domain=99

offl=1
;0 for Near-Real-Time (NRTl) files
;1 for Offline (OFFL) files (including RPRO & PAL files)

qa_filtering=0.75
;0.75 is typically used, 0.5 is sometimes used alternatively; this value can be set between 0 - 1. 1 restricts to "perfect" data, 0 yields no restriction

startmonth=1 ;1 for January 7 for July, etc.
nummonths=12 ;Number of consecutive months you would like the code to run for

startyear=2019
numyears=1   ;Number of consecutive year(s) you would like the code to run for, 1=start year only, 2=startyear plus next year, etc.

full_month=1
;0 to manually set the days to loop through by defining firstday and lastday variables (see below)
;1 for full month
firstday=1
lastday=1

output_latlon=1
;0 for no output
;1 for yes output

;-----------------------------------------------------------------------------------

;Initialize arrays
monthdate=['01','02','03','04','05','06','07','08','09','10','11','12']
monthname=['Jan','Feb','March','April','May','June','July','Aug','Sept','Oct','Nov','Dec']
date=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
qa_filtering=qa_filtering*100.0

if startmonth+nummonths gt 13 then print,'Number of consecutive months exceeds the number of months in the year'
if startmonth+nummonths gt 13 then stop
;------------------------------------------------------
;Create lat-lon grid

num_xlon=(max_lon_domain-min_lon_domain)/gridsize
num_xlat=num_xlon
num_ylat=(max_lat_domain-min_lat_domain)/gridsize
num_ylon=num_ylat

lat_model_1d=(findgen(num_ylat)*gridsize)+min_lat_domain
lon_model_1d=(findgen(num_xlon)*gridsize)+min_lon_domain

;Create output lat-lon file
if output_latlon eq 1 then begin 
id = NCDF_CREATE(''+output_directory+'LatLonGrid_'+domain_name+'.ncf', /CLOBBER)
NCDF_CONTROL, id, /FILL
xid = NCDF_DIMDEF(id, 'x', num_xlon)
yid = NCDF_DIMDEF(id, 'y', num_ylat)
NCDF_ATTPUT, id, /GLOBAL, 'Title', 'Latitudes and Longitudes for TROPOMI 0.01 x 0.01 grid'
aid = NCDF_VARDEF(id, 'LON', [xid], /FLOAT)
NCDF_ATTPUT, id, aid, 'units', 'degrees East'
bid = NCDF_VARDEF(id, 'LAT', [yid], /FLOAT)
NCDF_ATTPUT, id, bid, 'long_name', 'degrees North'
NCDF_CONTROL, id, /ENDEF
NCDF_VARPUT, id, aid, lon_model_1d
NCDF_VARPUT, id, bid, lat_model_1d
NCDF_CLOSE, id ; Close the NetCDF file.
endif

lat_min=min(lat_model_1d)
lat_max=max(lat_model_1d)
lon_min=min(lon_model_1d)
lon_max=max(lon_model_1d)

;----------------------------------------------------------
;Begin loops for each month and day
for yr=startyear,startyear+(numyears-1) do begin
yearname=string(yr,FORMAT='(I4)')

;----------------------------------------------------------

for month=startmonth-1,(startmonth-1)+(nummonths-1) do begin

numdays=31
if month eq (4-1) or month eq (6-1) or month eq (9-1) or month eq (11-1) then numdays=30
if month eq (2-1) then numdays=28
if month eq (2-1) and yr eq 2004 then numdays=29
if month eq (2-1) and yr eq 2008 then numdays=29
if month eq (2-1) and yr eq 2012 then numdays=29
if month eq (2-1) and yr eq 2016 then numdays=29
if month eq (2-1) and yr eq 2020 then numdays=29
if month eq (2-1) and yr eq 2024 then numdays=29
if month eq (2-1) and yr eq 2028 then numdays=29

if full_month eq 1 then begin
firstday=1
lastday=numdays
endif

for day=firstday-1,lastday-1 do begin

no2_satellite=fltarr(1e7)
pos_x=fltarr(1e7)
pos_y=fltarr(1e7)
no2_satellite(*)=-999.0
pos_x(*)=-999.0
pos_y(*)=-999.0
count_daily=dblarr(1)

count_previous=0

;Begin to read in files
if offl eq 1 then begin
filename_result=file_search(''+input_directory+'S5P*OFFL*L2*NO2*'+yearname+''+monthdate(month)+''+date(day)+'T*'+yearname+''+monthdate(month)+''+date(day)+'T*.nc',count=numfiles)
if numfiles eq 0 then filename_result=file_search(''+input_directory+'S5P*RPRO*L2*NO2*'+yearname+''+monthdate(month)+''+date(day)+'T*'+yearname+''+monthdate(month)+''+date(day)+'T*.nc',count=numfiles)
if numfiles eq 0 then filename_result=file_search(''+input_directory+'S5P*PAL*L2*NO2*'+yearname+''+monthdate(month)+''+date(day)+'T*'+yearname+''+monthdate(month)+''+date(day)+'T*.nc',count=numfiles)
endif

if offl eq 0 then filename_result=file_search(''+input_directory+'S5P*NRT*L2*NO2*'+yearname+''+monthdate(month)+''+date(day)+'T*'+yearname+''+monthdate(month)+''+date(day)+'T*.nc',count=numfiles)

if numfiles eq 0 then print,'No files found for '+monthname(month)+' '+date(day)+', '+yearname+''
if numfiles eq 0 then goto,SKIPDAY

print,'Files to be read-in'
print,filename_result
stop

for n=0,numfiles-1 do begin

filename=filename_result(n)
print, filename

length_directory=(strlen(input_directory))/1.0
substring=strmid(filename,length_directory+29.0,4)    ;This extracts the closest hour to the observation
hour=float(substring)
hour=hour/100.0
hour=round(hour)
print,'Approximate hour:',hour,' Z'

;----------------------------------------------------------
;Read-in variables

fid = h5f_open(filename)
pathname = '/PRODUCT/'
varname='nitrogendioxide_tropospheric_column'
id = h5d_open(fid, pathname + varname)
tropno2 = h5d_read(id)
h5d_close, id
invalid=where(tropno2 gt 1e20)
tropno2(invalid)=!values.f_nan
tvc=tropno2*6.02214*(10.0^19.0)   ;Convert from mol/m2 to molecules per cm2

pathname = '/PRODUCT/'
varname='latitude'
id = h5d_open(fid, pathname + varname)
latitudes = h5d_read(id)
h5d_close, id

pathname = '/PRODUCT/'
varname='longitude'
id = h5d_open(fid, pathname + varname)
longitudes = h5d_read(id)
h5d_close, id

pathname = '/PRODUCT/'
varname='qa_value'
id = h5d_open(fid, pathname + varname)
qa_value = h5d_read(id)
h5d_close, id

pathname = '/PRODUCT/SUPPORT_DATA/GEOLOCATIONS/'
varname='latitude_bounds'
id = h5d_open(fid, pathname + varname)
latitude_corners = h5d_read(id)
h5d_close, id

pathname = '/PRODUCT/SUPPORT_DATA/GEOLOCATIONS/'
varname='longitude_bounds'
id = h5d_open(fid, pathname + varname)
longitude_corners = h5d_read(id)
h5d_close, id

h5f_close, fid

;----------------------------------------------------------
;Filter data
result=where(latitudes gt lat_min and latitudes lt lat_max and longitudes lt lon_max and longitudes gt lon_min and qa_value ge qa_filtering, count)

if count(0) lt 1 then goto, JUMP

;----------------------------------------------------------
;Store only data at lat/long of relevance

;Initialize arrays
lats=fltarr(count)
longs=fltarr(count)
lat_corner3=fltarr(count)
lat_corner2=fltarr(count)
lat_corner4=fltarr(count)
lat_corner1=fltarr(count)
long_corner3=fltarr(count)
long_corner2=fltarr(count)
long_corner4=fltarr(count)
long_corner1=fltarr(count)

tropcolumns=fltarr(count)

;Start loop to store valid satellite data roughly within the domain of interest
for ii=0,count-1 do begin
lats(ii)=latitudes(result(ii))
longs(ii)=longitudes(result(ii))

pos1=array_indices(latitudes,result(ii))   ;Array indicies of lat/lon of interest

lat_corner1(ii)=latitude_corners(0,pos1(0),pos1(1))
lat_corner2(ii)=latitude_corners(1,pos1(0),pos1(1))
lat_corner3(ii)=latitude_corners(2,pos1(0),pos1(1))
lat_corner4(ii)=latitude_corners(3,pos1(0),pos1(1))
long_corner1(ii)=longitude_corners(0,pos1(0),pos1(1))
long_corner2(ii)=longitude_corners(1,pos1(0),pos1(1))
long_corner3(ii)=longitude_corners(2,pos1(0),pos1(1))
long_corner4(ii)=longitude_corners(3,pos1(0),pos1(1))

tropcolumns(ii)=tvc(pos1(0),pos1(1))

endfor  ;End 'ii' loop, # of of valid satellite datapoints

;-------------------------------------------------------------------------------------
;Find satellite data within the domain and match to closest model grid cell

for ii=0,count-1 do begin    ;For each lat/long point with VALID satellite data

result_lat=where(lat_model_1d ge lats(ii)-0.2 and lat_model_1d le lats(ii)+0.2,countlat)
result_lon=where(lon_model_1d ge longs(ii)-0.2 and lon_model_1d le longs(ii)+0.2,countlon)

;-------------------------------------------------------------------------------------
;Determine whether model gridpoint is within satellite pixel
for iii=0,countlon-1 do begin  ;For each model gridpoint with 0.5 degrees of the VALID satellite data
for jjj=0,countlat-1 do begin

;Right bounds
y1=lat_corner3(ii)
y2=lat_corner2(ii)
x1=long_corner3(ii)
x2=long_corner2(ii)
x=lon_model_1d(result_lon(iii))
y=((y2-y1)/(x2-x1))*(x-x1)+y1
if lat_model_1d(result_lat(jjj)) gt y then goto, SKIP

;Left bounds
y1=lat_corner4(ii)
y2=lat_corner1(ii)
x1=long_corner4(ii)
x2=long_corner1(ii)
x=lon_model_1d(result_lon(iii))
y=((y2-y1)/(x2-x1))*(x-x1)+y1
if lat_model_1d(result_lat(jjj)) lt y then goto, SKIP

;Top bounds
y1=lat_corner3(ii)
y2=lat_corner4(ii)
x1=long_corner3(ii)
x2=long_corner4(ii)
y=lat_model_1d(result_lat(jjj))
x=((x2-x1)/(y2-y1))*(y-y1)+x1
if lon_model_1d(result_lon(iii)) lt x then goto, SKIP

;Bottom bounds
y1=lat_corner2(ii)
y2=lat_corner1(ii)
x1=long_corner2(ii)
x2=long_corner1(ii)
y=lat_model_1d(result_lat(jjj))
x=((x2-x1)/(y2-y1))*(y-y1)+x1
if lon_model_1d(result_lon(iii)) gt x then goto, SKIP

pos2=intarr(2)
pos2(0)=result_lon(iii)
pos2(1)=result_lat(jjj)

;-------------------------------------------------------------------------------------
;Store NO2 column and other relevant data at appropriate gridpoint
no2_satellite(count_daily)=tropcolumns(ii)
pos_x(count_daily)=pos2(0)
pos_y(count_daily)=pos2(1)

count_daily=count_daily+1.0
SKIP:
endfor  ;End 'jjj' loop
endfor  ;End 'iii' loop

endfor  ;End 'ii' loop

count_previous=count
JUMP:
if count eq 0 then print, 'No satellite data within the domain, moving to next file'
SKIPFILEDAY:

print,count_daily
endfor ;End 'n' loop (# of files)

valid=where(no2_satellite ne -999.0,count_valid)
no2_satellite=no2_satellite(valid)
pos_x=pos_x(valid)
pos_y=pos_y(valid)
print,'# of total regridded gridpoints: ',count_valid

if count_valid eq 0 then print,'No data within the defined domain for '+monthname(month)+' '+date(day)+', '+yearname+''
if count_valid eq 0 then goto,SKIPDAY
;----------------------------------------------------------
;Create a new NetCDF file
if gridsize ge 0.01 then gridsize_string=string(gridsize,FORMAT='(F4.2)')
if gridsize lt 0.01 and gridsize ge 0.001 then gridsize_string=string(gridsize,FORMAT='(F5.3)')
qa_string=string((qa_filtering/100.0),FORMAT='(F4.2)')

id = NCDF_CREATE(''+output_directory+'Tropomi_NO2_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_'+monthdate(month)+''+date(day)+''+yearname+'_QA'+qa_string+'.nc', /CLOBBER)

; Fill the file with default values:
NCDF_CONTROL, id, /FILL

;Make dimensions
nid = NCDF_DIMDEF(id, 'n', count_daily+1)

; Define variables:
NCDF_ATTPUT, id, /GLOBAL, 'Title', 'Gridded Tropospheric NO2 Column for '+monthname(month)+' '+date(day)+', '+yearname+''

aid = NCDF_VARDEF(id, 'NO2', [nid], /FLOAT)
NCDF_ATTPUT, id, aid, 'units', 'molecules/cm2'
NCDF_ATTPUT, id, aid, 'long_name', 'TROPOMI Tropospheric Vertical NO2 Column'

bid = NCDF_VARDEF(id, 'x_pos', [nid], /FLOAT)
NCDF_ATTPUT, id, bid, 'long_name', 'x position'

cid = NCDF_VARDEF(id, 'y_pos', [nid], /FLOAT)
NCDF_ATTPUT, id, cid, 'long_name', 'y position'

; Put file in data mode:
NCDF_CONTROL, id, /ENDEF

; Input data:
NCDF_VARPUT, id, aid, no2_satellite
NCDF_VARPUT, id, bid, pos_x
NCDF_VARPUT, id, cid, pos_y

NCDF_CLOSE, id ; Close the NetCDF file.

print,'Files for '+monthname(month)+' '+date(day)+', '+yearname+'  successfully re-gridded'
SKIPDAY:
;print,day+1
endfor ;End 'day' loop
endfor ;End 'month' loop
endfor ;End 'yr' loop

end