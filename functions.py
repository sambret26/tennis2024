# -*- coding: utf-8 -*-

# Global packages
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component
from google_auth_oauthlib.flow import InstalledAppFlow as IAF
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from discord_slash import ButtonStyle
from datetime import datetime as date
from datetime import timedelta
from dotenv import load_dotenv
import os.path as path
import subprocess
import discord
import pickle
import json
import os

# My packages
from databases.repositories.messagesRepository import MessagesRepository
from databases.repositories.channelsRepository import ChannelsRepository
from databases.repositories.playersRepository import PlayersRepository
from databases.repositories.matchsRepository import MatchsRepository
from databases.repositories.courtsRepository import CourtsRepository
from databases.repositories.teamsRepository import TeamsRepository
from databases.base import engine, session
from constants import constants
import update

# Dotenv
load_dotenv()

messagesRepository = MessagesRepository(engine)
channelsRepository = ChannelsRepository(engine)
playersRepository = PlayersRepository(engine)
matchsRepository = MatchsRepository(engine)
courtsRepository = CourtsRepository(engine)
teamsRepository = TeamsRepository(engine)

def generateMatchMessage(match):
    player1 = getPlayerFromPlayerIdInDB(match.category, match.player1Id)
    player2 = getPlayerFromPlayerIdInDB(match.category, match.player2Id)
    if match.finish:
        msg = f"Le match {match.name} à opposé {player1} à {player2}"
        if match.day != None: msg += f" le {match.day}"
        if match.hour != None: msg += f" à {match.hour}"
        if match.courtId != None:
            courtName = courtsRepository.getCourtNameById(session, match.courtId)
            msg += f" sur le court {courtName}"
        msg += "."
        if match.winnerId != None and match.winnerId != 0:
            winner = player2
            if int(match.winnerId) == int(match.player1Id): winner = player1
            msg += " Il a été gagné par {}".format(winner.split("(")[0])
            if match.score != None: msg += f" ({match.score})"
            msg += "."
    else:
        if player1 == None and player2 == None and match.day == None and match.courtId == None: return (constants.NO_MATCH_INFO.replace("MATCH_NAME", match.name))
        if player1 != None and player2 != None : msg = f"Le match {match.name} opposera {player1} à {player2}"
        elif player1 != None: msg = f"Le match {match.name} opposera {player1} à ?"
        elif player2 != None: msg = f"Le match {match.name} opposera {player2} à ?"
        else: msg = f"Le match {match.name} se jouera"
        if match.day != None: msg += f" le {match.day}"
        if match.hour != None: msg += f" à {match.hour}"
        if match.courtId != None:
            courtName = courtsRepository.getCourtNameById(session, match.courtId)
            msg += f" sur le court {courtName}"
        msg += "."
    return msg

def getPlayerFromPlayerIdInDB(cat, playerIdDB):
    if playerIdDB == None or playerIdDB == "null": return None
    if playerIdDB.startswith("VS") or playerIdDB.startswith("VD") or playerIdDB.startswith("VP"):
        match = playerIdDB.lstrip("V")
        return constants.MATCH_WINNER.replace("MATCH_NAME", match)
    if playerIdDB.startswith("VT") or playerIdDB.startswith("QE"):
        return constants.INCOMING_QUALIFIED
    player = playersRepository.getPlayerNameById(session, playerIdDB)
    if player == None: return None
    if cat.startswith("S"):
        p1 = playersRepository.getPlayerInfosById(session, playerIdDB)
        return f"{p1[1]} {p1[0]} ({p1[2]})"
    team = teamsRepository.getTeamInfosById(session, playerIdDB)
    if team:
        player1 = playersRepository.getPlayerNameById(session, team.player1Id)
        player2 = playersRepository.getPlayerNameById(session, team.player2Id)
        if player1 and player2: return f"{player1.lastName} et {player2.lastName} ({team.ranking})"
    return None

def numberPlayersByCategory(category):
    nb = playersRepository.getNumberPlayersByCategory(session, category)
    return ("Il y a {} inscrit{} dans la catégorie {}".format(nb, '' if nb < 2 else 's', category))

async def yesOrNo(bot, ctx, message):
    return await question(bot, ctx, message, constants.YES_OR_NO)

async def question(bot, ctx, message, list):
    while len(list) > 0:
        questionList = list[:4]
        if len(questionList) == 4:
            questionList.append(constants.QUESTION_MORE)
        result = await question5max(bot, ctx, message, questionList)
        if result != "Next" : return result
        list = list[4:]

async def question5max(bot, ctx, message, list):

    def check(m): return m.author.id == ctx.author.id and m.origin_message.id == choice.id

    buttons = generateButtons(list)
    actionRow = create_actionrow(*buttons)
    choice = await ctx.send(message, components=[actionRow])
    buttonCtx = await wait_for_component(bot, components=actionRow, check=check)
    await buttonCtx.edit_origin(content=f"{message} ({buttonCtx.custom_id})")
    if buttonCtx.custom_id.isdigit(): return int(buttonCtx.custom_id)
    return buttonCtx.custom_id

def generateButtons(list):
    buttons=[]
    for (index, value) in enumerate(list):
        buttons.append(create_button(style=findStyle(index, value[2] if len(value) > 2 else None), label=value[0], custom_id=value[1]))
    return buttons

def findStyle(index, value):
    if value != None and value.lower() == constants.GREEN: return ButtonStyle.green
    if value != None and value.lower() == constants.RED: return ButtonStyle.red
    if value != None and value.lower() == constants.BLUE: return ButtonStyle.blue
    if index % 3 == 0: return ButtonStyle.green
    if index % 3 == 1: return ButtonStyle.red
    return ButtonStyle.blue

async def sendAllDetails(ctx):
    embed = discord.Embed(title=constants.NB_INSCRITS_BY_CAT, color=constants.EMBED_COLOR)
    rankings = playersRepository.getRankings(session)
    embed.add_field(name = constants.TOTAL, value=rankingMessage(rankings), inline=False)
    for category in constants.CATEGORIES:
        rankingByCategory = playersRepository.getRankingsByCategory(session, category)
        embed.add_field(name=category, value=rankingMessage(rankingByCategory), inline=False)
    await ctx.send(embed=embed)

async def sendCategoryDetails(ctx, category):
    embed = discord.Embed(title=constants.NB_INSCIRTS, color=constants.EMBED_COLOR)
    rankingByCategory = playersRepository.getRankingsByCategory(session, category)
    embed.add_field(name=category, value=rankingMessage(rankingByCategory), inline=False)
    await ctx.send(embed=embed)

def rankingMessage(rankings):
    message = "\u200B"
    for ranking in constants.RANKINGS:
        message += f"\t{ranking.ljust(4)} : {rankings.count(ranking)}\n"
    return message

async def addNotifMatch():
    currentDate = getCurrentDate().strftime("%d/%m")
    currentHour = int(getCurrentDate().strftime("%H"))
    currentMinutes = int(getCurrentDate().strftime("%M"))
    matchs = matchsRepository.getMatchsToPlay(session, currentDate)
    for match in matchs:
        matchHour = int(match[4][0:2])
        matchMinutes = int(match[4][3:])
        if ((60*matchHour + matchMinutes)) - (60*currentHour + currentMinutes) <= 16:
            player1 = getPlayerFromPlayerIdInDB(match[1], match[2])
            player2 = getPlayerFromPlayerIdInDB(match[1], match[3])
            matchsRepository.setNotifToSend(session, match[0])
            courtName = courtsRepository.getCourtNameById(match[5])
            message = f"Match {match[1]} : {player1} contre {player2} prévu à {match[4]} sur le court n°{courtName}"
            messagesRepository.addMessage(session, 'NOTIF', message)

# Returns the current date, with an offset if necessary (c.f. jetlag)
def getCurrentDate():
    offset = 0
    return date.now() + timedelta(seconds=3600 * offset)

def backup():
    subprocess.run(constants.BACKUP_CMD, shell=True, capture_output=True, text=True)

async def setResult(bot, ctx, id, name, player1Id, player2Id, winner):
    if winner:
        if player1Id == None or player1Id.startswith("V"): player1 = constants.UNKNOWN_PLAYER
        else:
            p1 = playersRepository.getPlayerInfosById(session, player1Id)
            player1 = f"{p1[1]} {p1[0]}"
        if player2Id == None or player2Id.startswith("V"): player2 = constants.UNKNOWN_PLAYER
        else:
            p2 = playersRepository.getPlayerInfosById(session, player2Id)
            player2 = f"{p2[1]} {p2[0]}"
        winner = await question(bot, ctx, constants.WHICH_PLAYER_WON, [(player1, player1Id, constants.GREEN), (player2, player2Id, constants.BLUE)])
        update.setWinner(id, winner)
        matchsRepository.updatePlayerId(session, "V"+name, winner) #TODO?
    set1 = await askSetResult(bot, ctx, constants.SET_1_RESULT)
    set2 = await askSetResult(bot, ctx, constants.SET_2_RESULT)
    res = set1 + " " + set2
    if thirdSet(set1, set2):
        set3 = await askSetResult(bot, ctx, constants.SET_3_RESULT, False)
        res += " " + set3
    update.setScore(id, res)
    await ctx.send(constants.RESULT_UPDATE.replace("MATCH_NAME",name))

async def askSetResult(bot, ctx, message, canLose=True):
    list = []
    win = constants.WIN
    for score in win : list.append((score, score, constants.GREEN))
    if canLose:
        lose = constants.LOSE
        for score in lose : list.append((score, score, constants.RED))
    return await question(bot, ctx, message, list)

def thirdSet(set1, set2):
    win = 0
    for set in [set1, set2]:
        score1, score2 = set.split("/")
        if score1 > score2 : win = win + 1
    return win < 2

async def sendMessages(bot):
    for category in constants.CHANNEL_CATEGORIES:
        await sendMessagesByCategory(bot, category)

async def sendMessagesByCategory(bot, category):
    messages = messagesRepository.getMessages(session, category)
    channelId = channelsRepository.getLogChannelId(session, category)
    channel = await bot.fetch_channel(channelId)
    for message in messages :
        await channel.send(message[1])
        messagesRepository.deleteMessageById(session, message[0])

def notADay(day):
    if len(day) != 5 or day[2] != "/": return True
    if day[0] != "0" and day[0] != "1" and day[0] != "2" and day[0] != "3": return True
    if not day[1].isdigit() or not day[3].isdigit() or not day[4].isdigit(): return True
    return False

def notInTournament(day):
    if day.split("/")[1] != "06" : return True
    if int(day.split("/")[0]) > 14 and int(day.split("/")[0]) < 32: return False
    return True

def convertInHour(hour):
    if len(hour) == 2:
        if hour[0].isdigit() and hour[1].upper() == "H": return hour.upper()
        return None
    if len(hour) == 3:
        if hour[0] == "0" and hour[1].isdigit() and hour[2].upper() == "H": return hour[1:].upper()
        if hour[0] == "1" and hour[1].isdigit() and hour[2].upper() == "H": return hour.upper()
        if hour[0] == "2" and hour[1] in ["0", "1", "2", "3"] and hour[2].upper() == "H": return hour.upper()
        return None
    if len(hour) == 4:
        if hour[0].isdigit() and hour[1].upper() == "H" and hour[2] == "0" and hour[3] == "0": return hour[:2].upper()
        if hour[0].isdigit() and hour[1].upper() == "H" and hour[2] in ["0", "1", "2", "3", "4", "5"] and hour[3].isdigit(): return hour.upper()
        return None
    if len(hour) == 5:
        if hour[0] == "0" and hour[1].isdigit() and hour[2].upper() == "H" and hour[3] == "0" and hour[4] == "0": return hour[1:3].upper()
        if hour[0] == "0" and hour[1].isdigit() and hour[2].upper() == "H" and hour[3] in ["0", "1", "2", "3", "4", "5"] and hour[4].isdigit(): return hour[:3].upper()
        if hour[0] == "1" and hour[1].isdigit() and hour[2].upper() == "H" and hour[3] == "0" and hour[4] == "0": return hour[:3].upper()
        if hour[0] == "1" and hour[1].isdigit() and hour[2].upper() == "H" and hour[3] in ["0", "1", "2", "3", "4", "5"] and hour[4].isdigit(): return hour.upper()
        if hour[0] == "2" and hour[1] in ["0", "1", "2", "3"] and hour[2].upper() == "H" and hour[3] == "0" and hour[4] == "0": return hour[:3].upper()
        if hour[0] == "2" and hour[1] in ["0", "1", "2", "3"] and hour[2].upper() == "H" and hour[3] in ["0", "1", "2", "3", "4", "5"] and hour[4].isdigit(): return hour.upper()
    return None

def getDatesFromArgs(args):
    dates = []
    for arg in args:
        if not notADay(arg) and not notInTournament(arg): dates.append(arg)
    if len(dates) == 0: return [getCurrentDate().strftime("%d/%m")]
    return dates

def generateEvent(match):
    player1 = getPlayerFromPlayerIdInDB(match.category, match.player1Id)
    player2 = getPlayerFromPlayerIdInDB(match.category, match.player2Id)
    courtName = courtsRepository.getCourtNameById(session, match.courtId)
    timezone = "Europe/Paris"
    newEvent = {
        "summary": match.name,
        "description": f"{player1} contre {player2} sur le terrain n°{courtName}",
        "colorId": getColor(match.category),
        "start": {"dateTime": getStart(match.day, match.hour), "timeZone" : timezone},
        "end": {"dateTime": getEnd(match.day, match.hour), "timeZone" : timezone},
    }
    return newEvent

def getColor(category):
    if category == "SM": return 9
    if category == "SD": return 3
    if category == "DM": return 10
    if category == "DD": return 11
    if category == "DX": return 5
    return 8

def getStart(day, hour):
    d, m = day.split("/")
    h, min = hour.lower().split("h")
    if min == '' : min = "00"
    if d == "15" : d, h = startOneDayBefore(d, h)
    if len(h) == 1 : h = "0" + h
    return "2024-{}-{}T{}:{}:00".format(m, d, h, min)

def startOneDayBefore(day, hour):
    day = "16"
    hour = str(int(hour) - 10)
    return day, hour

def getEnd(day, hour):
    d, m = day.split("/")
    h, min = hour.lower().split("h")
    if min == '' : min = "00"
    h = int(h) + 1
    min = int(min) + 30
    if min > 59:
      h = h + 1
      min = min - 60
    h = str(h)
    min = str(min)
    if len(h) == 1 : h = "0" + h
    if len(min) == 1 : min = "0" + min
    return "2024-{}-{}T{}:{}:00".format(m, d, h, min)

async def saveOldDB(channel):
    currentDate = getCurrentDate().strftime("_%m_%d_%Hh%M")
    filename = constants.BACKUP_DB_FILENAME.replace("DATE", currentDate)
    subprocess.run(constants.SAVE_OLD_DB_CMD.replace("FILENAME", filename), shell=True, capture_output=True, text=True)
    await channel.send(constants.DB_BACKUP.replace("FILENAME", filename))

def getDateFromFileName(f):
    if len(f) == 17 and f[0:3] == "DB_" and f[5] == f[8] == "_" and f[11] == "h" and f[14:] == ".db" and all(f[i].isdigit() for i in [3, 4, 6, 7, 9, 10, 12, 13]): return f"{f[6:8]}/{f[3:5]} à {f[9:14]}"
    if len(f) == 16 and f[0:3] == "DB_" and f[5] == f[8] == "_" and f[10] == "h" and f[13:] == ".db" and all(f[i].isdigit() for i in [3, 4, 6, 7, 9, 11, 12]): return f"{f[6:8]}/{f[3:5]} à {f[9:13]}"
    return f

def load(name):
    with open(name + ".pkl", 'rb') as f:
        return pickle.load(f)

def load_crypted(name):
    with open(name + '.pkl', 'rb') as f:
        crypted = pickle.load(f)
        return decode_credentials(crypted)

def decode_credentials(encrypted_credentials):
    password = os.environ.get('HashPassword')

    decrypted_data = ""
    for i in range(len(encrypted_credentials)):
        d = encrypted_credentials[i]
        p = password[i % len(password)]
        v = chr(ord(d) - ord(p))
        decrypted_data += v

    creds_dict = json.loads(decrypted_data)
    creds = Credentials.from_authorized_user_info(creds_dict)
    obj = {"credentials" : creds, "valid" : creds_dict["valid"], "expired" : creds_dict["expired"]}
    return obj

def code_credentials(credentials):
    password = os.environ.get('HashPassword')
    serialized_credentials = credentials.to_json()
    credentials_dict = json.loads(serialized_credentials)
    credentials_dict["valid"] = credentials.valid
    credentials_dict["expired"] = credentials.expired
    updated_serialized_credentials = json.dumps(credentials_dict)
    encrypted_data = ""
    for i in range(len(updated_serialized_credentials)):
        d = updated_serialized_credentials[i]
        p = password[i % len(password)]
        v = chr(ord(d) + ord(p))
        encrypted_data += v

    return encrypted_data

def findCreds():
    creds = None
    filename = os.environ.get("TokenFilename")
    if path.exists("./" + filename + ".pkl"):
        obj = load_crypted(filename)
        creds = obj["credentials"]
    else :
        print("File not found : " + filename)
        return None
    if not creds or not obj["valid"]:
        creds.refresh(Request())
        crypted_creds = code_credentials(creds)
        with open(filename + ".pkl", 'wb') as token:
            pickle.dump(crypted_creds, token)
    return creds

async def importDB(message):
    await saveOldDB(message.channel)
    file = await message.attachments[0].to_file()
    await message.attachments[0].save('./DB.db')
    await message.channel.send(constants.DB_SAVE.replace("FILENAME", file.filename))

async def loadDB(bot):
    channelId = os.environ.get("DBId")
    channel = await bot.fetch_channel(channelId)
    messages = await channel.history(limit=1).flatten()
    if not messages : return False
    message = messages[0]
    if not message.attachments: return False
    file = await message.attachments[0].to_file()
    if file.filename[-3:] != '.db': return False
    await message.attachments[0].save('./DB.db')
    return True
