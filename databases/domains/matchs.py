from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from databases.base import Base

class Match(Base):
    __tablename__ = 'Matchs'
    id = Column(Integer, primary_key=True)
    fftId = Column(Integer)
    category = Column(String, nullable=False)
    name = Column(String, nullable=False)
    player1Id = Column(String, ForeignKey('Players.id'))
    player2Id = Column(String, ForeignKey('Players.id'))
    day = Column(String)
    hour = Column(String)
    courtId = Column(Integer, ForeignKey('Courts.id'))
    finish = Column(Integer, CheckConstraint('finish IN (0, 1)'))
    winnerId = Column(Integer, ForeignKey('Players.id'))
    notif = Column(Integer, CheckConstraint('notif IN (0, 1)'))
    score = Column(String)
    panel = Column(String)
    nextRound = Column(String)
    calId = Column(String)
    state = Column(Integer, CheckConstraint('state IN (0, 1)'))
