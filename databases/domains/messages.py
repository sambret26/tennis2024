from sqlalchemy import Column, Integer, String
from databases.base import Base

class Message(Base):
    __tablename__ = 'Messages'
    id = Column(Integer, primary_key=True)
    category = Column(String, nullable=False)
    message = Column(String)
