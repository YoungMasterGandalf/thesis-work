import os
import datetime

def create_a_one_day_dopplergram_query_from_date(date: datetime.datetime) -> str:
    year = date.year
    month = date.month
    day = date.day
    
    jsoc_query = f'hmi.v_45s[{year}.{month}.{day}_00:00:00_TAI-{year}.{month}.{day + 1}_00:00:00_TAI]{{Dopplergram}}'
    
    return jsoc_query

if __name__ == "__main__":
    dates_to_queries_filename = "./dates_to_queries.txt"
    
    if not os.path.exists(dates_to_queries_filename):
        raise FileNotFoundError(f'"{dates_to_queries_filename}" does not exist, create it.')
    
    with open(dates_to_queries_filename, "r") as file:
        dates = file.readlines()
        
    queries: list[str] = []
        
    for date_string in dates:
        date = datetime.datetime.strptime(date_string, "%Y%m%d")
        jsoc_query = create_a_one_day_dopplergram_query_from_date(date=date)
        queries.append(jsoc_query)
        
    with open("./queries_to_check.txt", "w") as file:
        file.write("\n".join(queries))
        