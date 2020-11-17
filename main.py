import asyncio
import psycopg2
import discord
import random
import os
from objects import *
from discord.ext import commands

KEY = os.environ.get('KEY')
DATABASE_URL = os.environ.get('DATABASE_URL')

#INTENTS
intents = discord.Intents.default()
#intents.members = True
intents.typing = False

#LOAD DATABASE
try:
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    c = conn.cursor()
except:
    print("Failed to connect to database")

def get_prefix(client, message):
    try:
        guildID = message.guild.id
        sql_query = '''SELECT * FROM prefixes WHERE id = (%s)'''
        c.execute(sql_query, (guildID,))
        prefix = c.fetchone()

        if prefix is None:
            return 'am.'
        else:
            return prefix[1]
    except:
        return 'am.'

client = commands.AutoShardedBot(command_prefix = get_prefix, intents=intents, chunk_guilds_at_startup=False)
client.remove_command('help')

#LOAD COGS
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

#PREFIX COMMANDS
@client.command()
async def prefix(ctx, prefix):

    userPrefix = str(prefix)

    try:
        guildID = ctx.message.guild.id
    except AttributeError:
        await ctx.send("Changing prefix is only possible in servers!")
        return

    sql_query = '''SELECT FROM prefixes WHERE id = (%s)'''
    c.execute(sql_query, (guildID,))
    prefix = c.fetchone()

    #Check if prefix exists
    if prefix is not None:
        #Delete prior prefix
        sql_execute = '''DELETE FROM prefixes WHERE id = (%s)'''
        c.execute(sql_execute, (guildID,))

    #Add prefix to list
    sql_execute = '''INSERT INTO prefixes (id, prefix) VALUES (%s, %s)'''
    c.execute(sql_execute, (guildID, userPrefix))
    await ctx.send("Successfully changed prefix to " + userPrefix)

    conn.commit()

@client.event
async def on_guild_remove(guild):
    guildID = guild.id
    sql_execute = '''DELETE FROM prefixes WHERE id = (%s)'''
    c.execute(sql_execute, (guildID,))

    conn.commit()

client.run(KEY)
