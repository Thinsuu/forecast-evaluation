import json
import pandas as pd
import math
from sqlalchemy.exc import PendingRollbackError
from sqlalchemy.orm import aliased
from sqlalchemy import and_
from db_definitions import session, HistoricalData, ForecastData
from datetime import datetime, timedelta
from sqlalchemy import func
from pathlib import Path


OUTPUT_DIR = Path('publish')
CITY_ID = 2711537

# {city_id: deviation}
average_deviation = {}


def prepare_json_temp():
    diff_of_interest = list(range(2, 100))

    max_historical_date = session.query(func.max(HistoricalData.local_date)).scalar()
    end_date = max_historical_date
    start_date = (end_date - timedelta(days=10)).replace(hour=0)

    db_results = session.query(
        HistoricalData.local_date,
        HistoricalData.temperature.label('actual_temp'),
        ForecastData.temperature.label('forecast_temp'),
        ForecastData.time_difference
    ).join(
        ForecastData,
        and_(
            ForecastData.local_date == HistoricalData.local_date,
            ForecastData.city_id == HistoricalData.city_id,
        )
    ).filter(
        HistoricalData.local_date >= start_date,
        ForecastData.time_difference <= max(diff_of_interest),
        HistoricalData.city_id == CITY_ID,
    ).all()

    df = pd.DataFrame(db_results, columns=['local_date', 'actual_temp', 'forecast_temp', 'time_difference'])
    df['local_date'] = pd.to_datetime(df['local_date'])
    last_24_hours = end_date - timedelta(hours=24)
    df_24h = df[df['local_date'] >= last_24_hours]
    df_12h = df_24h[df_24h['time_difference'] == 12]

    if df_12h.empty:
        print("No data available for the last 24 hours.")
        return {}

    print(df_12h)

    df_12h.loc[:, "prediction_error"]  = abs(df_12h['forecast_temp'] - df_12h['actual_temp'])
    temp_differ_12hr_avg = df_12h['prediction_error'].mean()

    print(temp_differ_12hr_avg)
    average_deviation[CITY_ID] = temp_differ_12hr_avg
        
    data = {}
    for result in db_results:
        date = result.local_date
        if date not in data:
            data[date] = {'Actual_temp': result.actual_temp}
            for diff_time in diff_of_interest:
                data[date][diff_time] = None

        data[date][result.time_difference] =  result.forecast_temp - data[date]["Actual_temp"]
    
    df = pd.DataFrame.from_dict(data, orient='index')
    df = df.rename_axis('actual_date').reset_index()
    df = df.groupby(df['actual_date'].dt.date).mean()
    df = df.drop('actual_date', axis=1).sort_index(ascending=False)
    
    temp_output_data = {
            date.strftime('%Y-%m-%d'): {
                'Temp_Actual': f'{values_dict["Actual_temp"]:.1f}',
                'Temp_Trend': list(
                    (None if math.isnan(v) else round(v, 2))
                    for k, v in values_dict.items() if k != 'Actual_temp'
                ),
            }
            for date, values_dict in df.to_dict('index').items()
        }
    return temp_output_data


def prepare_json_wind():
    diff_of_interest = list(range(2, 100))

    max_historical_date = session.query(func.max(HistoricalData.local_date)).scalar()
    end_date = max_historical_date
    start_date = (end_date - timedelta(days=10)).replace(hour=0)

    db_results = session.query(
        HistoricalData.local_date,
        HistoricalData.wind_speed.label('actual_wind_speed'),
        ForecastData.wind_speed.label('forecast_wind_speed'),
        ForecastData.time_difference
    ).join(
        ForecastData,
        and_(
            ForecastData.local_date == HistoricalData.local_date,
            ForecastData.city_id == HistoricalData.city_id,
        )
    ).filter(
        HistoricalData.local_date >= start_date,
        ForecastData.time_difference <= max(diff_of_interest),
        HistoricalData.city_id == CITY_ID,
    ).all()

    wind_speed_data = {}
    for result in db_results:
        date = result.local_date
        if date not in wind_speed_data:
            wind_speed_data[date] = {'Actual_wind': result.actual_wind_speed}
            for diff_time in diff_of_interest:
                wind_speed_data[date][diff_time] = None
        wind_speed_data[date][result.time_difference] = result.forecast_wind_speed - wind_speed_data[date]["Actual_wind"]
    
    # df = pd.DataFrame.from_dict(wind_speed_data, orient='index')
    # df.index = pd.to_datetime(df.index)
    # df_grouped = df.groupby(df.index.date).mean()

    df = pd.DataFrame.from_dict(wind_speed_data, orient='index')
    df = df.rename_axis('actual_date').reset_index()
    df = df.groupby(df['actual_date'].dt.date).mean()
    df = df.drop('actual_date', axis=1).sort_index(ascending=False)
    

    wind_output_data = {
        date.strftime('%Y-%m-%d'): {
            'Wind_Actual': f'{values_dict["Actual_wind"]:.1f}',
            'Wind_Trend': list(
                (None if math.isnan(v) else round(v, 2))
                for k, v in values_dict.items() if k != 'Actual_wind'
            ),
        }
        for date, values_dict in df.to_dict('index').items()
        }
    return wind_output_data


def combine_data():
    temp_data = prepare_json_temp()
    wind_data = prepare_json_wind()
    for day, data_dict in wind_data.items():
        temp_data[day].update(data_dict)

    json_filename = f'SMHI_{CITY_ID}.json'
    with open(OUTPUT_DIR / json_filename, 'w') as f:
        json.dump(temp_data, f, indent=2)

    with open(Path(__file__).parent / 'anychart_template.html', 'r') as f:
        filedata = f.read()
    
    filedata = filedata.replace('REPLACEME_JSON_FILE_PATH', json_filename)
    filedata = filedata.replace('City_id_ToREPLACE', f'{from_cityId_to_name(CITY_ID)}')

    html_filename = f'SMHI_{CITY_ID}.html'
    with open(OUTPUT_DIR / html_filename, 'w') as f:
        filedata = f.write(filedata)

def process_all_city_id():
    city_ids_query = session.query(HistoricalData.city_id).distinct().all()
    print(f"City IDs query result: {city_ids_query}")

    if not city_ids_query:
        print("No city IDs found in the database.")
        return

    for row in city_ids_query:
        city_id = row[0]
        print(f"Processing city ID: {city_id}")

        global CITY_ID
        CITY_ID = city_id

        if CITY_ID is None:
            print(f"Error: City_ID is NONE for row {row}")
            continue

        combine_data()
    print("Finished processing all city IDs.")

    cityID_links = ""
    for row in city_ids_query:
        city_id = row[0]

        weather_standard_setting = ""
        if average_deviation[city_id] <= 10:
            weather_standard_setting = "Good"
        elif average_deviation[city_id] <= 20:
            weather_standard_setting = "So-so"
        else:
            weather_standard_setting = "Bad"

        cityID_links += f'<li><a href = "SMHI_{city_id}.html"> {from_cityId_to_name(city_id)} Weather</a> - {weather_standard_setting} precision</li>\n'
    
    with open(Path(__file__).parent / 'index_template.html', 'r') as f:
        html_body = f.read()
    html_body = html_body.replace('REPLACE_CITYID', cityID_links)

    with open(OUTPUT_DIR / 'index.html', 'w') as f:
        f.write(html_body)


def from_cityId_to_name(city_id):
    with open(Path(__file__).parent / 'city_names.json', 'r') as f:
        json_contents = json.load(f)
    
    city_id_str = str(city_id)

    if city_id_str in json_contents:
        city_name_only= json_contents[city_id_str]
    else:
        print(f"City ID {city_id} not found in city_names.json.")
        city_name_only = "Unknown city"
    return city_name_only


if __name__ == '__main__':
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    process_all_city_id()
