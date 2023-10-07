import os
import json
import drms

from typing import Literal

JSOC_EMAIL: str = "daniel123chmurny@gmail.com"
METHOD: Literal["url", "url-quick"] = "url"
PROTOCOL: Literal["fits", "as-is"] = "fits"

EXPECTED_FILE_COUNT: int = 1921

if __name__ == "__main__":
    queries_to_check_filename = "./queries_to_check.txt"
    if not os.path.exists(queries_to_check_filename):
        raise FileNotFoundError(f'"{queries_to_check_filename}" does not exist, create it.')
    
    with open("./requests_to_check.txt", "r") as file:
        jsoc_queries = file.readlines()
        
    if not jsoc_queries:
        raise ValueError(f'No JSOC requests found in "{queries_to_check_filename}".')

    complete_data_queries: list[str] = []
    incomplete_data_queries: dict[str, dict] = {}
    
    client = drms.Client(email=JSOC_EMAIL, verbose=True)
    
    for query in jsoc_queries:
        request = client.export(query, method=METHOD, protocol=PROTOCOL)
        request.wait(timeout=900, verbose=True)
        
        data_urls = request.urls
        number_of_files = len(data_urls)
        
        if number_of_files == EXPECTED_FILE_COUNT:
            complete_data_queries.append(query)
        else:
            files_missing = EXPECTED_FILE_COUNT - number_of_files
            incomplete_data_queries[query] = {
                "files_missing": files_missing
            }
            
    with open("./queries_with_complete_data.txt", "w") as file:
        file.write("\n".join(complete_data_queries))
     
    with open("./incomplete_data_queries.json", "w") as file:
        json.dump(incomplete_data_queries, file)    
        
