import os

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_MODE = os.environ.get('DB_MODE', 'sqlite')

Base = declarative_base()

class HistoricalData(Base):
    __tablename__ = 'historical_data'
    city_id = Column(Integer)
    weather_website = Column(String)
    local_date = Column(DateTime)
    temperature = Column(Float)
    precipitation = Column(Float)
    wind_speed = Column(Float)
    __table_args__ = (
        PrimaryKeyConstraint('city_id', 'weather_website', 'local_date', name='historical_data_pk'),
    )

class ForecastData(Base):
    __tablename__ = 'forecast_data'
    city_id = Column(Integer)
    weather_website = Column(String)
    local_date = Column(DateTime)
    time_difference = Column(Integer)
    temperature = Column(Float)
    precipitation = Column(Float)
    wind_speed = Column(Float)
    __table_args__ = (
        PrimaryKeyConstraint('city_id', 'weather_website', 'local_date', 'time_difference', name='forecast_data_pk'),
    )


class CityName(Base):
    __tablename__ = 'city_name'
    city_id = Column(Integer)
    weather_website = Column(String)
    city_name = Column(String)
    __table_args__ = (
        PrimaryKeyConstraint('city_id', 'weather_website', name='city_name_pk'),
    )


if DB_MODE == 'postgresql':
    print('Using PostgreSQL')
    db_username = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')
    db_address = os.environ.get('DB_ADDRESS')

    if not all([db_username, db_password, db_address]):
        raise ValueError('Please provide all DB_USER, DB_PASSWORD, DB_ADDRESS!')

    engine = create_engine(f'postgresql://{db_username}:{db_password}@{db_address}/forecast_evaluation')
else:
    print('Using SQLite')
    engine = create_engine('sqlite:///weather_data.db')


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

session = Session()
