# -*- coding: utf-8 -*-

# Global packages

# My packages
from databases.repositories.settingsRepository import SettingsRepository
from databases.repositories.playersRepository import PlayersRepository
from databases.repositories.matchsRepository import MatchsRepository
from databases.base import engine, session
import moja
import cal

settingsRepository = SettingsRepository(engine)
playersRepository = PlayersRepository(engine)
matchsRepository = MatchsRepository(engine)

def setCourt(matchId, courtId):
    matchsRepository.setCourt(session, matchId, courtId)
    updateEvent(matchId)

def setPlayer1(matchId, playerId):
    matchsRepository.setPlayer1(session, matchId, playerId)
    matchFftId = matchsRepository.getFftIdById(session, matchId)
    player = playersRepository.getPlayerById(session, playerId)
    if settingsRepository.isMojaActive(session) == 1 : moja.setPlayer(matchFftId, player, "A")
    if settingsRepository.isCalendarActive(session) == 1 : cal.updateOneEvent(matchId)

def setPlayer2(matchId, playerId):
    matchsRepository.setPlayer1(session, matchId, playerId)
    matchFftId = matchsRepository.getFftIdById(session, matchId)
    player = playersRepository.getPlayerById(session, playerId)
    if settingsRepository.isMojaActive(session) == 1 : moja.setPlayer(matchFftId, player, "B")
    if settingsRepository.isCalendarActive(session) == 1 : cal.updateOneEvent(matchId)

def setDay(matchId, day):
    matchsRepository.setDay(session, matchId, day)
    updateEvent(matchId)

def setHour(matchId, hour):
    matchsRepository.setHour(session, matchId, day)
    updateEvent(matchId)

def setPg(matchId, day, hour):
    matchsRepository.setDay(session, matchId, day)
    matchsRepository.setHour(session, matchId, hour)
    updateEvent(matchId)

def setWinner(id, winner):
    matchsRepository.setWinner(session, id, winner)
    #TODO

def setScore(id, res):
    matchsRepository.setScore(session, id, res)
    #TODO

def updateEvent(matchId):
    matchFftId = matchsRepository.getFftIdById(session, matchId)
    if settingsRepository.isMojaActive(session) == 1 : moja.schedule(matchFftId)
    if settingsRepository.isCalendarActive(session) == 1 : cal.updateOneEvent(matchId)
