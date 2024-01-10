import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

AVEFILTER_MAPPING = {
    "sin_m1": "s-n", # south-north
    "cos_m1": "e-w", # east-west
    "cos_m0": "o-i" # out-in
}

def flatten_array_and_get_first_value(array:np.ndarray):
    """Used for cases such as: array([[143.]], dtype=float) --> will return 143.

    Args:
        array (np.ndarray): A numpy array

    Returns:
        Any: 0th element of the flattened numpy array
    """    
    
    assert type(array) == np.ndarray, f"{array} is not of type numpy.ndarray."
    
    flattened_array = array.flatten()
    value = flattened_array[0]
    
    return value

def extract_inner_array_from_dtype_object_array(array:np.ndarray) -> np.ndarray:
    """If there is a numpy array inside a numpy array, the inner one is returned.
    Example: array([array([[1]], dtype=int)], dtype=object) --> array([[1]], dtype=int)

    Args:
        array (np.ndarray): A numpy array.

    Returns:
        np.ndarray: An inner numpy array (if the initial array is nested with dtype==object) or the initial array.
    """    
    
    assert type(array) == np.ndarray, f"Object {array} is not of the type numpy.ndarray."
    
    if array.dtype == object:
        array = flatten_array_and_get_first_value(array)
       
    return array
    
def convert_numpy_str_array_to_str(array:np.ndarray) -> str:
    """Converts numpy array of character decimal codes (ASCII) to string.

    Args:
        array (np.ndarray): numpy array containing character codes

    Returns:
        str: converted string
    """    
    string = ""
    for code in array:
        char = chr(int(code))
        string += char

    return string

def convert_data_from_h5py_dataset_to_numpy_array_if_needed(data) -> np.ndarray:
    
    if type(data) != np.ndarray:
        numpy_data = np.zeros(data.shape, dtype=data.dtype)
        data.read_direct(numpy_data)
    else:
        numpy_data = data
        
    return numpy_data

def get_traveltime_data_from_mat_file(mat_file) -> Tuple[np.ndarray]:

    tt_plus = mat_file["traveltimes_plus"]
    tt_minus = mat_file["traveltimes_minus"]
    
    tt_plus = convert_data_from_h5py_dataset_to_numpy_array_if_needed(tt_plus)
    tt_minus = convert_data_from_h5py_dataset_to_numpy_array_if_needed(tt_minus)
    
    return tt_plus, tt_minus

def create_param_dict_from_mat_file(mat_file):
    
    assert "param" in mat_file, "The 'param' key not present in parsed .mat file."
    
    param = mat_file["param"]
    PARAM_KEYS = ['dx', 'dy', 'nx', 'ny', 'avefilter', 'komega_filter', 'distance']

    param_dict = {}
    for key in PARAM_KEYS:
        value = param[key]
        value = extract_inner_array_from_dtype_object_array(value)
        value = convert_data_from_h5py_dataset_to_numpy_array_if_needed(value)
        value = flatten_array_and_get_first_value(value)
        
        param_dict[key] = value
        
    print(f'Created param dict:', param_dict, sep='\n')
            
    return param_dict

def create_traveltime_plot(tt_plus:np.ndarray, tt_minus:np.ndarray, param_dict:dict, save_to:str):
    
    x_axis_pixel_count = float(param_dict['nx'])
    x_axis_megameters_per_pixel = param_dict['dx']
    
    y_axis_pixel_count = float(param_dict['ny'])
    y_axis_megameters_per_pixel = param_dict['dy']
    
    k_omega_filter = param_dict["komega_filter"]
    avefilter = param_dict["avefilter"]
    avefilter = AVEFILTER_MAPPING[avefilter]
    
    distance = param_dict["distance"]
    
    #* x axis will go from "minus this value" to "plus this value" (that's why the half is there)
    x_axis_extent = x_axis_pixel_count * x_axis_megameters_per_pixel / 2 
    # x_axis_bounds = [-x_axis_extent/2, x_axis_extent/2]
    
    #* y axis will go from "minus this value" to "plus this value" (that's why the half is there)
    y_axis_extent = y_axis_pixel_count * y_axis_megameters_per_pixel / 2
    # y_axis_bounds = [-y_axis_extent/2, y_axis_extent/2]

    xticks = (-np.flip(np.arange(0, x_axis_extent, 100))).tolist() + np.arange(0, x_axis_extent, 100).tolist()
    yticks = (-np.flip(np.arange(0, y_axis_extent, 100))).tolist() + np.arange(0, y_axis_extent, 100).tolist()

    fig = plt.figure()

    combined_axis_extent = [-x_axis_extent, x_axis_extent] + [-y_axis_extent, y_axis_extent]

    image = plt.imshow(tt_plus - tt_minus, cmap='jet', extent=combined_axis_extent, aspect='auto')
    plt.title(f"{k_omega_filter}-mode, {distance} Mm, {avefilter}")
    plt.xticks(xticks)
    plt.xlabel(r'$x$ (Mm)')
    plt.ylabel(r'$y$ (Mm)')
    plt.yticks(yticks)
    colorbar = plt.colorbar(image)
    colorbar.set_label(r"$\delta \tau$ (s)")
    plt.grid(False)
    plt.show()
    # plt.savefig(save_to, dpi=300)
    
def calculate_mean_traveltime_value_around_center(tt_plus:np.ndarray, tt_minus:np.ndarray):
    
    tt_data = tt_plus - tt_minus
    
    # NOTE: 256x256 px area around center (if a whole picture is 512x512) --> DEPRECATED for 100x100 px around center
    # lower_boundary = int(tt_data.shape[0]/2 - tt_data.shape[0]/4)
    # upper_boundary = int(tt_data.shape[0]/2 + tt_data.shape[0]/4)
    
    lower_boundary = int(tt_data.shape[0]/2 - 50)
    upper_boundary = int(tt_data.shape[0]/2 + 50)
    
    tt_around_center = tt_data[lower_boundary:upper_boundary, lower_boundary:upper_boundary]
    mean_around_center = tt_around_center.mean()
    
    print("Mean around center: ", mean_around_center)
    
    return mean_around_center
