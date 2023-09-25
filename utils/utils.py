import os

def save_list_to_text_file(list_var: list, dir_path: str, filename: str):
	
	# Create the file directory if non-existent
	if not os.path.isdir(dir_path):
		os.makedirs(dir_path)

	with open(os.path.join(dir_path, filename), "w") as file:
		for element in list_var:
			file.write(f'{element}\n')