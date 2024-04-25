from databases.domains.channels import Channel
from sqlalchemy.orm import sessionmaker
from databases.base import Base
from sqlalchemy import func

class ChannelsRepository:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)

    def getLogChannelId(self, session, category):
        return session.query(Channel.channelId).filter(Channel.category == category, Channel.type == "Logs").scalar()

    def getChannelCategory(self, session, channelId):
        return session.query(Channel.category).filter(Channel.channelId == channelId).scalar()
