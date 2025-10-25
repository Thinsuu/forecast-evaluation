import sys
import json
from datetime import date, datetime
from pathlib import Path
from typing import List, Tuple

import pytz

# def prepare_forecast(file_path):
#     with open(file_path, 'r') as file:
#         data = json.load(file)
    
#     day_series = data['daySerie']
#     reference_time = datetime.fromisoformat(data['referenceTime'][:-1])
#     for day in day_series:
#         for entry in day['data']:
#             local_date = datetime.fromisoformat(entry['localDate'][:-1])
#             time_difference = local_date - reference_time
#             time_dif_hours = int(time_difference.seconds/60/60)
#             print(f"{entry['localDate']}  {time_dif_hours}    {entry['t']}")

def list_files(starting_name):
    directory = 'raw_data'
    dir_path = Path(directory)

    forecast_files = [file for file in dir_path.glob('*') if starting_name in file.name]
    return forecast_files

def extract_data_forecast_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    city_id = data['place']['geonameid']
    if 'forecast10d' in data:
        data = data['forecast10d']
    day_series = data['days']
    reference_time = datetime.fromisoformat(data['referenceTime'][:-1])
    reference_time = reference_time.replace(tzinfo=pytz.utc)
    stockholm_tz = pytz.timezone('Europe/Stockholm')
    reference_time = reference_time.astimezone(stockholm_tz)
    website_name = 'SMHI'

    extracted_data = []

    for day in day_series:
        for entry in day['data']:
            local_date = datetime.fromisoformat(entry['localDate'][:-1])
            local_date = local_date.replace(tzinfo=stockholm_tz)
            time_difference = local_date - reference_time
            time_dif_hours = int(time_difference.seconds/60/60)
            time_dif_hours += time_difference.days * 24
            temperature = float(entry['t'])
            if type(entry['tp']) == float:
                precipitation = float(entry['tp'])
            else:
                precipitation = (entry['precMax'] + entry['precMin']) / 2
                precipitation = round(precipitation, 2)
            wind_speed = float(entry['ws'])
            extracted_data.append((city_id, website_name, local_date, time_dif_hours, temperature, precipitation, wind_speed))
    return extracted_data
            
def forecast_dataset_prep():
    forecast_files = list_files('forecast')
    dataset_forecast = set()

    for file in forecast_files:
        file_data = extract_data_forecast_file(file)
        dataset_forecast.update(file_data)
    return dataset_forecast

def extract_data_historical_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    day_series = data['days']
    extracted_data = []
    city_id = data['place']['geonameid']
    city_name = data['place']['place']
    website_name = 'SMHI'

    for day in day_series:
        for entry in day['data']:
            local_date = datetime.fromisoformat(entry['localDate'][:-1])
            temperature = float(entry['t'])
            precipitation = float(entry.get('prec1h', 0))
            wind_speed = float(entry['ws'])
            extracted_data.append((city_id, website_name, local_date, temperature, precipitation, wind_speed, city_name))
    return extracted_data

def historical_dataset_prep():
    historical_files = list_files('historical')
    dataset_historical = set()

    for file in historical_files:
        file_data = extract_data_historical_file(file)
        dataset_historical.update(file_data)
    return dataset_historical

# def prepare_rows(file_path):
#     if "historical" in file_path.name:
#         extract_data_historical_file(file_path)
#     elif "forecast" in file_path.name:
#         prepare_forecast(file_path)
#     else:
#         print("The file name should contain 'historical' or 'foreccast'. Exiting.")
#         return


def main():
    # if len(sys.argv) != 2:
    #     print("Usage: python3 prepare_rows.py <path_to_json_file>")
    #     return

    # json_path = Path(sys.argv[1])
    # if not json_path.exists():
    #     print(f'{json_path} does not exist!')
    #     return

    # prepare_rows(json_path)

    print('Historical:')
    for row in historical_dataset_prep():
        print(row)

    print('Forecast:')
    for row in sorted(forecast_dataset_prep()):
        print(row)



if __name__ == "__main__":
    main()
    