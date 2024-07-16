import json
import pandas as pd
import math
import shutil
from sqlalchemy.exc import PendingRollbackError
from sqlalchemy.orm import aliased
from db_definitions import session, HistoricalData, ForecastData
from datetime import datetime, timedelta
from sqlalchemy import func
from pathlib import Path


OUTPUT_DIR = Path('publish')


def prepare_json():
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
        ForecastData.local_date == HistoricalData.local_date
    ).filter(
        HistoricalData.local_date >= start_date,
        ForecastData.time_difference <= max(diff_of_interest),
    ).all()

    data = {}
    for result in db_results:
        date = result.local_date
        if date not in data:
            data[date] = {'Actual': result.actual_temp}
            for diff_time in diff_of_interest:
                data[date][diff_time] = None
        data[date][result.time_difference] = (data[date]["Actual"] / result.forecast_temp) * 100.0 - 100.0

    df = pd.DataFrame.from_dict(data, orient='index')
    df = df.rename_axis('actual_date').reset_index()
    df = df.groupby(df['actual_date'].dt.date).mean()
    df = df.drop('actual_date', axis=1).sort_index(ascending=False)

    output_data = {
        date.strftime('%Y-%m-%d'): {
            'Actual': f'{values_dict["Actual"]:.1f}',
            'Trend': list(
                (None if math.isnan(v) else round(v, 2))
                for k, v in values_dict.items() if k != 'Actual'
            ),
        }
        for date, values_dict in df.to_dict('index').items()
    }

    with open(OUTPUT_DIR / 'result.json', 'w') as f:
        json.dump(output_data, f, indent=2)


def produce_html():
    """
    Get data from DB and produce HTML with a table.
    """
    diff_of_interest = [1, 3, 12, 24, 72]

    max_historical_date = session.query(func.max(HistoricalData.local_date)).scalar()
    end_date = max_historical_date
    start_date = end_date - timedelta(days=10)

    db_results = session.query(
        HistoricalData.local_date,
        HistoricalData.temperature.label('actual_temp'),
        ForecastData.local_date.label('forecast_date'),
        ForecastData.temperature.label('forecast_temp'),
        ForecastData.time_difference
    ).join(
        ForecastData,
        ForecastData.local_date == HistoricalData.local_date
    ).all()

    data = {}
    for result in db_results:
        if result.time_difference not in diff_of_interest:
            continue
        date = result.local_date
        if date not in data:
            data[date] = {'Actual': result.actual_temp}
        data[date][f'Diff -{result.time_difference}h'] = f'{result.forecast_temp} ({result.forecast_temp - result.actual_temp:.1f})'
    
    for date in data.keys():
        for diff in diff_of_interest:
            col = f'Diff -{diff}h'
            if col not in data[date]:
                closest_result = None
                closest_diff = None
                for result in db_results:
                    if result.local_date == date:
                        if closest_diff is None or abs(result.time_difference - diff) < closest_diff:
                            closest_diff = abs(result.time_difference - diff)
                            closest_result = result
        
                if closest_result:
                    data[date][col] = f'{closest_result.forecast_temp} ({closest_result.forecast_temp - data[date]["Actual"]:.1f})'
                else:
                    data[date][col] = '--'

    df = pd.DataFrame.from_dict(data, orient='index').sort_index(ascending=False)
    df = df[(df.index >= start_date) & (df.index <= end_date)]

    
    for diff in diff_of_interest:
        col = f'Diff -{diff}h'
        if col not in df.columns:
            df[col] = '--'
    df = df.fillna('--')


    html_table = df.to_html(classes='table table-striped', border=0)

    with open('./template.html', 'r') as f:
        template_html = f.read()
    complete_html = template_html.format(table=html_table)

    with open(OUTPUT_DIR / 'table.html', 'w') as f:
        f.write(complete_html)

    # print(complete_html)

if __name__ == '__main__':
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    prepare_json()
    shutil.copy(Path(__file__).parent / 'anychart_template.html', OUTPUT_DIR / 'index.html')
