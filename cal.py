# -*- coding: utf-8 -*-

# Global packages
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

# My packages
from databases.repositories.settingsRepository import SettingsRepository
from databases.repositories.matchsRepository import MatchsRepository
from databases.base import engine, session
from constants import constants
import functions as F

# Dotenv
load_dotenv()
settingsRepository = SettingsRepository(engine)
matchsRepository = MatchsRepository(engine)

async def deleteCalendar(ctx):
    await ctx.send(constants.DELETE_CALENDAR)
    service = getService()
    events = service.events().list(calendarId=getCalendarId(), singleEvents=True, orderBy='startTime').execute().get('items', [])
    for event in events: service.events().delete(calendarId=getCalendarId(), eventId=event['id']).execute()
    matchsRepository.removeCalId(session)
    await ctx.send(constants.CALENDAR_DELETED)

async def updateCalendar(ctx):
    if settingsRepository.getCalendarStatus(session) == 1:
        await ctx.send(constants.CALENDAR_ALREADY_RUNNING)
        return
    await ctx.send(constants.UPDATE_CALENDAR)
    settingsRepository.setCalendarStatus(session, 1)
    eventsInDB = matchsRepository.getMatchs(session)
    for eventInDB in eventsInDB: updateSingleEvent(eventInDB)
    settingsRepository.setCalendarStatus(session, 0)
    await ctx.send(constants.CALENDAR_UPDATED)

def getEvent(eventId):
    event = getService().events().get(calendarId=getCalendarId(), eventId=eventId).execute()
    return event

def compare(eventInDB, eventInCal):
    event = F.generateEvent(eventInDB)
    if event['summary'] != eventInCal['summary'] or event['description'] != eventInCal['description'] or\
       event['colorId'] != eventInCal['colorId'] or event['start']['dateTime'] != eventInCal['start']['dateTime'][0:19] or\
       event['end']['dateTime'] != eventInCal['end']['dateTime'][0:19]: return True
    return False

def deleteEvent(eventId):
    getService().events().delete(calendarId=getCalendarId(), eventId=eventId).execute()

def createEvent(event):
    return getService().events().insert(calendarId=getCalendarId(), body=F.generateEvent(event), sendNotifications=True).execute()["id"]

def updateSingleEvent(eventInDB):
    id = eventInDB.id
    idCal = eventInDB.calId
    if idCal != None:
        eventInCal = getEvent(idCal)
        diff = compare(eventInDB, eventInCal)
        if diff:
            try:
                deleteEvent(idCal)
                idCal = createEvent(eventInDB)
                matchsRepository.updateEvent(session, id, idCal)
            except Exception as e :
                print("Erreur lors de la modification d'un évenement sur le calendrier : ")
                print(e)
    else:
        try:
            idCal = createEvent(eventInDB)
            matchsRepository.updateEvent(session, id, idCal)
        except Exception as e:
            print("Erreur lors de la création d'un évenement sur le calendrier : ")
            print(e)

def updateOneEvent(id):
    eventInDB = matchsRepository.getMatchInfosById(session, id)
    if (settingsRepository.getCalendarStatus(session) == 1) : return
    settingsRepository.setCalendarStatus(session, 1)
    updateSingleEvent(eventInDB)
    settingsRepository.setCalendarStatus(session, 0)

def launch_update():
    if settingsRepository.setCalendarStatus(session, 0):
        update()

def getService():
    return build('calendar', 'v3', credentials=F.findCreds())

def getCalendarId():
    return os.environ.get("CalendarId")
