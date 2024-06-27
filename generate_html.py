import pandas as pd
from sqlalchemy.exc import PendingRollbackError
from sqlalchemy.orm import aliased
from db_definitions import session, HistoricalData, ForecastData
from datetime import datetime, timedelta

def main():
    """
    Get data from DB and produce HTML with a table.
    """
    diff_of_interest = [1, 3, 12, 24, 72]

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
               
    df = pd.DataFrame.from_dict(data, orient='index').sort_index()
    
    for diff in diff_of_interest:
        col = f'Diff -{diff}h'
        if col not in df.columns:
            df[col] = '--'
    df = df.fillna('--')


    html_table = df.to_html(classes='table table-striped', border=0)

    with open('./template.html', 'r') as f:
        template_html = f.read()
    complete_html = template_html.format(table=html_table)

    with open('table.html', 'w') as f:
        f.write(complete_html)

    # print(complete_html)

if __name__ == '__main__':
    main()

