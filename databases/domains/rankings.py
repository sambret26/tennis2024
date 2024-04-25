from sqlalchemy import Column, String, Integer
from databases.base import Base

class Ranking(Base):
    __tablename__ = 'Rankings'
    id = Column(Integer, primary_key=True)
    simple = Column(String)
    double = Column(String)
    fftSimple = Column(String)
    fftDouble = Column(String)
