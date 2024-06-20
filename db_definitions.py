from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class HistoricalData(Base):
    __tablename__ = 'historical_data'
    local_date = Column(DateTime, primary_key=True)
    temperature = Column(Float)

engine = create_engine('sqlite:///weather_data.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

session = Session()
