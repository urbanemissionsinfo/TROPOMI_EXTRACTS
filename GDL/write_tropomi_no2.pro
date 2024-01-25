;Takes an average of specifc days/months

;Define Input variables
input_directory='G:\Goldberg\TROPOMI\V2\'  ;MUST change this directory!
output_directory='G:\Goldberg\TROPOMI\V2\' ;MUST change this directory!

domain_name='India'
gridsize=0.01   ;Must be smaller than 0.04, ideally equal to or smaller than 0.01
min_lat_domain=7
max_lat_domain=39
min_lon_domain=67
max_lon_domain=99

timescale=0
;0 for any
;1 for year-specific
;2 for month- and year-specific (can modify start and end months below)
if timescale ge 1 then yearname='2019' ;Define which year
if timescale eq 2 then monthstart='01' ;Define which month to start at
if timescale eq 2 then monthend='12'   ;Define which month to end at

nr=0
;0 for NO2
;1 for HCHO
;2 for CO
;3 for CH4

qa_filtering=0.75
;0.75 is typically used, 0.5 is sometimes used alternatively; this value can be set between 0 - 1. 1 resticts to "perfect" data, 0 yields no restriction

;------------------------------------------------------
;Initialize arrays
monthdate=['01','02','03','04','05','06','07','08','09','10','11','12']
monthname=['Jan','Feb','March','April','May','June','July','Aug','Sept','Oct','Nov','Dec']
date=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
qa_filtering=qa_filtering*100.0

if timescale le 1 then loop=0
if timescale eq 2 then begin
  monthstart_num=monthstart_num/1.0
  monthend_num=monthend_num/1.0
  loop=monthend_num-monthstart_num
  if loop lt 0 then print,'Month end date must be after month start date'
  if loop lt 0 then stop
endif

for l=0,loop do begin
  monthdate_loop=monthdate(l+monthstart_num-1)
;------------------------------------------------------
;Create lat-lon grid

num_xlon=(max_lon_domain-min_lon_domain)/gridsize
num_xlat=num_xlon
num_ylat=(max_lat_domain-min_lat_domain)/gridsize
num_ylon=num_ylat

  lat_1d=(findgen(num_ylat)*gridsize)+min_lat_domain+(gridsize/2.0)
  lon_1d=(findgen(num_xlon)*gridsize)+min_lon_domain+(gridsize/2.0)

  lat_min=min(lat_1d)
  lat_max=max(lat_1d)
  lon_min=min(lon_1d)
  lon_max=max(lon_1d)

;-----------------------------------------------------
;Define storage arrays
        tropomi=fltarr(num_xlat,num_ylon)
        tropomi_temporary=fltarr(num_xlat,num_ylon)
        count_array=fltarr(num_xlat,num_ylon)

;----------------------------------------------------------
        ;Find all relevant files
        if gridsize ge 0.01 then gridsize_string=string(gridsize,FORMAT='(F4.2)')
        if gridsize lt 0.01 and gridsize ge 0.001 then gridsize_string=string(gridsize,FORMAT='(F5.3)')
        qa_string=string((qa_filtering/100.0),FORMAT='(F4.2)')

        if timescale eq 0 then begin
          if nr eq 0 then filename_result=file_search(''+output_directory+'Tropomi_NO2_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_*_QA'+qa_string+'.nc',count=numfiles)
          if nr eq 1 then filename_result=file_search(''+output_directory+'Tropomi_HCHO_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_*_QA'+qa_string+'.nc',count=numfiles)
          if nr eq 2 then filename_result=file_search(''+output_directory+'Tropomi_CO_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_*_QA'+qa_string+'.nc',count=numfiles)
          if nr eq 3 then filename_result=file_search(''+output_directory+'Tropomi_CH4_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_*_QA'+qa_string+'.nc',count=numfiles)
        endif
        
        if timescale eq 1 then begin
          if nr eq 0 then filename_result=file_search(''+output_directory+'Tropomi_NO2_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_*'+yearname+'_QA'+qa_string+'.nc',count=numfiles)
          if nr eq 1 then filename_result=file_search(''+output_directory+'Tropomi_HCHO_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_*'+yearname+'_QA'+qa_string+'.nc',count=numfiles)
          if nr eq 2 then filename_result=file_search(''+output_directory+'Tropomi_CO_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_*'+yearname+'_QA'+qa_string+'.nc',count=numfiles)
          if nr eq 3 then filename_result=file_search(''+output_directory+'Tropomi_CH4_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_*'+yearname+'_QA'+qa_string+'.nc',count=numfiles)
        endif
        
        if timescale eq 2 then begin
          if nr eq 0 then filename_result=file_search(''+output_directory+'Tropomi_NO2_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_*'+monthdate_loop+'*'+yearname+'_QA'+qa_string+'.nc',count=numfiles)
          if nr eq 1 then filename_result=file_search(''+output_directory+'Tropomi_HCHO_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_*'+monthdate_loop+'*'+yearname+'_QA'+qa_string+'.nc',count=numfiles)
          if nr eq 2 then filename_result=file_search(''+output_directory+'Tropomi_CO_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_*'+monthdate_loop+'*'+yearname+'_QA'+qa_string+'.nc',count=numfiles)
          if nr eq 3 then filename_result=file_search(''+output_directory+'Tropomi_CH4_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_*'+monthdate_loop+'*'+yearname+'_QA'+qa_string+'.nc',count=numfiles)
        endif
        
        count_previous=0
        print,''+output_directory+'Tropomi_NO2_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_*'+yearname+'_QA'+qa_string+'.ncf'
        if numfiles eq 0 then print, 'Cannot find satellite data for this period'
        if numfiles eq 0 then stop
        print,'# of files: ',numfiles
;        stop
        ;----------------------------------------------------------------------------------------------------------
        ;Begin to read files
        for n=0,numfiles-1 do begin
          
          filename_satellite=filename_result(n)
          print, filename_satellite
          sf=0 ;Skip file flag
          
          cdfid=ncdf_open(filename_satellite)
          if nr eq 0 then  ncdf_varget,cdfid,'NO2',tg_satellite
          if nr eq 1 then  ncdf_varget,cdfid,'HCHO',tg_satellite
          if nr eq 2 then  ncdf_varget,cdfid,'CO',tg_satellite
          if nr eq 3 then  ncdf_varget,cdfid,'CH4',tg_satellite
          ncdf_varget,cdfid,'x_pos',xcoord
          ncdf_varget,cdfid,'y_pos',ycoord
          ncdf_close,cdfid

          tg_satellite=tg_satellite/1.0e15

          ;--------------------------------------------------------------------------------------------
          ;Open and store TROPOMI satellite gridded product

          valid_pixels=where(tg_satellite lt 100.0,num_pixels)
          if num_pixels le 1 then sf=1
          if sf eq 0 then begin
          for ii=0,num_pixels-1 do begin
            tropomi_temporary(xcoord(valid_pixels(ii)),ycoord(valid_pixels(ii)))=tropomi_temporary(xcoord(valid_pixels(ii)),ycoord(valid_pixels(ii)))+tg_satellite(valid_pixels(ii))
            count_array(xcoord(valid_pixels(ii)),ycoord(valid_pixels(ii)))=count_array(xcoord(valid_pixels(ii)),ycoord(valid_pixels(ii)))+1.0
          endfor
          endif
          
          ;------------------------------------------------------------
          ;stop

          print,'Looping through file #: ',n+1
        endfor ;End 'n' loop (# of files)
        print,'Avg # of days of with data: ',mean(count_array)

        for i=0,num_xlat-1 do begin
          for j=0,num_ylon-1 do begin
            tropomi(i,j)=tropomi_temporary(i,j)/count_array(i,j)
          endfor
        endfor

        if nr le 2 then tropomi=tropomi*1.0e15
        ;stop

        ;------------------------------------------------------------------------

        ;Create a new NetCDF file
        if timescale eq 0 then begin
          if nr eq 0 then id = NCDF_CREATE(''+output_directory+'Tropomi_NO2_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_QA'+qa_string+'.ncf', /CLOBBER)
          if nr eq 1 then id = NCDF_CREATE(''+output_directory+'Tropomi_HCHO_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_QA'+qa_string+'.ncf', /CLOBBER)
          if nr eq 2 then id = NCDF_CREATE(''+output_directory+'Tropomi_CO_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_QA'+qa_string+'.ncf', /CLOBBER)
          if nr eq 3 then id = NCDF_CREATE(''+output_directory+'Tropomi_CH4_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_QA'+qa_string+'.ncf', /CLOBBER)
        endif
        
        if timescale eq 1 then begin
          if nr eq 0 then id = NCDF_CREATE(''+output_directory+'Tropomi_NO2_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_'+yearname+'_QA'+qa_string+'.ncf', /CLOBBER)
          if nr eq 1 then id = NCDF_CREATE(''+output_directory+'Tropomi_HCHO_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_'+yearname+'_QA'+qa_string+'.ncf', /CLOBBER)
          if nr eq 2 then id = NCDF_CREATE(''+output_directory+'Tropomi_CO_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_'+yearname+'_QA'+qa_string+'.ncf', /CLOBBER)
          if nr eq 3 then id = NCDF_CREATE(''+output_directory+'Tropomi_CH4_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_'+yearname+'_QA'+qa_string+'.ncf', /CLOBBER)
        endif
        
        if timescale eq 2 then begin
          if nr eq 0 then id = NCDF_CREATE(''+output_directory+'Tropomi_NO2_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_'+monthdate_loop+''+yearname+'_QA'+qa_string+'.ncf', /CLOBBER)
          if nr eq 1 then id = NCDF_CREATE(''+output_directory+'Tropomi_HCHO_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_'+monthdate_loop+''+yearname+'_QA'+qa_string+'.ncf', /CLOBBER)
          if nr eq 2 then id = NCDF_CREATE(''+output_directory+'Tropomi_CO_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_'+monthdate_loop+''+yearname+'_QA'+qa_string+'.ncf', /CLOBBER)
          if nr eq 3 then id = NCDF_CREATE(''+output_directory+'Tropomi_CH4_griddedon'+gridsize_string+'x'+gridsize_string+'grid_'+domain_name+'_'+monthdate_loop+''+yearname+'_QA'+qa_string+'.ncf', /CLOBBER)
        endif
        ; Fill the file with default values:
        NCDF_CONTROL, id, /FILL

        ;Make dimensions
        xid = NCDF_DIMDEF(id, 'x', num_xlat)
        yid = NCDF_DIMDEF(id, 'y', num_ylon)

        ; Define variables:
        NCDF_ATTPUT, id, /GLOBAL, 'Title', 'Re-gridded TROPOMI filtered with a QA flag of 0.75'

        if nr eq 0 then aid = NCDF_VARDEF(id, 'NO2', [xid,yid], /FLOAT)
        if nr eq 1 then aid = NCDF_VARDEF(id, 'HCHO', [xid,yid], /FLOAT)
        if nr eq 2 then aid = NCDF_VARDEF(id, 'CO', [xid,yid], /FLOAT)
        if nr eq 3 then aid = NCDF_VARDEF(id, 'CH4', [xid,yid], /FLOAT)
        
        if nr le 2 then NCDF_ATTPUT, id, aid, 'units', 'molecules/cm2'
        if nr eq 3 then NCDF_ATTPUT, id, aid, 'units', 'ppb'
        
        bid = NCDF_VARDEF(id, 'latitude', [yid], /FLOAT)
        NCDF_ATTPUT, id, bid, 'units', 'degrees N'
        
        cid = NCDF_VARDEF(id, 'longitude', [xid], /FLOAT)
        NCDF_ATTPUT, id, cid, 'units', 'degrees E'
        
        ; Put file in data mode:
        NCDF_CONTROL, id, /ENDEF

        ; Input data:
        NCDF_VARPUT, id, aid, tropomi
        NCDF_VARPUT, id, bid, lat_1d
        NCDF_VARPUT, id, cid, lon_1d

        NCDF_CLOSE, id ; Close the NetCDF file.

  endfor
  end