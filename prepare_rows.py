import sys
import json
from pathlib import Path

def prepare_forecast(file_path):
    if "forecast" not in file_path.name:
        print("The file name does not contain 'forecast'. Exiting.")
        return

    with open(file_path, 'r') as file:
        data = json.load(file)
    
    day_series = data['daySerie']


def prepare_historical(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    day_series = data['daySerie']

    for day in day_series:
        for entry in day['data']:
            print(f"{entry['localDate']}    {entry['t']}")


def prepare_rows(file_path):
    if "historical" in file_path.name:
        prepare_historical(file_path)
    elif "forecast" in file_path.name:
        prepare_forecast(file_path)
    else:
        print("The file name should contain 'historical' or 'foreccast'. Exiting.")
        return


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 prepare_rows.py <path_to_json_file>")
        return

    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f'{json_path} does not exist!')
        return

    prepare_rows(json_path)


if __name__ == "__main__":
    main()
    