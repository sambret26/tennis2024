from databases.domains.courts import Court
from sqlalchemy.orm import sessionmaker
from databases.base import Base
from sqlalchemy import func

class CourtsRepository:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)

    # GETTERS
    def getCourtById(self, session, id):
        return session.query(Court).filter(Court.id == id).first()

    def getCourtByFftId(self, session, fftId):
        return session.query(Court).filter(Court.fftId == fftId).first()

    def getCourtByName(self, session, name):
        return session.query(Court).filter(Court.name == name).first()

    def getCourtIdByName(self, session, name):
        return session.query(Court.id).filter(Court.name == name).scalar()

    def getCourtNameById(self, session, id):
        return session.query(Court.name).filter(Court.id == id).scalar()

    def getCourtFftIdById(self, session, id):
        return session.query(Court.fftId).filter(Court.id == id).scalar()

    def getCourtIdByFftId(self, session, fftId):
        return session.query(Court.id).filter(Court.fftId == fftId).scalar()

    # SETTERS
    def setFftIdById(self, session, id, fftId):
        session.query(Court).filter(Court.id == id).update({Court.fftId: fftId})
        session.commit()

    # INSERT
    def insertCourt(self, session, court):
        newCourt = Court(fftId=court['FftId'], name=court['Name'])
        session.add(newCourt)
        session.commit()

    # DELETE
