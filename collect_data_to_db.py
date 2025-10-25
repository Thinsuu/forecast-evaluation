from db_definitions import CityName, ForecastData, session, HistoricalData
import prepare_rows


def put_historical_data():
    existing_dates = session.query(
        HistoricalData.city_id, HistoricalData.weather_website, HistoricalData.local_date).all()
    
    existing_cities_in_city_names_table = session.query(CityName.city_id).all()  # SELECT city_id FROM city_name
    fromjson_cityid_cityname = {}

    from_json = prepare_rows.historical_dataset_prep()
    for city_id, website_name, local_date, temperature, precipitation, wind_speed, city_name in from_json:
        fromjson_cityid_cityname[city_id] = city_name
        key_row = (city_id, website_name, local_date)
        if key_row in existing_dates:
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
        existing_dates.append(key_row)

    for city_id_from_dict, city_name_from_dict in fromjson_cityid_cityname.items():
        if (city_id_from_dict,) not in existing_cities_in_city_names_table:
            print('City name to add:', city_name_from_dict)
            name_row = CityName(
                city_name=city_name_from_dict,
                weather_website='SMHI',
                city_id=city_id_from_dict,
            )
            session.add(name_row)


def put_forecast_data():
    existing_dates = session.query(
        ForecastData.city_id, ForecastData.weather_website, ForecastData.local_date, ForecastData.time_difference).all()

    from_json = prepare_rows.forecast_dataset_prep()
    for city_id, website_name, local_date, time_dif_hours, temperature, precipitation, wind_speed in from_json:
        local_date = local_date.replace(tzinfo=None)
        key_row = (city_id, website_name, local_date, time_dif_hours)
        if key_row in existing_dates:
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
        existing_dates.append(key_row)


def main():
    print('put_historical_data')
    put_historical_data()

    print('put_forecast_data')
    put_forecast_data()

    session.commit()
    print('Finished.')


if __name__ == '__main__':
    main()