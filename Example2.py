# Load file import requirements
from data_converters.image2xarray import image2xarray
from Run_DP import Run_DP

# Load Nd3Ni2O7 resPES datasets
a = image2xarray('Example2/DTC-C_RT_1.png','x','y','z','pix','pix','bytes')
b = image2xarray('Example2/DTC-C_4K_2.png','x','y','z','pix','pix','bytes')

Run_DP([a,b])