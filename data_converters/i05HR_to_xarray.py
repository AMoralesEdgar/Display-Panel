#Functions to load data from the I05-HR beamline into an xarray, or for the logbook maker
#Phil King 11/01/2021
#Brendan Edwards 09/02/2021

import numpy as np
import xarray as xr
import nexusformat.nexus as nf

def load_i05HR_data(file, **kwargs):
    '''This function loads ARPES data from I05-HR beamline
    
    Input:
        file - Path to the file to be loaded (string)
        **kwargs - Additional slicing options for partial loading of data or for binning on load (strings)
    
    Returns:
        data - DataArray or DataSet with loaded data (xarray)'''

    #open the file (read only)
    f = nf.nxload(file, 'r')
    
    #check scan is from Diamond I05-HR
    if f.entry1.instrument.name.nxvalue != 'i05':
        raise Exception("File "+file+" does not appear to be from I05-HR branch. Please check.")
    
    #list the analyser_keys: this is a useful entry in the Diamond .nxs files which shows what is a variable co-ordinate in the scan vs. static metadata
    analyser_keys = list(f['entry1/analyser/'].keys())

    #read some core data from file
    spectrum = f.entry1.instrument.analyser.data.nxvalue #the actual (cube) of measured spectra
    theta = f.entry1.instrument.analyser.angles.nxvalue #the analyser angle scale readout

    #determine type of scan from heirarchy of driven/secondary axes and load data accordingly
    #note: deflector scans not yet implemented
    if 'energy' in analyser_keys: #should be a photon energy scan
        raise Exception("File "+file+" appears to be an hv scan. This is not yet implemented.")
        data = []
        scan_type = "hv scan"
        #this needs more thought, probably need to use a DataSet not DataArray for this one to keen the detector data in KE
        
    else: #for all other scan types, the KE measured on the detector shouldn't be varying across the scan files
        KE_values = f.entry1.instrument.analyser.energies.nxvalue
        if 'sapolar' in analyser_keys: #should be a FS manipulator polar map
            sapolar = f.entry1.instrument.manipulator.sapolar.nxvalue #extract the polar mapping dimension
            #create a DataArray with the measured map 
            data = xr.DataArray(spectrum, dims=("theta_perp","theta_par","eV"), coords={"theta_perp": sapolar, "theta_par": theta, "eV": KE_values})
            data.coords['theta_perp'].attrs = {'units' : 'deg'}
            data.coords['theta_par'].attrs = {'units' : 'deg'}
            scan_type = "FS map"
    
        elif 'salong' in analyser_keys: #should be a focus scan
            salong = f.entry1.instrument.manipulator.salong.nxvalue #extract the focus co-ordinate (along the beam direction)
            #create a DataArray with the measured map 
            data = xr.DataArray(spectrum, dims=("focus","theta_par","eV"), coords={"focus": salong, "theta_par": theta, "eV": KE_values})
            data.coords['focus'].attrs = {'units' : 'mm'}
            data.coords['theta_par'].attrs = {'units' : 'deg'}
            scan_type = "focus scan"
    
        else:
            if 'saz' in analyser_keys and 'sax' in analyser_keys: #should be a spatial map
                #check which is the heirarchy of the spatial scan co-ordinates (fast and slow axis), extract relevant 1D waves for x and z, and build DataArray
                if f.entry1.instrument.manipulator.sax[1][0].nxvalue > f.entry1.instrument.manipulator.sax[0][0].nxvalue:
                    sax = f.entry1.instrument.manipulator.sax[:,0].nxvalue
                    saz = f.entry1.instrument.manipulator.saz[0,:].nxvalue 
                    #create a DataArray with the measured map, NB, using x/y as per PyPhoto geometry conventions
                    data = xr.DataArray(spectrum, dims=("x1","x2","theta_par","eV"), coords={"x1": sax, "x2": saz, "theta_par": theta, "eV": KE_values})
                    data.coords['x1'].attrs = {'units' : 'mm'}
                    data.coords['x2'].attrs = {'units' : 'mm'}
                    data.coords['theta_par'].attrs = {'units' : 'deg'}
                    scan_type = "spatial map"
                    
                else:
                    sax = f.entry1.instrument.manipulator.sax[0,:].nxvalue
                    saz = f.entry1.instrument.manipulator.saz[:,0].nxvalue
                    #create a DataArray with the measured map, NB, using x/y as per PyPhoto geometry conventions
                    data = xr.DataArray(spectrum, dims=("x2","x1","theta_par","eV"), coords={"x2": saz, "x1": sax, "theta_par": theta, "eV": KE_values})
                    data.coords['x1'].attrs = {'units' : 'mm'}
                    data.coords['x2'].attrs = {'units' : 'mm'}
                    data.coords['theta_par'].attrs = {'units' : 'deg'}
                    scan_type = "spatial map"
            
            elif 'saz' in analyser_keys: #should be a 1D spatial scan
                saz = f.entry1.instrument.manipulator.saz.nxvalue #extract the saz co-ordinate
                data = xr.DataArray(spectrum, dims=("x2","theta_par","eV"), coords={"x2": saz, "theta_par": theta, "eV": KE_values}) #corresponding DataArray
                data.coords['x2'].attrs = {'units' : 'mm'}
                data.coords['theta_par'].attrs = {'units' : 'deg'}
                scan_type = "line scan"
            
            elif 'sax' in analyser_keys: #should be a 1D spatial scan
                sax = f.entry1.instrument.manipulator.sax.nxvalue #extract the sax co-ordinate
                data = xr.DataArray(spectrum, dims=("x1","theta_par","eV"), coords={"x1": sax, "theta_par": theta, "eV": KE_values}) #corresponding DataArray
                data.coords['x1'].attrs = {'units' : 'mm'}
                data.coords['theta_par'].attrs = {'units' : 'deg'}
                scan_type = "line scan"
            
            elif 'say' in analyser_keys: #should be a form of focus scan
                say = f.entry1.instrument.manipulator.say.nxvalue #extract the say co-ordinate
                data = xr.DataArray(spectrum, dims=("x3","theta_par","eV"), coords={"x3": say, "theta_par": theta, "eV": KE_values}) #corresponding DataArray
                data.coords['x3'].attrs = {'units' : 'mm'}
                data.coords['theta_par'].attrs = {'units' : 'deg'}
                scan_type = "focus scan"
            
            elif 'temperature' in analyser_keys: #should be an automated temp-dependence
                temperature = f.entry1.instrument.sample.temperature.nxvalue #extract sample temperature
                data = xr.DataArray(spectrum, dims=("temp_sample","theta_par","eV"), coords={"temp_sample": temperature, "theta_par": theta, "eV": KE_values}) #corresponding DataArray
                data.coords['temp_sample'].attrs = {'units' : 'K'}
                data.coords['theta_par'].attrs = {'units' : 'deg'}
                scan_type = "temp dep"
            
            else: #should be a simple dispersion
                #check data format looks right for a single dispersion
                if len(spectrum.shape) == 3 and spectrum.shape[0] == 1:
                    #data array
                    data = xr.DataArray(spectrum[0], dims=("theta_par","eV"), coords={"theta_par": theta, "eV": KE_values})
                    data.coords['theta_par'].attrs = {'units' : 'deg'}
                    scan_type = "dispersion"
                
                else:
                    raise Exception("Scan type does not seem to be supported.")
    
    #get and attach metadata
    meta_list = get_i05HR_metadata(file, scan_type)
    for i in meta_list:
        data.attrs[i] = meta_list[i]
    data.name = meta_list['scan_name']
    return data

def get_i05HR_metadata(file,scan_type):
    '''This function will extract the relevant metadata from the data tree of a Nexus file otained at the Diamond i05 HR branch.
    
    Input:
        file - Path to the file being loaded (string)
        scan_type - The type of scan, e.g. FS map (string)
        
    Retuns:
        meta_list - List of relevant metadata (dictionary)
    '''
    
    #load the file tree of the data
    a=nf.nxload(file)

    #assign metadata
    meta_list = {}
    meta_list['scan_name'] = 'i05-'+str(a.entry1.entry_identifier)
    meta_list['scan_type'] = scan_type
    meta_list['sample_description'] = None
    meta_list['eV_type'] = 'Kinetic'
    meta_list['beamline'] = 'Diamond I05-HR'
    meta_list['analysis_history'] = []
    meta_list['EF_correction'] = None
    meta_list['PE'] = float(a.entry1.instrument.analyser.pass_energy)
    
    #photon energy
    N_hv = len(a.entry1.instrument.monochromator.energy)  #number of recorded photon energy values
    if N_hv == 1:
        meta_list['hv'] = float(np.round(a.entry1.instrument.monochromator.energy,1)[0])
    else:
        hv_first = np.round(a.entry1.instrument.monochromator.energy[0],1)
        hv_last = np.round(a.entry1.instrument.monochromator.energy[N_hv-1],1)
        hv_step = (hv_last - hv_first)/(N_hv-1)
        meta_list['hv'] = str(hv_first)+'_'+str(hv_step)+'_'+str(hv_last)

    #polarisation
    N_pol = len(a.entry1.instrument.insertion_device.beam.final_polarisation_label)  #number of recorded polarisations
    if N_pol == 1:
        meta_list['pol'] = str(a.entry1.instrument.insertion_device.beam.final_polarisation_label)
    else:
        meta_list['pol'] = 'var'
    
    #number of sweeps
    try:
        meta_list['sweeps'] = int(a.entry1.instrument.analyser.number_of_iterations)
    except:
        try:
            meta_list['sweeps'] = int(a.entry1.instrument.analyser.number_of_cycles)
        except:
            meta_list['sweeps'] = 1

    meta_list['dwell'] = float(np.round(a.entry1.instrument.analyser.time_for_frames,2)[0])
    
    #analyser mode
    if 'Angular30' in a.entry1.instrument.analyser.lens_mode:
        meta_list['ana_mode'] = 'Ang30'
    elif 'Angular14' in a.entry1.instrument.analyser.lens_mode:
        meta_list['ana_mode'] = 'Ang14'
    elif 'Transmission' in a.entry1.instrument.analyser.lens_mode:
        meta_list['ana_mode'] = 'Trans'
    else:
        meta_list['ana_mode'] = str(a.entry1.instrument.analyser.lens_mode)

    #analyser entrance slit
    slit_no = a.entry1.instrument.analyser.entrance_slit_setting
    slit_size = a.entry1.instrument.analyser.entrance_slit_size
    if 'straight' in a.entry1.instrument.analyser.entrance_slit_shape:
        slit_shape = 's'
    elif 'curved' in a.entry1.instrument.analyser.entrance_slit_shape:
        slit_shape = 'c'
    else:
        slit_shape = str(a.entry1.instrument.analyser.entrance_slit_shape)
    meta_list['ana_slit'] = str(slit_size)+slit_shape+' (#'+str(slit_no)+')'
    meta_list['ana_slit_angle'] = 90
    
    #exit slits
    N_slits = len(a.entry1.instrument.monochromator.exit_slit_size)  #number of recorded exit slit values
    if N_slits == 1:
        meta_list['exit_slit'] = str(np.round(a.entry1.instrument.monochromator.exit_slit_size,3)[0]*1000)
    else:
        meta_list['exit_slit'] = 'var'
    
    #x position
    try:
        Dim_sax = len(np.shape(a.entry1.instrument.manipulator.sax)) #dimensions of scan
        if Dim_sax == 1:  #either single value or single array
            N_x = len(a.entry1.instrument.manipulator.sax)  #number of x values
            if N_x == 1:  #if a single value 
                x = float(np.round(a.entry1.instrument.manipulator.sax,3)[0])
            else:  #if varying
                x_start = np.round(a.entry1.instrument.manipulator.sax[0],3)
                x_end = np.round(a.entry1.instrument.manipulator.sax[N_x-1],3)
                x_step = np.round((x_end - x_start)/(N_x-1),2)
                x = str(x_start)+'_'+str(x_step)+'_'+str(x_end)
        elif Dim_sax == 2:  #2D array
            if a.entry1.instrument.manipulator.sax[0,0] == a.entry1.instrument.manipulator.sax[1,0]:  #then scan direction is along dim 1
                N_x = np.shape(a.entry1.instrument.manipulator.sax)[1]
                x_start = np.round(a.entry1.instrument.manipulator.sax[0,0],3)
                x_end = np.round(a.entry1.instrument.manipulator.sax[0,N_x-1],3)
            else:  #scan direction along dim 0    
                N_x = np.shape(a.entry1.instrument.manipulator.sax)[0]
                x_start = np.round(a.entry1.instrument.manipulator.sax[0,0],3)
                x_end = np.round(a.entry1.instrument.manipulator.sax[N_x-1,0],3)
            x_step = np.round((x_end - x_start)/(N_x-1),2)
            x = str(x_start)+'_'+str(x_step)+'_'+str(x_end)
        else:
            x = 'var'
    except:
        x = None
    

    #y position
    try:
        Dim_say = len(np.shape(a.entry1.instrument.manipulator.say)) #dimensions of scan
        if Dim_say == 1:  #either single value or single array
            N_y = len(a.entry1.instrument.manipulator.say)  #number of y values
            if N_y == 1:  #if a single value 
                y = float(np.round(a.entry1.instrument.manipulator.say,3)[0])
            else:  #if varying
                y_start = np.round(a.entry1.instrument.manipulator.say[0],3)
                y_end = np.round(a.entry1.instrument.manipulator.say[N_y-1],3)
                y_step = np.round((y_end - y_start)/(N_y-1),2)
                y = str(y_start)+'_'+str(y_step)+'_'+str(y_end)
        elif Dim_say == 2:  #2D array
            if a.entry1.instrument.manipulator.say[0,0] == a.entry1.instrument.manipulator.say[1,0]:  #then scan direction is along dim 1
                N_y = np.shape(a.entry1.instrument.manipulator.say)[1]
                y_start = np.round(a.entry1.instrument.manipulator.say[0,0],3)
                y_end = np.round(a.entry1.instrument.manipulator.say[0,N_y-1],3)
            else:  #scan direction along dim 0    
                N_y = np.shape(a.entry1.instrument.manipulator.say)[0]
                y_start = np.round(a.entry1.instrument.manipulator.say[0,0],3)
                y_end = np.round(a.entry1.instrument.manipulator.say[N_y-1,0],3)
            y_step = np.round((y_end - y_start)/(N_y-1),2)
            y = str(y_start)+'_'+str(y_step)+'_'+str(y_end)
        else:
            y = 'var'
    except:
        y = None

    #z position
    try:
        #z-axis
        Dim_saz = len(np.shape(a.entry1.instrument.manipulator.saz)) #dimensions of scan
        if Dim_saz == 1:  #either single value or single array
            N_z = len(a.entry1.instrument.manipulator.saz)  #number of z values
            if N_z == 1:  #if a single value 
                z = float(np.round(a.entry1.instrument.manipulator.saz,3)[0])
            else:  #if varying
                z_start = np.round(a.entry1.instrument.manipulator.saz[0],3)
                z_end = np.round(a.entry1.instrument.manipulator.saz[N_z-1],3)
                z_step = np.round((z_end - z_start)/(N_z-1),2)
                z = str(z_start)+'_'+str(z_step)+'_'+str(z_end)
        elif Dim_saz == 2:  #2D array
            if a.entry1.instrument.manipulator.saz[0,0] == a.entry1.instrument.manipulator.saz[1,0]:  #then scan direction is along dim 1
                N_z = np.shape(a.entry1.instrument.manipulator.saz)[1]
                z_start = np.round(a.entry1.instrument.manipulator.saz[0,0],3)
                z_end = np.round(a.entry1.instrument.manipulator.saz[0,N_z-1],3)
            else:  #scan direction along dim 0    
                N_z = np.shape(a.entry1.instrument.manipulator.saz)[0]
                z_start = np.round(a.entry1.instrument.manipulator.saz[0,0],3)
                z_end = np.round(a.entry1.instrument.manipulator.saz[N_z-1,0],3)
            z_step = np.round((z_end - z_start)/(N_z-1),2)
            z = str(z_start)+'_'+str(z_step)+'_'+str(z_end)
        else:
            z = 'var'  
    except:
        z = None
    
    #set to pyPhoto conventions
    meta_list['x1'] = x
    meta_list['x2'] = z
    meta_list['x3'] = y

    #polar
    N_polar = len(a.entry1.instrument.manipulator.sapolar)  #number of polar values
    if N_polar == 1:  #if a single value 
        meta_list['polar'] = float(np.round(a.entry1.instrument.manipulator.sapolar,1)[0])
    else:  #if a scan
        polar_first = np.round(a.entry1.instrument.manipulator.sapolar[0],1)
        polar_last = np.round(a.entry1.instrument.manipulator.sapolar[N_polar-1],1)
        polar_step = (polar_last - polar_first)/(N_polar-1)
        meta_list['polar'] = str(polar_first)+'_'+str(polar_step)+'_'+str(polar_last)
    
    #tilt
    try:
        meta_list['tilt'] = float(np.round(a.entry1.instrument.manipulator.satilt,1)[0])
    except:
        meta_list['tilt'] = str(np.round(a.entry1.instrument.manipulator.satilt,1)[0])
    
    #azi
    try:
        meta_list['azi'] = float(np.round(a.entry1.instrument.manipulator.saazimuth,1)[0])
    except:
        meta_list['azi'] = str(np.round(a.entry1.instrument.manipulator.saazimuth,1)[0])
    
    meta_list['norm_polar'] = None
    meta_list['norm_tilt'] = None
    meta_list['norm_azi'] = None

    #temperatures
    N_Temp = len(a.entry1.sample.temperature) #number of recorded temperature values
    if N_Temp == 1:  #if a single value 
        meta_list['temp_sample'] = float(np.round(a.entry1.sample.temperature,1)[0])
        meta_list['temp_cryo'] = float(np.round(a.entry1.sample.cryostat_temperature,1)[0])
    else:  #if varying
        T_sample_first = np.round(a.entry1.sample.temperature[0],1)
        T_sample_last = np.round(a.entry1.sample.temperature[N_Temp-1],1)
        T_cryo_first = np.round(a.entry1.sample.cryostat_temperature[0],1)
        T_cryo_last = np.round(a.entry1.sample.cryostat_temperature[N_Temp-1],1)
        meta_list['temp_sample'] = str(T_sample_first)+' : '+str(T_sample_last)
        meta_list['temp_cryo'] = str(T_cryo_first)+' : '+str(T_cryo_last)
    
    return meta_list