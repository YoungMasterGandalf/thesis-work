import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

#* PATH example
# FILE_PATH = "/Users/daniel/Documents/diploma_thesis_sidework/komega_cube.mat_controlplots.mat"

def plot_ring_diagram(mat_file):
    kx = mat_file["kx"]
    ky = mat_file["ky"]
    
    #* x axis: k (Mm^-1)
    x_axis_extent = [0, np.pi] #? Is this extent right? Shouldn't it be dependent on the data/keys?
    
    #* y axis: nu (mHz)
    # y_axis_extent_omega = [mat_file["omega"].min(), mat_file["omega"].max()]
    # y_axis_extent = [element/(2*np.pi)*10**3 for element in y_axis_extent_omega] #* omega (Hz) --> nu (mHz) conversion
    
    for i in range(5):
        data = mat_file["kx_ky"][:, :, i]
        data = np.fft.fftshift(data)
        cut_omega = mat_file["freq"][i][0]
        cut_frequency = cut_omega/(2 * np.pi) * 1000 # mHz
        fig = plt.figure()
        # plt.imshow(k_omega, cmap='jet', norm=colors.LogNorm(), extent=x_axis_extent + y_axis_extent, aspect='auto')
        plt.imshow(data, cmap='jet', norm=colors.LogNorm(), 
                   extent=[kx.min(), kx.max()] + [ky.min(), ky.max()])
        plt.title(r'Ring diagram ($\nu$ = ' + str(cut_frequency) + ' mHz)')
        # plt.xlabel(r'$k$ (Mm$^{-1}$)')
        # plt.ylabel(r'$\nu$ (mHz)')
        plt.plot([kx.min(), kx.max()], [0, 0], "k--", lw=0.5)
        plt.plot([0, 0], [ky.min(), ky.max()], "k--", lw=0.5)
        plt.xlabel(r'$k_x$ (Mm$^{-1}$)')
        plt.ylabel(r'$k_y$ (Mm$^{-1}$)')
        plt.grid(False)
    # plt.savefig(save_to, dpi=300)
    plt.show()
    
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

            