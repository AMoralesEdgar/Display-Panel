# Load file import requirements
from data_converters.txt2xarray import txt2xarray
from Run_DP import Run_DP

# Load Nd3Ni2O7 resPES datasets
a = txt2xarray('Map_Nd3Ni2O7_or','Example1/x.txt','Example1/y.txt','Example1/z_or.txt','BE','hv','Intensity','eV','eV','counts')
b = txt2xarray('Map_Nd3Ni2O7_nR','Example1/x.txt','Example1/y.txt','Example1/z_nR.txt','BE','hv','Intensity','eV','eV','counts')
c = txt2xarray('Map_Nd3Ni2O7_df','Example1/x.txt','Example1/y.txt','Example1/z_df.txt','BE','hv','Intensity','eV','eV','counts')

Run_DP([a,b,c])