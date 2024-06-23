from db_definitions import ForecastData, session, HistoricalData
import prepare_rows


def put_historical_data():
    existing_dates = session.query(HistoricalData.local_date).all()
    existing_dates = [row[0] for row in existing_dates]

    from_json = prepare_rows.historical_dataset_prep()
    for local_date, temperature in from_json:
        if local_date in existing_dates:
            continue
        print(local_date, temperature)
        row = HistoricalData(
            local_date=local_date,
            temperature=temperature,
        )
        session.add(row)


def put_forecast_data():
    existing_dates = session.query(
        ForecastData.local_date, ForecastData.time_difference).all()

    from_json = prepare_rows.forecast_dataset_prep()
    for local_date, time_dif_hours, temperature in from_json:
        local_date = local_date.replace(tzinfo=None)
        if (local_date, time_dif_hours) in existing_dates:
            continue
        row = ForecastData(
            local_date=local_date,
            time_difference=time_dif_hours,
            temperature=temperature,
        )
        session.add(row)


def main():
    print('put_historical_data')
    put_historical_data()

    print('put_forecast_data')
    put_forecast_data()

    session.commit()
    print('Finished.')


if __name__ == '__main__':
    main()