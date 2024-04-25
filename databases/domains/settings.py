from sqlalchemy import Column, Integer, String, CheckConstraint
from databases.base import Base

class Setting(Base):
    __tablename__ = 'Settings'
    id = Column(Integer, primary_key=True)
    data = Column(String, nullable=False)
    state = Column(Integer, CheckConstraint('state IN (0, 1)'))
