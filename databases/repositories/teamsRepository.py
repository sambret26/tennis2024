from databases.domains.teams import Team
from sqlalchemy.orm import sessionmaker
from databases.base import Base
from sqlalchemy import func

class TeamsRepository:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)

    # GETTERS
    def getTeamByPlayersIds(self, session, id1, id2):
        return session.query(Team.id).filter(Team.player1Id == id1, Team.player2Id == id2).scalar()

    def getTeamsToDelete(self, session, idList):
        return session.query(Team.id).filter(~Team.id.in_(idList)).all()

    def getTeamNameById(self, session, id):
        return session.query(Team.player1Id, Team.player2Id).filter(Team.id == id).first()

    def getTeamInfosById(self, session, id):
        return session.query(Team).filter(Team.id == id).first()

    def getTeams(self, session):
        return session.query(Team).all()

    #SETTERS
    def setAllTeamsToZero(self, session):
        session.query(Team).update({Team.state: 0})
        session.commit()

    def setTeamToOne(self, session, id):
        session.query(Team).filter(Team.id == id).update({Team.state: 1})
        session.commit()

    # INSERT
    def insertTeam(self, session, fftId, player1Id, player2Id, ranking):
        newTeam = Team(fftId=fftId, player1Id=player1Id, player2Id=player2Id, ranking=ranking)
        session.add(newTeam)
        session.commit()

    # DELETE
    def deleteTeamById(self, session, id):
        teamToDelete = session.query(Team).filter(Team.id == id).first()
        if teamToDelete:
            session.delete(teamToDelete)
            session.commit()
            return True
        return False

    def deleteTeamsAtZero(self, session):
        session.query(Team).filter(Team.state == 0).delete()
        session.commit()
