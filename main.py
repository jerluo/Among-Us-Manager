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
        description = "***IMPORTANT***: If you're using this bot at around 12AM EST the bot may restart and delete your game while ongoing. Just simply start a new game if it stops working."
    )

    embed.set_author(name = '[Among Us Manager] Commands:')

    #Starting commands
    embed.add_field(name='Getting started:',value='''`am.start <code>` - host new game in current voice channel. Only one game is allowed in each voice channel. *Code optional*
                                                  \n`am.join` - joins existing game in voice channel.
                                                  \n`am.joinall` - joins everyone in the voice channel into the game. *Kicks everyone in the game but not in the voice channel*
                                                  \n`am.endgame` - terminates existing game in voice channel. Only players in the game are able to use this command during a 6 hour time period after game is created. ''', inline = False)

    #Host game commands
    embed.add_field(name='Host game commands: if these commands are spammed the bot will slow down',value='''\n`am.round   or 🔇` - mute everyone alive (tasks).
                                                        \n`am.meeting or 📢` - umutes everyone alive (meeting).
                                                        \n`am.lobby   or ⏮` - restart game (lobby). Sets everyone alive and unmutes all.''', inline = False)

    #Player game commands
    embed.add_field(name='Player game commands:',value='''`am.dead or ☠` - toggle status to dead: lets you hear everyone during rounds.''', inline = False)

    #Management commands
    embed.add_field(name='Management commands:', value ='''`am.promote <@user>` - promotes player to host. **Host only**
                                                         \n`am.kick <@user>` - removes player from game.
                                                         \n`am.leave` - leave game.
                                                         \n`am.code <code>` - change the code displayed on the interface.''', inline = False)

    embed.add_field(name='Wiki commands:', value = '''`am.wiki` - link to the official Among Us Fandom Wiki.
                                                    \n`am.map <map>` - image of map with vents, common tasks, and more.
                                                    \n`am.tip <imposter OR crewmate>` - returns random tip for either the imposter or crewmate.''', inline = False)

    embed.add_field(name="Information:", value = '''`am.info` - github link and invite link.
                                                  \n`am.vote` - vote to support the bot!''')

    embed.set_footer(text='Created by Jerry#5922')

    await ctx.send(embed=embed)



client.run(KEY)
