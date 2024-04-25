from sqlalchemy import Column, Integer, String
from databases.base import Base

class Channel(Base):
    __tablename__ = 'Channels'
    id = Column(Integer, primary_key=True)
    category = Column(String, nullable=False)
    channelId = Column(Integer)
    type = Column(String)
