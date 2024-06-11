from databases.domains.settings import Setting
from sqlalchemy.orm import sessionmaker
from databases.base import Base
from sqlalchemy import func

class SettingsRepository:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)

    def isCalendarActive(self, session):
        return session.query(Setting.state).filter(Setting.data == "CalendarActive").scalar()

    def isMojaActive(self, session):
        return session.query(Setting.state).filter(Setting.data == "MojaActive").scalar()

    def getCalendarStatus(self, session):
        return session.query(Setting.state).filter(Setting.data == "CalendarState").scalar()

    def isRefreshTokenOk(self, session):
        return session.query(Setting.state).filter(Setting.data == "RefreshTokenOk").scalar()

    def setCalendarActive(self, session, value):
        session.query(Setting).filter(Setting.data == "CalendarActive").update({Setting.state: value})
        session.commit()

    def setMojaActive(self, session, value):
        session.query(Setting).filter(Setting.data == "MojaActive").update({Setting.state: value})
        session.commit()

    def setCalendarStatus(self, session, value):
        session.query(Setting).filter(Setting.data == "CalendarState").update({Setting.state: value})
        session.commit()

    def setRefreshTokenOk(self, session, value):
        session.query(Setting).filter(Setting.data == "RefreshTokenOk").update({Setting.state: value})
        session.commit()
