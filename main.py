import asyncio
import discord
import random
import os
from objects import *
from discord.ext import commands

#INTENTS
intents = discord.Intents.default()
intents.members = True
intents.typing = False

client = commands.AutoShardedBot(command_prefix = 'am.', intents=intents)
client.remove_command('help')

#LOAD COGS
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

KEY = os.environ.get('KEY')
client.run(KEY)
