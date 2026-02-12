# Convert image to xarray
# Edgar Abarca Morales

# Load file import requirements
from PIL import Image
import numpy as np
import xarray as xr

# Create a Display Panel input dictionary from image
def image2xarray(filename, xdim, ydim, zdim, xuts, yuts, zuts):

    # Process image
    I = Image.open(filename).convert('L')
    I = I.rotate(-0.5)

    # Extract data
    z=255-np.flip(np.array(I).astype(int),axis=0)
    y=np.arange(0,np.shape(z)[0])
    x=np.arange(0,np.shape(z)[1])

    A = xr.DataArray(np.transpose(z), dims=(xdim,ydim), coords={xdim:x,ydim:y})
    A.coords[xdim].attrs = {'units' : xuts}
    A.coords[ydim].attrs = {'units' : yuts}
    A.attrs['scan_name'] = filename
    A.attrs['zdim'] = zdim
    A.attrs['zuts'] = zuts

    return A