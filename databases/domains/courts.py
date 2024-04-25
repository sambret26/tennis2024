from sqlalchemy import Column, Integer, String
from databases.base import Base

class Court(Base):
    __tablename__ = 'Courts'
    id = Column(Integer, primary_key=True)
    fftId = Column(Integer)
    name = Column(String(10))
