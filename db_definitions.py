from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class HistoricalData(Base):
    __tablename__ = 'historical_data'
    local_date = Column(DateTime, primary_key=True)
    temperature = Column(Float)

class ForecastData(Base):
    __tablename__ = 'forecast_data'
    local_date = Column(DateTime)
    time_difference = Column(Integer)
    temperature = Column(Float)
    __table_args__ = (
        PrimaryKeyConstraint('local_date', 'time_difference', name='forecast_data_pk'),
    )

engine = create_engine('sqlite:///weather_data.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

session = Session()
