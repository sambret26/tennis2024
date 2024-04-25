from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint
from databases.base import Base

class Team(Base):
    __tablename__ = 'Teams'
    id = Column(Integer, primary_key=True)
    fftId = Column(Integer)
    player1Id = Column(Integer, ForeignKey('Players.id'))
    player2Id = Column(Integer, ForeignKey('Players.id'))
    ranking = Column(Integer, nullable=False)
    state = Column(Integer, CheckConstraint('state IN (0, 1)'))
