from databases.domains.rankings import Ranking
from sqlalchemy.orm import sessionmaker
from databases.base import Base
from sqlalchemy import func

class RankingsRepository:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)

    # GETTERS
    def getRankingsByFftRanking(self, session, fftId):
        result = session.query(Ranking.simple).filter(Ranking.fftSimple == fftId).scalar()
        if result != None : return result
        return session.query(Ranking.double).filter(Ranking.fftDouble == fftId).scalar()

    def getSimpleRankingByDoubleRanking(self, session, fftId):
        return session.query(Ranking.simple).filter(Ranking.double == fftId).scalar()

    def getSimpleRankingByFftRanking(self, session, fftId):
        result = session.query(Ranking.simple).filter(Ranking.fftSimple == fftId).scalar()
        if result != None : return result
        return session.query(Ranking.simple).filter(Ranking.fftDouble == fftId).scalar()

    # SETTERS
    def setFftSimpleRankingBySimpleRanking(self, session, simple, fftSimple):
        session.query(Ranking).filter(Ranking.simple == simple).update({Ranking.fftSimple: fftSimple})
        session.commit()

    def setFftDoubleRankingByDoubleRanking(self, session, double, fftDouble):
        session.query(Ranking).filter(Ranking.double == double).update({Ranking.fftDouble: fftDouble})
        session.commit()

    #INSERT
    def insertRanking(self, session, simple, double, fftSimple, fftDouble):
        newRanking = Ranking(simple=simple, double=double, fftSimple=fftSimple, fftDouble=fftDouble)
        session.add(newRanking)
        session.commit()
