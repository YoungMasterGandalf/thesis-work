import os
import scipy.io
import h5py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import argparse

#* PATH example
# FILE_PATH = "/Users/daniel/Documents/diploma_thesis_sidework/komega_cube.mat_controlplots.mat"

def read_mat_file(file_path:str):
    try:
        mat = scipy.io.loadmat(file_path)
        print("Running scipy mat ...")
    except NotImplementedError:
        mat = h5py.File(file_path, 'r')
        print("Running h5py ... ")
        
    return mat

def plot_powerspectrum_from_mat_object(mat_object):
    
    k_omega = mat_object["k_omega"]
    
    #* x axis: k (Mm^-1)
    x_axis_extent = [0, np.pi] #? Is this extent right? Shouldn't it be dependent on the data/keys?
    
    #* y axis: nu (mHz)
    y_axis_extent_omega = [mat_object["omega"].min(), mat_object["omega"].max()]
    y_axis_extent = [element/(2*np.pi)*10**3 for element in y_axis_extent_omega] #* omega (Hz) --> nu (mHz) conversion
    
    fig = plt.figure()
    plt.imshow(k_omega, cmap='jet', norm=colors.LogNorm(), extent=x_axis_extent + y_axis_extent, aspect='auto')
    plt.xlabel(r'$k$ (Mm$^{-1}$)')
    plt.ylabel(r'$\nu$ (mHz)')
    plt.grid(False)
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    file_path_help = """Path leading to a .mat file containing k_omega data, 
    e.g.: "/Users/daniel/Documents/diploma_thesis_sidework/komega_cube.mat_controlplots.mat" """
    parser.add_argument('file_path', type=str, help=file_path_help)
    
    args = parser.parse_args()
    
    FILE_PATH = args.file_path
    assert os.path.exists(FILE_PATH), f'Entered PATH {FILE_PATH} does not exist.'
    assert os.path.isfile(FILE_PATH), f'Entered PATH {FILE_PATH} does not lead to a file.'
    
    mat = read_mat_file(FILE_PATH)
    plot_powerspectrum_from_mat_object(mat_object=mat)
    