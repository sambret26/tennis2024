# -*- coding: utf-8 -*-

# Global packages
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import os

# My packages
from databases.repositories.messagesRepository import MessagesRepository
from databases.repositories.rankingsRepository import RankingsRepository
from databases.repositories.playersRepository import PlayersRepository
from databases.repositories.matchsRepository import MatchsRepository
from databases.repositories.courtsRepository import CourtsRepository
from databases.repositories.teamsRepository import TeamsRepository
from databases.base import engine, session
from constants import constants
import functions as F

messagesRepository = MessagesRepository(engine)
rankingsRepository = RankingsRepository(engine)
playersRepository = PlayersRepository(engine)
matchsRepository = MatchsRepository(engine)
courtsRepository = CourtsRepository(engine)
teamsRepository = TeamsRepository(engine)

load_dotenv()

accessToken = None
tokenExpiry = None

def sendGetRequest(url):
    headers = {"Authorization" : f"Bearer {getToken()}"}
    response = requests.get(url, headers = headers)
    if response.status_code == 200:
        return response.json()
    print("Erreur de la requete get : " + url)
    print(response.text)
    print(response.json())
    return None

def sendPostRequestWithJson(url, headers, json):
    response = requests.post(url, headers=headers, json=json)
    if response.status_code == 200:
        return True
    print("Erreur de la requete post : " + url)
    print(str(json))
    print(response.text)
    print(response.json())
    return False

def sendDeleteRequestWithJson(url, headers, json):
    response = requests.delete(url, headers=headers, json=json)
    if response.status_code == 200:
        return True
    print("Erreur de la requete delete : " + url)
    print(str(json))
    print(response.text)
    print(response.json())
    return False

def getRefreshToken():
    return os.environ.get("RefreshToken")

def getToken():
    global accessToken, tokenExpiry
    if accessToken and tokenExpiry and tokenExpiry > datetime.now():
        return accessToken
    url = os.environ.get("TokenUrl")
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id" : os.environ.get("ClientId"),
        "client_secret" : os.environ.get("ClientSecret"),
        "grant_type" : "refresh_token",
        "refresh_token" : getRefreshToken()
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        tokenData = response.json()
        accessToken = tokenData["access_token"]
        tokenExpiry = datetime.now() + timedelta(seconds=(tokenData["expires_in"]-30))
        return accessToken
    accessToken = None
    print("Erreur lors de la récupération du token")
    print(response.text)
    print(response.json())
    return None

def getHomologationId():
    competition = sendGetRequest(os.environ.get("CompetitionUrl"))
    if not competition : return None
    return str(competition["competitions"][0]["homologationId"])

def getEpreuves():
    return sendGetRequest(os.environ.get("EpreuvesUrl").replace("HOMOLOGATION_ID", getHomologationId()))

def getPlayersInformations(retry=5):
    players = []
    teams = []
    epreuves = getEpreuves()
    for epreuve in epreuves:
        category = epreuve["libelle"][0:2]
        datas = sendGetRequest(os.environ.get("EpreuvesDataUrl").replace("EPREUVE_ID", str(epreuve['epreuveId'])))
        for player in datas["listJoueurInscrit"]:
            if category.startswith("S"): addPlayerinPlayersList(players, player, category, False)
            else : addPlayersAndTeamInLists(players, teams, player, category, False)
        for player in datas["listJoueurAttente"]:
            if category.startswith("S"): addPlayerinPlayersList(players, player, category, True)
            else : addPlayersAndTeamInLists(players, teams, player, category, True)
    return players, teams

def getMatchsInformations():
    matchs = []
    epreuves = getEpreuves()
    for epreuve in epreuves:
        matchNumber = 1
        tabNumber = 1
        datas = sendGetRequest(os.environ.get("EpreuvesDataUrl").replace("EPREUVE_ID", str(epreuve['epreuveId'])))
        positionOrder = {"TOP": 0, "CLASSIQUE": 1, "BOTTOM": 2}
        for decoupage in datas["decoupageDisplayList"]:
            if decoupage["typeDecoupage"] == "POU" :
                url = os.environ.get("MatchsUrlPoules").replace("DECOUPAGE", str(decoupage['decoupageId']))
            else :
                url = os.environ.get("MatchsUrl").replace("DECOUPAGE", str(decoupage['decoupageId']))
                url = f"https://moja.fft.fr/moja/api/spa/tableaux/{decoupage['tableauActifId']}/matchs"
            tabDatas = sendGetRequest(url)
            if decoupage["typeDecoupage"] == "POU":
                tabName = "TP" + epreuve["libelle"][0:2]
            elif decoupage["typeDecoupage"] == "TFI":
                tabDatas = sorted(tabDatas, key=lambda x: (int(x["numeroMatch"][3]), int(x["numeroMatch"][1]), positionOrder[x["position"]], int(x["numeroMatch"][5])))
                tabName = "TF" + epreuve["libelle"][0:2]
            else :
                tabDatas = sorted(tabDatas, key=lambda x: (int(x["numeroMatch"][3]), int(x["numeroMatch"][1]), positionOrder[x["position"]], int(x["numeroMatch"][5])))
                tabName = "T" + str(tabNumber) + epreuve["libelle"][0:2]
                tabNumber += 1
            for match in matchs:
                if not match["nextRound"] : match["nextRound"] = tabName
            for match in tabDatas :
                addMatch(matchs, match, matchNumber, tabName)
                matchNumber += 1
    return matchs

def getCourtInformations():
    list = []
    competition = sendGetRequest(os.environ.get("CompetitionUrl"))
    if not competition : return None
    courts = competition["competitions"][0]["courts"]
    for court in courts:
        newCourt = {
            "Name" : court["numero"],
            "FftId" : court["courtId"]
        }
        list.append(newCourt)
    return list

def setPlayer(matchFftId, player, letter):
    url = os.environ.get("SetPlayerUrl").replace("PLAYER", letter).replace("MATCHFFTID", str(matchFftId))
    headers = {"Authorization" : f"Bearer {getToken()}", "Content-Type" : "application/json"}
    json = {
        "inscriptionId" : player.inscriptionId,
        "joueur1Id" : player.fftId,
        "echelonJoueur1" : 120,
        "joueur2Id" : None,
        "echelonJoueur2" : None
    }
    return sendPostRequestWithJson(url, headers, json)

def deletePlayer(matchFftId, player, letter):
    url = os.environ.get("UnsetPlayerUrl").replace("PLAYER", letter).replace("MATCHFFTID", str(matchFftId))
    headers = {"Authorization" : f"Bearer {getToken()}", "Content-Type" : "application/json"}
    json = {
        "inscriptionId" : player.inscriptionId,
        "joueur1Id" : player.fftId,
        "echelonJoueur1" : 120,
        "joueur2Id" : None,
        "echelonJoueur2" : None
    }
    return sendDeleteRequestWithJson(url, headers, json)

def schedule(matchFftId):
    match = matchsRepository.getMatchInfosByFftId(session, matchFftId)
    courtFftId = courtsRepository.getCourtFftIdById(session, match.courtId)
    if not match.day or not match.hour :
        unschedule(match)
        return
    date = F.getStart(match.day, match.hour)
    url = os.environ.get("ScheduleUrl").replace("MATCHFFTID", str(matchFftId))
    headers = {"Authorization" : f"Bearer {getToken()}", "Content-Type" : "application/json"}
    json = {
        "matchId" : match.fftId,
        "homologationId" : getHomologationId(),
        "courtId" : courtFftId,
        "duree": 90,
        "dateProgrammation" : date,
    }
    return sendPostRequestWithJson(url, headers, json)

def unschedule(match):
    url = os.environ.get("UnscheduleUrl").replace("MATCHFFTID", str(match.fftId))
    return sendGetRequest(url)

def addPlayerinPlayersList(players, player, category, waitingList):
    fftId = player["joueur1Id"]
    inscriptionId = player["inscriptionId"]
    firstName = player["joueur1Prenom"].title()
    lastName = player["joueur1Nom"].upper()
    club = player["clubJoueur1"]
    ranking = player["classementJoueur1"]
    addPlayer(players, fftId, inscriptionId, firstName, lastName, club, ranking, category, waitingList)

def addPlayersAndTeamInLists(players, teams, player, category, waitingList):
    fftId1 = player["joueur1Id"]
    inscriptionId1 = player["inscriptionId"]
    firstName1 = player["joueur1Prenom"].title()
    lastName1 = player["joueur1Nom"].upper()
    club = player["clubJoueur1"]
    doubleRanking = player["classementJoueur1"]
    ranking = rankingsRepository.getSimpleRankingByDoubleRanking(session, doubleRanking)
    addPlayer(players, fftId1, inscriptionId1, firstName1, lastName1, club, ranking, category, waitingList)
    if player["joueur2Nom"]:
        fftId2 = player["joueur2Id"]
        inscriptionId2 = player["inscriptionId"]
        firstName2 = player["joueur2Prenom"].title()
        lastName2 = player["joueur2Nom"].upper()
        club = player["clubJoueur2"]
        doubleRanking = player["classementJoueur2"]
        ranking = rankingsRepository.getSimpleRankingByDoubleRanking(session, doubleRanking)
        addPlayer(players, fftId2, inscriptionId2, firstName2, lastName2, club, ranking, category, waitingList)
        teamRanking = player["poidsEquipe"]
        fftIdTeam = player["inscriptionId"]
        addTeam(teams, fftIdTeam, firstName1, lastName1, firstName2, lastName2, teamRanking)

def addPlayer(players, fftId, inscriptionId, firstName, lastName, club, ranking, category, waitingList):
    for player in players:
        if player["Firstname"] == firstName and player["Lastname"] == lastName:
            player[category] = True
            return
    newPlayer = {'FftId' : fftId, 'InscriptionId' : inscriptionId, 'Firstname': firstName, 'Lastname': lastName, 'Club': club, 'Ranking': ranking}
    for cat in constants.CATEGORIES:
        if (cat == category):
            if waitingList: newPlayer[cat] = 2
            else : newPlayer[cat] = 1
        else : newPlayer[cat] = 0
    players.append(newPlayer)

def addTeam(teams, fftId, firstName1, lastName1, firstName2, lastName2, teamRanking):
    newTeam = {'FftId' : fftId, 'Firstname1': firstName1, 'Lastname1': lastName1, 'Firstname2': firstName2, 'Lastname2': lastName2, 'Ranking': teamRanking}
    teams.append(newTeam)

def addMatch(matchs, match, matchNumber, tabName):
    category = match["nomCategorie"][0:2]
    if category.startswith("S"):
        player1Id, player2Id = getPlayersIds(match)
    else:
        player1Id, player2Id = getTeamsIds(match)
    winner = match["equipeGagnante"]
    winnerId = None
    if winner == "equipeA" : winnerId = player1Id
    elif winner == "equipeB" : winnerId = player2Id
    finish = (winnerId != None)
    score = ""
    sets = match["sets"]
    if not sets : sets = []
    for set in sets :
        if set['scoreA'] == set['scoreB'] == 0 : break
        if score != "" : score += " "
        if winner == "equipeA": score += f"{set['scoreA']}/{set['scoreB']}"
        elif winner == "equipeB": score += f"{set['scoreB']}/{set['scoreA']}"
    if score == "" : score = None
    if tabName.startswith("TF") and match["tourCode"] == "1":
        nextRound = "Vainqueur"
    elif  match["matchsSuivants"] != []:
        nextRound = category + match["matchsSuivants"][0]["numeroMatch"]
    else :
        nextRound = None
    if len(match["matchsPrecedents"]) == 1 :
        previousMatch = match["matchsPrecedents"][0]
        if match["position"] == "TOP" and not player2Id : player2Id = getMatchName(matchs, previousMatch["matchId"])
        if match["position"] in ["BOTTOM", "CLASSIQUE"] and not player1Id : player1Id = getMatchName(matchs, previousMatch["matchId"])
    if len(match["matchsPrecedents"]) == 2 :
        player1Id = getMatchName(matchs, match["matchsPrecedents"][0]["matchId"])
        player2Id = getMatchName(matchs, match["matchsPrecedents"][1]["matchId"])
    if match["haveQe"]:
        if match["position"] == "TOP" and not player2Id : player2Id = "QE"
        if match["position"] == "BOTTOM" and not player1Id : player1Id = "QE"
        if match["position"] == "CLASSIQUE" and not player1Id : player1Id = "QE"
        if match["position"] == "CLASSIQUE" and not player2Id : player2Id = "QE"
        #Pour les tableaux finaux, on peut avoir 2 QE (indépendamment de la position du match)
        if match["typeDecoupage"] == "TFI" and not player1Id : player1Id = "QE"
        if match["typeDecoupage"] == "TFI" and not player2Id : player2Id = "QE"
    matchName = category + str(matchNumber).zfill(2)
    program = match["dateProgrammation"]
    (day, hour) = parseProgram(program)
    courtFftId = match["courtId"]
    courtId = courtsRepository.getCourtIdByFftId(session, courtFftId)
    newMatch = {
        "fftId" : match["matchId"],
        "category" : category,
        "name" : matchName,
        "player1Id" : player1Id,
        "player2Id" : player2Id,
        "winnerId" : winnerId,
        "score" : score,
        "panel" : tabName,
        "nextRound" : nextRound,
        "finish" : finish,
        "day" : day,
        "hour" : hour,
        "courtId" : courtId
    }
    if match["numeroMatch"] : setNextRound(matchs, category + match["numeroMatch"], matchName)
    matchs.append(newMatch)

def updateDBPlayers(players):
    playersRepository.setAllPlayersToZero(session)
    for player in players:
        id = playersRepository.searchPlayer(session, player)
        if id:
            checkCategories(player, id)
            checkRanking(player,id)
            playersRepository.setPlayerToOne(session, player, id)
        else:
            playersRepository.insertPlayer(session, player)
            sendNotifAdd(player)
    for playerToRemove in playersRepository.getPlayersAtZero(session):
        playersRepository.deletePlayerById(session, playerToRemove.id)
        sendNotifRemove(playerToRemove)

def updateDBTeams(teams):
    teamsRepository.setAllTeamsToZero(session)
    for team in teams:
        player1Id = playersRepository.getPlayerIdByName(session, team["Lastname1"], team["Firstname1"])
        player2Id = playersRepository.getPlayerIdByName(session, team["Lastname2"], team["Firstname2"])
        id = teamsRepository.getTeamByPlayersIds(session, player1Id, player2Id)
        if id:
            teamsRepository.setTeamToOne(session, id)
        else:
            teamsRepository.insertTeam(session, team['FftId'], player1Id, player2Id, team["Ranking"])
    teamsRepository.deleteTeamsAtZero(session)

def updateDBMatchs(matchs):
    matchsRepository.setAllMatchsToZero(session)
    for match in matchs:
        matchInDB = matchsRepository.getAllMatchInfosByName(session, match["name"])
        if matchInDB:
            if not matchEquals(matchInDB, match): matchsRepository.updateMatch(session, matchInDB.id, match)
            matchsRepository.setMatchToOne(session, matchInDB.id)
        else: matchsRepository.insertMatch2(session, match)
    matchsRepository.deleteMatchsAtZero(session)

def updateDBCourts(courts):
    for court in courts:
        courtInDB = courtsRepository.getCourtByFftId(session, court['FftId'])
        if not courtInDB :
            courtInDB = courtsRepository.getCourtIdByName(session, court['Name'])
            if courtInDB: courtsRepository.setFftIdById(session, courtInDB, court['FftId'])
            else : courtsRepository.insertCourt(session, court)
    return

def updatePlayers():
    players, teams = getPlayersInformations()
    updateDBPlayers(players)
    updateDBTeams(teams)

def updateMatchs():
    matchs = getMatchsInformations()
    updateDBMatchs(matchs)

def updateCourts():
    courts = getCourtInformations()
    updateDBCourts(courts)

def getMatchName(matchs, matchFftId):
    for match in matchs:
        if match["fftId"] == matchFftId : return "V" + match["name"]
    return None

def checkCategories(player, id):
    categoriesInDB = playersRepository.getCategoriesById(session, id)
    for (index, category) in [(0, "SM"), (1, "SD"), (2, "DM"), (3, "DD"), (4, "DX")]:
        if (categoriesInDB[index] == 0 and player[category] == 1): #Inscription liste principale
            message = f"Nouvelle inscription : {player['Firstname']} {player['Lastname']} ({player['Club']}) classé(e) {player['Ranking']}"
            messagesRepository.insertMessage(session, category, message)
        elif (categoriesInDB[index] == 1 and player[category] == 0): #Désinscription liste principale
            message = f"Désinscription de {player['Firstname']} {player['Lastname']} ({player['Club']}) classé(e) {player['Ranking']}"
            messagesRepository.insertMessage(session, category, message)
        elif (categoriesInDB[index] == 0 and player[category] == 2): #Inscription liste d'attente
            message = f"Nouvelle inscription en liste d'attente : {player['Firstname']} {player['Lastname']} ({player['Club']}) classé(e) {player['Ranking']}"
            messagesRepository.insertMessage(session, category, message)
        elif (categoriesInDB[index] == 2 and player[category] == 0): #Désinscription liste d'attente
            message = f"Désinscription en liste d'attente de {player['Firstname']} {player['Lastname']} ({player['Club']}) classé(e) {player['Ranking']}"
            messagesRepository.insertMessage(session, category, message)
        elif (categoriesInDB[index] == 1 and player[category] == 2): #Passage en liste d'attente
            message = f"Passage de liste principale à liste d'attente de {player['Firstname']} {player['Lastname']} ({player['Club']}) classé(e) {player['Ranking']}"
            messagesRepository.insertMessage(session, category, message)
        elif (categoriesInDB[index] == 2 and player[category] == 1): #Passage en liste principale
            message = f"Passage de liste d'attente à liste principale de {player['Firstname']} {player['Lastname']} ({player['Club']}) classé(e) {player['Ranking']}"
            messagesRepository.insertMessage(session, category, message)

def checkRanking(player, id):
    playerInDB = playersRepository.getPlayerInfosById(session, id)
    if playerInDB.ranking != player['Ranking']:
        message = f"Reclassement : {playerInDB.firstName} {playerInDB.lastName} ({playerInDB.ranking} => {player['Ranking']})"
        messagesRepository.insertMessage(session, "G", message)

def sendNotifAdd(player):
    message = f"Nouvelle inscription : {player['Firstname']} {player['Lastname']} ({player['Club']}) classé(e) {player['Ranking']}"
    waitingMessage = f"Nouvelle inscription en liste d'attente : {player['Firstname']} {player['Lastname']} ({player['Club']}) classé(e) {player['Ranking']}"
    messagesRepository.insertMessage(session, "G", message)
    for category in constants.CATEGORIES:
        if player[category] == 1 : messagesRepository.insertMessage(session, category, message)
        elif player[category] == 2 : messagesRepository.insertMessage(session, category, waitingMessage)

def sendNotifRemove(player):
    message = f"Désinscription de {player.firstName} {player.lastName} ({player.club}) classé(e) {player.ranking}"
    waitingMessage = f"Désinscription en liste d'attente de {player.firstName} {player.lastName} ({player.club}) classé(e) {player.ranking}"
    messagesRepository.insertMessage(session, "G", message)
    for (category, index) in [("SM", 6), ("SD", 7), ("DM", 8), ("DD", 9), ("DX", 10)]:
        if player[index] == 1 : messagesRepository.insertMessage(session, category, message)
        if player[index] == 2 : messagesRepository.insertMessage(session, category, waitingMessage)

def parseProgram(program):
    if not program : return (None, None)
    m = program[5:7]
    d = program[8:10]
    h = program[11:13]
    min = program[14:16]
    if h[0] == "0" : h = h[1]
    if min == "00" : min = ""
    day = f"{d}/{m}"
    hour = f"{h}H{min}"
    return (day, hour)

def getPlayersIds(match):
    player1Id = None
    if len(match["joueurList"]) > 0 :
        player1 = match["joueurList"][0]
        player1Id = getPlayerIdByInfos(player1)
    player2Id = None
    if len(match["joueurList"]) > 1 :
        player2 = match["joueurList"][1]
        player2Id = getPlayerIdByInfos(player2)
    if match["position"] == "TOP" : return player1Id, player2Id
    return player2Id, player1Id

def getTeamsIds(match):
    player1Id = None
    if len(match["joueurList"]) > 0 :
        player1 = match["joueurList"][0]
        player1Id = getPlayerIdByInfos(player1)
    player2Id = None
    if len(match["joueurList"]) > 1 :
        player2 = match["joueurList"][1]
        player2Id = getPlayerIdByInfos(player2)
    player3Id = None
    if len(match["joueurList"]) > 2 :
        player3 = match["joueurList"][2]
        player3Id = getPlayerIdByInfos(player3)
    player4Id = None
    if len(match["joueurList"]) > 3 :
        player4 = match["joueurList"][3]
        player4Id = getPlayerIdByInfos(player4)
    team1Id = None
    if(player1Id and player2Id) : team1Id = teamsRepository.getTeamByPlayersIds(session, player1Id, player2Id)
    team2Id = None
    if(player3Id and player4Id) : team2Id = teamsRepository.getTeamByPlayersIds(session, player3Id, player4Id)
    if match["position"] == "TOP" : return team1Id, team2Id
    return team2Id, team1Id

def getPlayerIdByInfos(player):
    lastName = player["nom"].upper()
    firstName = player["prenom"].title()
    return playersRepository.getPlayerIdByName(session, lastName, firstName)


def setNextRound(matchs, matchNumber, matchName):
    for match in matchs:
        if match["nextRound"] == matchNumber:
            match["nextRound"] = matchName

def matchEquals(m1, m2):
    if m1.player1Id != str(m2["player1Id"]): return False
    if m1.player2Id != str(m2["player2Id"]): return False
    if m1.winnerId != m2["winnerId"]: return False
    if m1.courtId != m2["courtId"]: return False
    if m1.day != m2["day"]: return False
    if m1.hour != m2["hour"]: return False
    if m1.score != m2["score"]: return False
    if m1.panel != m2["panel"]: return False
    if m1.nextRound != m2["nextRound"]: return False
    return True
