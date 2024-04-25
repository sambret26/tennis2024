from databases.domains.matchs import Match
from sqlalchemy.orm import sessionmaker
from databases.base import Base
from sqlalchemy import func

class MatchsRepository:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)

    # GETTERS
    def getMatchsToPlay(self, session, date):
        return session.query(Match.id, Match.name, Match.player1Id, Match.player2Id, Match.hour, Match.courtId).filter(Match.day == date, Match.notif == 0).all()

    def getAllMatchInfosByName(self, session, name):
        return session.query(Match).filter(Match.name == name).first()

    def getMatchIdByName(self, session, name):
        return session.query(Match.id).filter(Match.name == name).scalar()

    def getMatchsByDate(self, session, date):
        return session.query(Match.name, Match.player1Id, Match.player2Id, Match.hour, Match.courtId).filter(Match.day == date).all()

    def getMatchs(self, session):
        return session.query(Match).filter(Match.day != None, Match.hour != None).all()

    def getMatchInfosById(self, session, id):
        return session.query(Match).filter(Match.id == id).first()

    def getMatchInfosByFftId(self, session, fftId):
        return session.query(Match).filter(Match.fftId == fftId).first()

    def getMatchsNamesByCategories(self, session, category):
        return session.query(Match.name).filter(Match.category == category).order_by(Match.name).all()

    def getMatchInfosByName(self, session, name):
        return session.query(Match.player1Id, Match.player2Id, Match.winnerId, Match.score, Match.panel, Match.nextRound).filter(Match.name == name).first()

    def getMatchsByDateAndCourt(self, session, date, courtId):
        return session.query(Match.hour, Match.name, Match.courtId).filter(Match.day == date, Match.courtId == courtId).all()

    def getMatchsNamesToDelete(self, session, nameList):
        return [match[0] for match in session.query(Match.name).filter(~Match.name.in_(nameList)).all()]

    def getMatchProgramByName(self, session, name):
        return session.query(Match.day, Match.hour, Match.courtId).filter(Match.name == name).first()

    def getMatchsToUnschedule(self, session, nameList):
        return [match[0] for match in session.query(Match.name).filter(Match.day != None, ~Match.name.in_(nameList)).all()]

    def getFftIdById(self, session, id):
        return session.query(Match.fftId).filter(Match.id == id).scalar()

    # SETTERS
    def setWinner(self, session, id, winnerId):
        session.query(Match).filter(Match.id == id).update({Match.winnerId: winnerId, Match.finish: 1})
        session.commit()

    def setCourt(self, session, id, courtId):
        session.query(Match).filter(Match.id == id).update({Match.courtId: int(courtId) if courtId is not None else None})
        session.commit()

    def setPlayer1(self, session, id, playerId):
        session.query(Match).filter(Match.id == id).update({Match.player1Id: playerId})
        session.commit()

    def setPlayer2(self, session, id, playerId):
        session.query(Match).filter(Match.id == id).update({Match.player2Id: playerId})
        session.commit()

    def setDay(self, session, id, day):
        session.query(Match).filter(Match.id == id).update({Match.day: day})
        session.commit()

    def setHour(self, session, id, hour):
        session.query(Match).filter(Match.id == id).update({Match.hour: hour})
        session.commit()

    def setNotifToSend(self, session, id):
        session.query(Match).filter(Match.id == id).update({Match.notif: 1})
        session.commit()

    def setScore(self, session, id, score):
        session.query(Match).filter(Match.id == id).update({Match.score: score})
        session.commit()

    def setPanel(self, session, id, panel):
        session.query(Match).filter(Match.id == id).update({Match.panel: panel})
        session.commit()

    def setNextRound(self, session, id, nextRound):
        session.query(Match).filter(Match.id == id).update({Match.nextRound: nextRound})
        session.commit()

    def setAllMatchsToZero(self, session):
        session.query(Match).update({Match.state: 0})
        session.commit()

    def setMatchToOne(self, session, id):
        session.query(Match).filter(Match.id == id).update({Match.state: 1})
        session.commit()

    def updateMatch(self, session, id, match):
        session.query(Match).filter(Match.id == id).update({Match.fftId: match["fftId"], Match.player1Id: match["player1Id"], Match.player2Id: match["player2Id"], Match.winnerId: match["winnerId"], Match.score: match["score"], Match.panel: match["panel"], Match.nextRound: match["nextRound"], Match.finish: match["finish"], Match.day: match["day"], Match.hour: match["hour"], Match.courtId: match["courtId"]})
        session.commit()

    def updatePlayerId(self, session, name, playerId):
        session.query(Match).filter(Match.player1Id == name).update({Match.player1Id: playerId})
        session.query(Match).filter(Match.player2Id == name).update({Match.player2Id: playerId})
        session.commit()

    def removeCalId(self, session):
        session.query(Match).update({Match.calId: None})
        session.commit()

    def updateEvent(self, session, id, calId):
        session.query(Match).filter(Match.id == id).update({Match.calId: calId})
        session.commit()

    #INSERT
    def insertMatch(self, session, category, name, player1Id, player2Id, day, hour, courtId, winnerId, score, panel, nextRound):
        newMatch = Match(category=category, name=name, player1Id=player1Id, player2Id=player2Id, day=day,hour=hour, courtId=courtId, winnerId=winnerId, score=score, panel=panel, nextRound=nextRound)
        session.add(newMatch)
        session.commit()

    def insertMatch2(self, session, match):
        newMatch = Match(fftId=match["fftId"], category=match["category"], name=match["name"], player1Id=match["player1Id"], player2Id=match["player2Id"], day=match["day"],hour=match["hour"], courtId=match["courtId"], winnerId=match["winnerId"], score=match["score"], panel=match["panel"], nextRound=match["nextRound"], finish=match["finish"])
        session.add(newMatch)
        session.commit()

    # DELETE
    def deleteMatchById(self, session, id):
        matchToDelete = session.query(Match).filter(Match.id == id).first()
        if matchToDelete:
            session.delete(matchToDelete)
            session.commit()
            return True
        return False

    def deleteMatchsAtZero(self, session):
        session.query(Match).filter(Match.state == 0).delete()
        session.commit()
