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
        result = session.query(Ranking).filter(Ranking.fft == fftId).scalar()
        return result

    def getSimpleRankingByDoubleRanking(self, session, double):
        return session.query(Ranking.simple).filter(Ranking.double == double).scalar()

    def getSimpleRankingByFftRanking(self, session, fftId):
        return session.query(Ranking.simple).filter(Ranking.fft == fftId).scalar()

    # SETTERS
    def setFftRankingBySimpleRanking(self, session, simple, fftId):
        session.query(Ranking).filter(Ranking.simple == simple).update({Ranking.fft: fftId})
        session.commit()

    def setFftRankingByDoubleRanking(self, session, double, fftId):
        session.query(Ranking).filter(Ranking.double == double).update({Ranking.fft: fftId})
        session.commit()

    #INSERT
    def insertRanking(self, session, simple, double, fftId):
        newRanking = Ranking(simple=simple, double=double, fft=fftId)
        session.add(newRanking)
        session.commit()
