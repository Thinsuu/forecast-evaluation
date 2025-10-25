import requests
from pathlib import Path
from datetime import datetime
import argparse

def fetch_and_save(url, file_path):
    response = requests.get(url)
    if response.status_code == 200:
        print(f'Save {file_path}')
        with open(file_path, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed to fetch data from {url}, status code: {response.status_code}")


def main(city_id):
    base_url = "https://wpt-a.smhi.se/backend-weatherpage"
    forecast_url = f"{base_url}/forecast/v2025.4/{city_id}"
    historical_url = f"{base_url}/analys/{city_id}"
    raw_data_dir = Path('raw_data')

    raw_data_dir.mkdir(parents=True, exist_ok=True)

    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    forecast_file = raw_data_dir / f"forecast_{city_id}_{current_time}.json"
    historical_file = raw_data_dir / f"historical_{city_id}_{current_time}.json"

    fetch_and_save(forecast_url, forecast_file)
    fetch_and_save(historical_url, historical_file)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch weather data for a given city ID from SMHI.')
    parser.add_argument('city_id', type=int, help='City ID for fetching weather data from SMHI')

    args = parser.parse_args()
    main(args.city_id)


