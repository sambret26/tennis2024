from sqlalchemy import Column, Integer, String, CheckConstraint
from databases.base import Base

class Player(Base):
    __tablename__ = 'Players'
    id = Column(Integer, primary_key=True)
    fftId = Column(Integer)
    inscriptionId = Column(Integer)
    firstName = Column(String(50), nullable=False)
    lastName = Column(String(100), nullable=False)
    ranking = Column(String(10), nullable=False)
    club = Column(String(100), nullable=False)
    sm = Column(Integer, CheckConstraint('sm IN (0, 1)'))
    sd = Column(Integer, CheckConstraint('sd IN (0, 1)'))
    dm = Column(Integer, CheckConstraint('dm IN (0, 1)'))
    dd = Column(Integer, CheckConstraint('dd IN (0, 1)'))
    dx = Column(Integer, CheckConstraint('dx IN (0, 1)'))
    state = Column(Integer, CheckConstraint('state IN (0, 1)'))
