# -*- coding: utf-8 -*-

# Global packages
import sys
sys.path.append("modules")

from discord_slash import SlashCommand
from discord.ext import commands
from dotenv import load_dotenv
import schedule
import asyncio
import discord
import fillDB
import os

# My packages
from databases.base import Base, engine, session
from constants import constants
import cal as calendar
import functions as F
import service

# Dotenv
load_dotenv()

# Créer les tables dans la base de données
Base.metadata.create_all(engine)

intent = discord.Intents(messages=True, members=True, guilds=True)
bot = commands.Bot(command_prefix="$", description="Sam's API", intents=intent)
slash = SlashCommand(bot, sync_commands=True)

GUILD_ID = int(os.environ.get("GuildId"))

def isAllowed(ctx):
    return int(ctx.author.id) == int(os.environ.get("SamId"))

# @bot.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(constants.FORBIDDEN)
    elif isinstance(error, commands.CommandNotFound):
        command_name = ctx.message.content.split()[0][1:]
        await ctx.send(constants.UNKNOWN_COMMAND.replace("COMMAND", command_name))
    else :
        await ctx.send(error)

# Commandes
@bot.command()
async def maj(ctx):
    if ctx.message.guild.id != GUILD_ID: return
    await service.maj(bot, ctx)

@bot.command()
async def majJoueurs(ctx):
    if ctx.message.guild.id != GUILD_ID: return
    await service.majPlayers(ctx)

@bot.command()
async def majMatchs(ctx):
    if ctx.message.guild.id != GUILD_ID: return
    await service.majMatchs(ctx)

@bot.command()
async def majCourts(ctx):
    await service.majCourts(ctx)

@bot.command()
async def nb(ctx):
    if ctx.message.guild.id != GUILD_ID: return
    await service.nb(bot, ctx)

@bot.command()
async def info(ctx, name=None):
    if ctx.message.guild.id != GUILD_ID: return
    await service.info(ctx, name)

@bot.command()
async def infos(ctx, name=None):
    await info(ctx, name)

@bot.command()
async def result(ctx, name=None):
    if ctx.message.guild.id != GUILD_ID: return
    await service.result(bot, ctx, name)

@bot.command()
async def resultat(ctx, name=None):
    await result(ctx, name)

@bot.command()
async def modifCourt(ctx, name=None):
    if ctx.message.guild.id != GUILD_ID: return
    await service.modifCourt(bot, ctx, name)

@bot.command()
async def mc(ctx, name=None):
    await modifCourt(ctx, name)

@bot.command()
async def modifJoueur1(ctx, *args):
    if ctx.message.guild.id != GUILD_ID: return
    await service.modifJoueur(ctx, args, 1)

@bot.command()
async def mj1(ctx, *args):
    await modifJoueur1(ctx, *args)

@bot.command()
async def modifJoueur2(ctx, *args):
    if ctx.message.guild.id != GUILD_ID: return
    await service.modifJoueur(ctx, args, 2)

@bot.command()
async def mj2(ctx, *args):
    await modifJoueur2(ctx, *args)

@bot.command()
async def modifJour(ctx, *args):
    if ctx.message.guild.id != GUILD_ID: return
    await service.modifJour(ctx, args)

@bot.command()
async def mj(ctx, *args):
    await modifJour(ctx, *args)

@bot.command()
async def modifHeure(ctx, *args):
    if ctx.message.guild.id != GUILD_ID: return
    await service.modifHeure(ctx, args)

@bot.command()
async def mh(ctx, *args):
    await modifHeure(ctx, *args)

@bot.command()
async def modifPg(ctx, *args):
    if ctx.message.guild.id != GUILD_ID: return
    await service.modifPg(ctx, args)

@bot.command()
async def mpg(ctx, *args):
    await modifPg(ctx, *args)

@bot.command()
async def pg(ctx, *args):
    if ctx.message.guild.id != GUILD_ID: return
    await service.pg(ctx, args)

@bot.command()
async def programmation(ctx, *args):
    await pg(ctx, *args)

@bot.command()
async def program(ctx, *args):
    await pg(ctx, *args)

@bot.command()
async def pgw(ctx):
    await service.pgWhatsapp(bot)

@bot.command()
async def revert(ctx):
    if ctx.message.guild.id != GUILD_ID: return
    await service.revert(ctx)
    reload_DB()

@bot.command()
async def export(ctx):
    if ctx.message.guild.id != GUILD_ID: return
    await service.export(bot, ctx)

@bot.command()
async def db(ctx):
    if ctx.message.guild.id != GUILD_ID: return
    await service.db(ctx)

@bot.command()
async def excel(ctx):
    if ctx.message.guild.id != GUILD_ID: return
    await service.excel(ctx)

@bot.command()
async def restore(ctx):
    if ctx.message.guild.id != GUILD_ID: return
    await service.restore(bot, ctx)
    reload_DB()

@bot.command()
async def updateCalendar(ctx):
    if ctx.message.guild.id != GUILD_ID: return
    await service.updateCalendar(ctx)

@bot.command()
async def updateCal(ctx):
    await updateCalendar(ctx)

@bot.command()
async def uc(ctx):
    await updateCalendar(ctx)

@bot.command()
async def deleteCalendar(ctx):
    if ctx.message.guild.id != GUILD_ID: return
    await service.deleteCalendar(ctx)

@bot.command()
async def deleteCal(ctx):
    await deleteCalendar(ctx)

@bot.command()
async def dc(ctx):
    await deleteCalendar(ctx)

@bot.command()
@commands.check(isAllowed)
async def moja(ctx):
    await service.moja(bot, ctx)

@bot.command()
@commands.check(isAllowed)
async def cal(ctx):
    await service.cal(bot, ctx)

@bot.command()
@commands.check(isAllowed)
async def unsetcal(ctx):
    await service.unsetcal(ctx)

@bot.command()
@commands.check(isAllowed)
async def fill(ctx):
    await service.fill(ctx)

@bot.command()
async def cmd(ctx):
    if ctx.message.guild.id != GUILD_ID: return
    await service.cmd(ctx)

@bot.command()
async def command(ctx):
    await cmd(ctx)

@bot.command()
async def commandes(ctx):
    await cmd(ctx)

@bot.command()
@commands.check(isAllowed)
async def clear(ctx, nombre: int = 100):
    await service.clear(ctx, nombre)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if message.attachments:
        await service.importFile(message)
        reload_DB()
    await bot.process_commands(message)

def reload_DB():
    from databases.base import session

# Recuring Tasks
async def recurring_task():
    await bot.wait_until_ready()
    if os.environ.get("Prod") == "true" : fillDB.fill()
    while not bot.is_closed():
        schedule.run_pending()
        await asyncio.sleep(1)

def main():
    schedule.every().minute.at(":00").do(lambda: asyncio.create_task(F.sendMessages(bot)))
    schedule.every().minute.at(":30").do(lambda: asyncio.create_task(service.updatePlayersAndSendNotif()))
    schedule.every().day.at("06:58").do(lambda: asyncio.create_task(service.pgWhatsapp(bot)))
    schedule.every().day.at("04:00").do(lambda: asyncio.create_task(calendar.main()))
    bot.loop.create_task(recurring_task())
    bot.run(os.environ.get("DiscordToken"))

main()
