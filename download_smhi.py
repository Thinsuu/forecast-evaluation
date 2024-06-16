import requests
from pathlib import Path
from datetime import datetime

forecast_url = "https://www.smhi.se/wpt-a/backend_tendayforecast_nextgen/forecast/fetcher/2711537/10dFormat"
historical_url = "https://www.smhi.se/wpt-a/backend_tendayforecast_nextgen/analys/fetcher/2711537/10dFormat"
raw_data_dir = Path('raw_data')

raw_data_dir.mkdir(parents=True, exist_ok=True)

def fetch_and_save(url, file_path):
    response = requests.get(url)
    if response.status_code == 200:
        print(f'Save {file_path}')
        with open(file_path, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed to fetch data from {url}, status code: {response.status_code}")

current_time = datetime.now().strftime("%Y%m%d%H%M%S")
forecast_file = raw_data_dir / f"forecast_{current_time}.json"
historical_file = raw_data_dir / f"historical_{current_time}.json"

fetch_and_save(forecast_url, forecast_file)
fetch_and_save(historical_url, historical_file)
