from db_definitions import session, HistoricalData
import prepare_rows


def main():
    from_json = prepare_rows.historical_dataset_prep()
    for local_date, temperature in from_json:
        print(local_date, temperature)
        row = HistoricalData(
            local_date=local_date,
            temperature=temperature,
        )
        session.add(row)
    session.commit()


if __name__ == '__main__':
    main()