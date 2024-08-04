from db_definitions import ForecastData, session, HistoricalData
import prepare_rows


def put_historical_data():
    existing_dates = session.query(
        HistoricalData.city_id, HistoricalData.weather_website, HistoricalData.local_date).all()

    from_json = prepare_rows.historical_dataset_prep()
    for city_id, website_name, local_date, temperature, precipitation, wind_speed in from_json:
        if (city_id, website_name, local_date) in existing_dates:
            continue
        print(local_date, temperature, precipitation, wind_speed)
        row = HistoricalData(
            city_id=city_id,
            weather_website=website_name,
            local_date=local_date,
            temperature=temperature,
            precipitation=precipitation,
            wind_speed=wind_speed,
        )
        session.add(row)


def put_forecast_data():
    existing_dates = session.query(
        ForecastData.city_id, ForecastData.weather_website, ForecastData.local_date, ForecastData.time_difference).all()

    from_json = prepare_rows.forecast_dataset_prep()
    for city_id, website_name, local_date, time_dif_hours, temperature, precipitation, wind_speed in from_json:
        local_date = local_date.replace(tzinfo=None)
        if (city_id, website_name, local_date, time_dif_hours) in existing_dates:
            continue
        row = ForecastData(
            city_id=city_id,
            weather_website=website_name,
            local_date=local_date,
            time_difference=time_dif_hours,
            temperature=temperature,
            precipitation=precipitation,
            wind_speed=wind_speed,
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