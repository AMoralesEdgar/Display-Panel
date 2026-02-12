# Load file import requirements
from data_converters.i05HR_to_xarray import load_i05HR_data
from Run_DP import Run_DP

# Load files
a = load_i05HR_data('Example0/i05-126294.nxs')
b = load_i05HR_data('Example0/i05-126295.nxs')
c = load_i05HR_data('Example0/i05-126305.nxs')
d = load_i05HR_data('Example0/i05-126306.nxs')

Run_DP([a,b,c,d])