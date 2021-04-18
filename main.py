import asyncio
import psycopg2
import discord
import random
import os
from objects import *
from GameManager import *
from discord.ext import commands

KEY = os.environ.get('KEY')

#INTENTS
intents = discord.Intents.default()
#intents.members = True
intents.typing = False

def get_prefix(client, message):
    try:
        guildID = message.guild.id
        sql_query = '''SELECT * FROM prefixes
                        WHERE id = (%s)'''
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

client.run(KEY)
