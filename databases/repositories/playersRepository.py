from databases.domains.players import Player
from sqlalchemy.orm import sessionmaker
from databases.base import Base
from sqlalchemy import func

class PlayersRepository:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)

    # GETTERS
    def searchPlayer(self, session, player):
        return session.query(Player.id).filter(Player.firstName == player['Firstname'], Player.lastName == player['Lastname'], Player.club == player['Club']).scalar()

    def getPlayerById(self, session, id):
        return session.query(Player).filter(Player.id == id).first()

    def getPlayersAtZero(self, session):
        return session.query(Player).filter(Player.state == 0).all()

    def getCategoriesById(self, session, id):
        return session.query(Player.sm, Player.sd, Player.dm, Player.dd, Player.dx).filter(Player.id == id).first()

    def getPlayerInfosById(self, session, id):
        return session.query(Player.firstName, Player.lastName, Player.ranking).filter(Player.id == id).first()

    def getNumberPlayers(self, session):
        return session.query(func.count(Player.id)).scalar()

    def getNumberPlayersByCategory(self, session, category):
        return session.query(func.count(Player.id)).filter(getattr(Player, category.lower()) == 1).scalar()

    def getRankings(self, session):
        return [player[0] for player in session.query(Player.ranking).all()]

    def getRankingsByCategory(self, session, category):
        return [player[0] for player in session.query(Player.ranking).filter(getattr(Player, category.lower()) == 1).all()]

    def getPlayerIdByName(self, session, lastname, firstname):
        return session.query(Player.id).filter(Player.lastName == lastname, Player.firstName == firstname).scalar()

    def getPlayers(self, session):
        return session.query(Player.firstName, Player.lastName, Player.ranking).all()

    def getPlayerNameById(self, session, id):
        return session.query(Player.lastName, Player.firstName).filter(Player.id == id).first()

    def getFftIdAndInscriptionIdById(self, session, id):
        return session.query(Player.fftId, Player.inscriptionId).filter(Player.id == id).first()

    # SETTERS
    def setAllPlayersToZero(self, session):
        session.query(Player).update({Player.state: 0})
        session.commit()

    def setPlayerToOne(self, session, player, id):
        session.query(Player).filter(Player.id == id).update({Player.state: 1, Player.sm: player["SM"], Player.sd: player["SD"], Player.dm: player["DM"], Player.dd: player["DD"], Player.dx: player["DX"]})
        session.commit()

    # INSERT
    def insertPlayer(self, session, player):
        newPlayer = Player(fftId=player['FftId'], inscriptionId=player['InscriptionId'], firstName=player["Firstname"], lastName=player["Lastname"], ranking=player["Ranking"], club=player["Club"], sm=player["SM"], sd=player["SD"], dm=player["DM"], dd=player["DD"], dx=player["DX"])
        session.add(newPlayer)
        session.commit()

    # DELETE
    def deletePlayerById(self, session, id):
        playerToDelete = session.query(Player).filter(Player.id == id).first()
        if playerToDelete:
            session.delete(playerToDelete)
            session.commit()
            return True
        return False
