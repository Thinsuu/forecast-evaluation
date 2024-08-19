import json
import pandas as pd
import math
import shutil
from sqlalchemy.exc import PendingRollbackError
from sqlalchemy.orm import aliased
from sqlalchemy import and_
from db_definitions import session, HistoricalData, ForecastData
from datetime import datetime, timedelta
from sqlalchemy import func
from pathlib import Path


OUTPUT_DIR = Path('publish')
CITY_ID = 2711537


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

    data = {}
    for result in db_results:
        date = result.local_date
        if date not in data:
            data[date] = {'Actual_temp': result.actual_temp}
            for diff_time in diff_of_interest:
                data[date][diff_time] = None
        data[date][result.time_difference] = (data[date]["Actual_temp"] / result.forecast_temp) * 100.0 - 100.0
    
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
        if result.forecast_wind_speed != 0:
            wind_speed_data[date][result.time_difference] = (wind_speed_data[date]["Actual_wind"] / result.forecast_wind_speed) * 100.0 - 100.0
        else:
            wind_speed_data[date][result.time_difference] = 0

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
    #     temp_data[day] = 123
    # for day, data_dict in wind_data.items():
    #     if day not in merged_dict:
    #         merged_dict[day] = {}
    #     merged_dict[day].update(data_dict)

    with open(OUTPUT_DIR / 'result.json', 'w') as f:
        json.dump(temp_data, f, indent=2)


if __name__ == '__main__':
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    combine_data()
    shutil.copy(Path(__file__).parent / 'anychart_template.html', OUTPUT_DIR / 'index.html')
