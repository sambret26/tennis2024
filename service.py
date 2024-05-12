# -*- coding: utf-8 -*-

# Global packages
import subprocess
import discord
import os

# My packages
from databases.repositories.channelsRepository import ChannelsRepository
from databases.repositories.settingsRepository import SettingsRepository
from databases.repositories.playersRepository import PlayersRepository
from databases.repositories.matchsRepository import MatchsRepository
from databases.repositories.courtsRepository import CourtsRepository
from databases.base import engine, session
from constants import constants
import fillDB
import cal as calendar
import functions as F
import moja as FFT
import exportExcel
import importExcel
import update

channelsRepository = ChannelsRepository(engine)
settingsRepository = SettingsRepository(engine)
playersRepository = PlayersRepository(engine)
matchsRepository = MatchsRepository(engine)
courtsRepository = CourtsRepository(engine)

async def maj(bot, ctx):
    number = await F.question(bot, ctx, constants.WHICH_UPDATE, constants.WHICH_UPDATE_LIST)
    if number == 1: await majPlayers(ctx)
    if number == 2: await majMatchs(ctx)
    if number == 3: await majCourts(ctx)

async def majPlayers(ctx):
    FFT.updatePlayers()
    await ctx.send(constants.UPDATE_PLAYERS_OK)

async def majMatchs(ctx):
    FFT.updateMatchs()
    await ctx.send(constants.UPDATE_MATCHS_OK)

async def majCourts(ctx):
    FFT.updateCourts()
    await ctx.send(constants.UPDATE_COURTS_OK)

async def nb(bot, ctx):
    category = channelsRepository.getChannelCategory(session, ctx.channel.id)
    if category is None or category == "G":
        nb = playersRepository.getNumberPlayers(session)
        message = "Il y a {} inscrit{} dans le tournoi".format(nb, '' if nb <2 else 's')
        for cat in constants.CATEGORIES : message += f"\n\t\t{F.numberPlayersByCategory(cat)}"
        await ctx.send(message)
    else:
        await ctx.send(F.numberPlayersByCategory(category))
    details = await F.yesOrNo(bot, ctx, constants.ASK_FOR_DETAILS)
    if details:
        if (category is None or category == "G"): await F.sendAllDetails(ctx)
        else : await F.sendCategoryDetails(ctx, category)

async def info(ctx, name):
    if name == None:
        await ctx.send(constants.INFO_UNVALID_PARAMETERS)
        return
    name = name.upper()
    matchInfos = matchsRepository.getAllMatchInfosByName(session, name)
    if matchInfos == None:
        await ctx.send(constants.NO_MATCH.replace("MATCH_NAME", name))
        return
    message = F.generateMatchMessage(matchInfos)
    await ctx.send(message)

async def result(bot, ctx, name):
    if name == None:
        await ctx.send(constants.RESULT_UNVALID_PARAMETERS)
        return
    name = name.upper()
    match = matchsRepository.getAllMatchInfosByName(session, name)
    if match == None:
        await ctx.send(constants.NO_MATCH.replace("MATCH_NAME", name))
        return
    F.backup()
    if match.winnerId != None and match.winnerId != 0 and match.score != None:
        res = await F.yesOrNo(bot, ctx, constants.WINNER_AND_SCORE_ALREADY_EXISTS)
        if res : await F.setResult(bot, ctx, match.id, match.name, match.player1Id, match.player2Id, True)
    elif match.winnerId != None and match.winnerId != 0:
        res = await F.yesOrNo(bot, ctx, constants.WINNER_ALREADY_EXISTS)
        if not res : await F.setResult(bot, ctx, match.id, match.name, match.player1Id, match.player2Id, False)
        else : await F.setResult(bot, ctx, match.id, match.name, match.player1Id, match.player2Id, True)
    else: await F.setResult(bot, ctx, match.id, match.name, match.player1Id, match.player2Id, True)

async def modifCourt(bot, ctx, name):
    if name == None:
        await ctx.send(constants.MODIF_COURT_UNVALID_PARAMETERS)
        return
    matchName = name.upper()
    matchId = matchsRepository.getMatchIdByName(session, matchName)
    if matchId == None:
        await ctx.send(constants.NO_MATCH.replace("MATCH_NAME", matchName))
        return
    F.backup()
    list = [("Numéro 1", "1", "green"), ("Numéro 2", "2", "blue"), ("Numéro 3", "3", "red")]
    courtNumber = await F.question(bot, ctx, constants.WHICH_COURT, list)
    courtId = courtsRepository.getCourtIdByName(session, courtNumber)
    update.setCourt(matchId, courtId)
    await ctx.send(constants.COURT_UPDATE.replace("MATCH_NAME", matchName).replace("COURT", str(courtNumber)))

async def modifJoueur(ctx, args, number):
    if len(args) < 3:
        await ctx.send(constants.UPDATE_PLAYERS_UNVALID_PARAMETERS)
        return
    matchName = args[0].upper()
    matchId = matchsRepository.getMatchIdByName(session, matchName)
    if matchId == None:
        await ctx.send(constants.NO_MATCH.replace("MATCH_NAME", matchName))
        return
    playerLastname = " ".join(args[1:-1]).upper()
    playerFirstname = args[-1].title()
    playerId = playersRepository.getPlayerIdByName(session, playerLastname, playerFirstname)
    if playerId == None:
        await ctx.send(constants.PLAYER_NOT_FOUND + f"{playerLastname} {playerFirstname}")
        return
    F.backup()
    if number == 1 :
        update.setPlayer1(matchId, playerId)
        message = f"Le match {matchName} à maintenant comme joueur 1 {playerLastname} {playerFirstname}"
    else:
        update.setPlayer2(matchId, playerId)
        message = f"Le match {matchName} à maintenant comme joueur 2 {playerLastname} {playerFirstname}"
    await ctx.send(message)

async def modifJour(ctx, args):
    if len(args) != 2:
        await ctx.send(constants.UPDATE_DAY_UNVALID_PARAMETERS)
        return
    matchName = args[0].upper()
    matchId = matchsRepository.getMatchIdByName(session, matchName)
    if matchId == None:
        await ctx.send(constants.NO_MATCH.replace("MATCH_NAME", matchName))
        return
    day = args[1]
    if len(day) == 4: day = "0" + day
    if F.notADay(day):
        await ctx.send(constants.UNVALID_DAY)
        return
    if F.notInTournament(day):
        await ctx.send(constants.DAY_NOT_IN_TOURNAMENT.replace("DAY", day))
        return
    F.backup()
    update.setDay(matchId, day)
    message = f"Le match {matchName} est programmé pour le {day}"
    await ctx.send(message)

async def modifHeure(ctx, args):
    if len(args) != 2:
        await ctx.send(constants.UPDATE_HOUR_UNVALID_PARAMETERS)
        return
    matchName = args[0].upper()
    matchId = matchsRepository.getMatchIdByName(session, matchName)
    if matchId == None:
        await ctx.send(constants.NO_MATCH.replace("MATCH_NAME", matchName))
        return
    hour = F.convertInHour(args[1])
    if hour == None:
        await ctx.send(constants.UNVALID_HOUR)
        return
    F.backup()
    update.setHour(matchId, hour)
    message = f"Le match {matchName} est programmé à {hour}"
    await ctx.send(message)

async def modifPg(ctx, args):
    if len(args) != 3:
        await ctx.send(constants.UPDATE_PG_UNVALID_PARAMETERS)
        return
    matchName = args[0].upper()
    matchId = matchsRepository.getMatchIdByName(session, matchName)
    if matchId == None:
        await ctx.send(constants.NO_MATCH.replace("MATCH_NAME", matchName))
        return
    day = args[1]
    if len(day) == 4: day = "0" + day
    if F.notADay(day):
        await ctx.send(constants.UNVALID_DAY)
        return
    if F.notInTournament(day):
        await ctx.send(constants.DAY_NOT_IN_TOURNAMENT.replace("DAY", day))
        return
    hour = F.convertInHour(args[2])
    if hour == None:
        await ctx.send(constants.UNVALID_HOUR)
        return
    F.backup()
    update.setPg(matchId, day, hour)
    message = f"Le match {matchName} est programmé pour le {day} à {hour}"
    await ctx.send(message)

async def pg(ctx, args):

    def sort_key(match):
        time = match[3].lower()
        if time.endswith('h'): time = time[:-1].zfill(2) + '00'
        else: time = time.replace('h', '').zfill(4)
        return int(time)

    dates = F.getDatesFromArgs(args)
    message = ""
    matchs = False
    for date in dates:
        matchs = matchsRepository.getMatchsByDate(session, date)
        if matchs == None: break
        message += constants.PG.replace("DATE", date)
        matchs = sorted(matchs, key=sort_key)
        for match in matchs:
            courtName = courtsRepository.getCourtNameById(session, match[4])
            player1 = F.getPlayerFromPlayerIdInDB(match[0], match[1])
            player2 = F.getPlayerFromPlayerIdInDB(match[0], match[2])
            message += f"{match[3]} : {match[0]}, {player1} contre {player2} sur le court n°{courtName}\n"
            matchs = True
        message += "\n"
    if not matchs : message = constants.NO_PG.replace("DATE", dates[0])
    await ctx.send(message)

async def pgWhatsapp(bot):

    def sort_key(match):
        time = match[3].lower()
        if time.endswith('h'): time = time[:-1].zfill(2) + '00'
        else: time = time.replace('h', '').zfill(4)
        return int(time)

    channelId = channelsRepository.getLogChannelId(session, "WA")
    channel = await bot.fetch_channel(channelId)
    matchs = False
    date = F.getCurrentDate().strftime("%d/%m")
    matchs = matchsRepository.getMatchsByDate(session, date)
    if matchs == None or matchs == []:
        await channel.send(constants.NO_PG.replace("DATE", date))
        return
    message += constants.PG.replace("DATE", date)
    matchs = sorted(matchs, key=sort_key)
    for match in matchs:
        player1 = F.getPlayerFromPlayerIdInDB(match[0], match[1])
        player2 = F.getPlayerFromPlayerIdInDB(match[0], match[2])
        message += f"{match[3]} : {player1} contre {player2}\n"
    await channel.send(message)

async def revert(ctx):
    subprocess.run(constants.REVERT_CMD, shell=True, capture_output=True, text=True)
    await ctx.send(constants.REVERT)

async def moja(bot, ctx):
    number = await F.question(bot, ctx, constants.HOW_MOJA_SYNC, constants.SYNC_LIST)
    settingsRepository.setMojaActive(session, number)
    if number == 0:
        await ctx.send(constants.MOJA_UNSYNC)
    else :
        await ctx.send(constants.MOJA_SYNC)

async def cal(bot, ctx):
    number = await F.question(bot, ctx, constants.HOW_CAL_SYNC, constants.SYNC_LIST)
    settingsRepository.setCalendarActive(session, number)
    if number == 0:
        await ctx.send(constants.CAL_UNSYNC)
    else :
        await ctx.send(constants.CAL_SYNC)

async def unsetcal(ctx):
    settingsRepository.setCalendarStatus(session, 0)
    await ctx.send(constants.CAL_UNSET)

async def fill(ctx):
    fillDB.fill()
    await ctx.send(constants.DB_FILLED)

async def cmd(ctx):
    await ctx.send(constants.COMMAND_LIST)
    await ctx.send(constants.COMMAND_LIST_2)

async def clear(ctx, nombre):
    await ctx.channel.purge(limit=nombre+1, check=lambda msg: not msg.pinned)

async def export(bot, ctx):
    number = await F.question(bot, ctx, constants.WHICH_EXPORT, constants.WHICH_EXPORT_LIST)
    if number == "1": await excel(ctx)
    if number == "2": await db(ctx)

async def db(ctx):
    await ctx.send(file=discord.File(fp=constants.DB_FILENAME, filename = constants.DB_FILENAME))

async def excel(ctx):
    await ctx.send(file=discord.File(fp=exportExcel.initiateExcel(), filename = constants.EXCEL_FILENAME))

async def restore(bot, ctx):
    if not os.path.exists(constants.BACKUP_DB_PATHNAME):
        await ctx.send(constants.NO_BACKUP_FILES)
        return
    files = sorted(os.listdir(constants.BACKUP_DB_PATHNAME), reverse = True)
    if not files :
        await ctx.send(constants.NO_BACKUP_FILES)
        return
    list = []
    for file in files :
        list.append((F.getDateFromFileName(file), file))
    fileName = await F.question(bot, ctx, constants.WHICH_FILE, list)
    pathName = constants.BACKUP_DB_PATHNAME + fileName
    await F.saveOldDB(ctx)
    subprocess.run(constants.RESTORE_CMD.replace("FILENAME", pathName), shell=True, capture_output=True, text=True)
    await ctx.send(constants.BDD_RESTAURED.replace("FILENAME", fileName))

async def importFile(message):
    file = await message.attachments[0].to_file()
    if file.filename[-3:] == '.db': await F.importDB(message)
    elif file.filename[-5:] == '.xlsx':
        await importExcel.readExcel(message)
    else: await message.channel.send(constants.EXTENSION_NOT_FOUND)

async def deleteCalendar(ctx):
    await calendar.deleteCalendar(ctx)

async def updateCalendar(ctx):
    await calendar.updateCalendar(ctx)

async def updatePlayersAndSendNotif():
    FFT.updatePlayers()
    await F.addNotifMatch()
