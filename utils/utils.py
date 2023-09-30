import os

from typing import Union

def save_list_to_text_file(list_var: list, dir_path: str, filename: str):
	
	# Create the file directory if non-existent
	if not os.path.isdir(dir_path):
		os.makedirs(dir_path)

	with open(os.path.join(dir_path, filename), "w") as file:
		for element in list_var:
			file.write(f'{element}\n')
   
def get_plus_minus_value_string_from_value(value: Union[int, float], round_value:bool=True) -> str:
    """Converts a numerical value to string representation with it's sign represented as a word.

    Args:
        value (Union[int, float]): A numerical value to be parsed to string.
        round_value (bool, optional): If true a value is round to an integer. Defaults to True.

    Returns:
        str: A string representation of the initial value.
        
    Example 1:
        value = -13.8
        round_value = True
        
        returns: "minus_14"
        
    Example 2:
        value = 4.7
        round_value = False
        
        returns: "plus_4.7"
    """    
    if round_value:
        value = round(value)
        
    sign_string = "plus" if value >= 0 else "minus"
    
    value_string = f'{sign_string}_{str(abs(value))}'
    
    return value_string

def create_request_name_from_request_string(request:str) -> str:
    tai_index = request.index("_TAI")
    req_name = request[:tai_index]
    req_name = req_name.replace("[", "_")
    req_name = req_name.replace(":", ".")
    
    return req_name

def create_datacube_directory_name(request:str, origin:list[float], velocity:float):
    req_name = create_request_name_from_request_string(request)
    lon_string = f'lon_{get_plus_minus_value_string_from_value(origin[0])}'
    lat_string = f'lat_{get_plus_minus_value_string_from_value(origin[1])}'
    velocity_string = f'vel_{get_plus_minus_value_string_from_value(velocity)}'
    
    datacube_dir_name = f'{req_name}_{lon_string}_{lat_string}_{velocity_string}'
    
    return datacube_dir_name