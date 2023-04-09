import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

#* PATH example
# FILE_PATH = "/Users/daniel/Documents/diploma_thesis_sidework/komega_cube.mat_controlplots.mat"

def create_powerspectrum_fig_from_mat_file(mat_file, save_to:str):
    k_omega = mat_file["k_omega"]
    
    #* x axis: k (Mm^-1)
    x_axis_extent = [0, np.pi] #? Is this extent right? Shouldn't it be dependent on the data/keys?
    
    #* y axis: nu (mHz)
    y_axis_extent_omega = [mat_file["omega"].min(), mat_file["omega"].max()]
    y_axis_extent = [element/(2*np.pi)*10**3 for element in y_axis_extent_omega] #* omega (Hz) --> nu (mHz) conversion
    
    fig = plt.figure()
    plt.imshow(k_omega, cmap='jet', norm=colors.LogNorm(), extent=x_axis_extent + y_axis_extent, aspect='auto')
    plt.xlabel(r'$k$ (Mm$^{-1}$)')
    plt.ylabel(r'$\nu$ (mHz)')
    plt.grid(False)
    plt.savefig(save_to, dpi=300)

            