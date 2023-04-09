import scipy.io
import h5py

def read_mat_file(file_path:str):
    try:
        mat = scipy.io.loadmat(file_path)
        print("Running scipy mat ...")
    except NotImplementedError:
        mat = h5py.File(file_path, 'r')
        print("Running h5py ... ")
        
    return mat

