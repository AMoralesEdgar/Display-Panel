# Convert txt to xarray
# Edgar Abarca Morales

# Load file import requirements
import numpy as np
import xarray as xr

def txt2xarray(filename, x_file, y_file, z_file, xdim, ydim, zdim, xuts, yuts, zuts):

    x = np.genfromtxt(x_file,delimiter=',')
    y = np.genfromtxt(y_file,delimiter=',')
    z = np.genfromtxt(z_file,delimiter=',')

    A = xr.DataArray(np.transpose(z), dims=(xdim,ydim), coords={xdim:x,ydim:y})
    A.coords[xdim].attrs = {'units' : xuts}
    A.coords[ydim].attrs = {'units' : yuts}
    A.attrs['scan_name'] = filename
    A.attrs['zdim'] = zdim
    A.attrs['zuts'] = zuts

    return A