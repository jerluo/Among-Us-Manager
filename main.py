import asyncio
import discord
import random
import os
from objects import *
from discord.ext import commands


client = commands.Bot(command_prefix = 'am.')
client.remove_command('help')

KEY = os.environ.get('KEY')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

@client.command()
async def help(ctx):
    embed = discord.Embed(
        colour = discord.Colour.orange(),
        description = "Among Us bot to manage muting (and deafening) during a game."
    )

    embed.set_author(name = '[Among Us Manager] Commands:')

    #Starting commands
    embed.add_field(name='Getting started:',value='''`am.start` - host new game in current voice channel. Only one game is allowed in each voice channel.
                                                  \n`am.join` - joins existing game in voice channel.
                                                  \n`am.joinall` - joins everyone in the voice channel into the game.
                                                  \n`am.endgame` - terminates existing game in voice channel. Only players in the game are able to use this command during a 6 hour time period after game is created. ''', inline = False)

    #Host game commands
    embed.add_field(name='Host game commands:',value='''\n`am.round   or 🔇` - start the round (tasks). Deafens alive, unmutes dead.
                                                        \n`am.meeting or 📢` - call a meeting. Undeafens alive, mutes dead.
                                                        \n`am.lobby   or ⏮` - end of game, back to lobby. Undeafens and unmutes everyone.''', inline = False)

    #Player game commands
    embed.add_field(name='Player game commands:',value='''`am.dead or ☠` - toggle status to dead. Undeafens during rounds to discuss with other dead players and hear other players alive''', inline = False)

    #Management commands
    embed.add_field(name='Management commands:', value ='''`am.promote <@user>` - Promotes player to host. **Host only**
                                                         \n`am.kick <@user>` - removes player from game.
                                                         \n`am.leave` - leave game.''', inline = False)

    await ctx.send(embed=embed)



client.run(KEY)
