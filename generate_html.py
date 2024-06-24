import pandas as pd
from sqlalchemy.exc import PendingRollbackError
from sqlalchemy.orm import aliased
from db_definitions import session, HistoricalData, ForecastData

def main():
    diff_of_interest = [1, 3, 12, 24, 72]

    db_results = session.query(
        HistoricalData.local_date,
        HistoricalData.temperature.label('actual_temp'),
        ForecastData.temperature.label('forecast_temp'),
        ForecastData.time_difference
    ).join(
        ForecastData,
        ForecastData.local_date == HistoricalData.local_date
    ).filter(
        ForecastData.time_difference.in_(diff_of_interest)
    ).all()

    data = {}
    for result in db_results:
        date = result.local_date
        if date not in data:
            data[date] = {'Actual': result.actual_temp}
        data[date][f'Diff -{result.time_difference}h'] = f'{result.forecast_temp} ({result.forecast_temp - result.actual_temp:.1f})'

    df = pd.DataFrame.from_dict(data, orient='index').sort_index()
    
    for diff in diff_of_interest:
        col = f'Diff -{diff}h'
        if col not in df.columns:
            df[col] = '--'
    df = df.fillna('--')
    
    html_table = df.to_html(classes='table table-striped', border=0)

    with open('table.html', 'w') as f:
        f.write(html_table)

    print(html_table)

if __name__ == '__main__':
    main()

