from db_definitions import session, HistoricalData
import prepare_rows


def main():
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
    session.commit()
    print('Finished.')


if __name__ == '__main__':
    main()