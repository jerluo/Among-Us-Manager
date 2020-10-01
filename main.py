import asyncio
import discord
import random
import time
import datetime
import os
from objects import Game
from objects import Player
from objects import Stage
from discord.ext import commands


client = commands.Bot(command_prefix = 'am.')
client.remove_command('help')

games = {}

KEY = os.environ.get('KEY')


"""
    EVENTS: on_ready
            on_reaction_add
"""


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="am.help"))
    print('Bot is ready.')


@client.event
async def on_reaction_add(reaction, user):
    #Make sure reaction isn't from bot
    if user == client.user:
        return

    reaction = str(reaction)

    #Make sure reaction is releated to the game
    if reaction != '☠' and reaction != '📢' and reaction != '🔇' and reaction != '⏮':
        return

    #Variables needed
    try:
        voiceChannel = user.voice.channel
    except:
        return

    member = user

    #Dead reaction
    if reaction == '☠':
        await deadWorker(member, voiceChannel)


    #Meeting reaction
    if reaction == '📢':
        await changeStage(member, voiceChannel, Stage.Meeting)

    #Mute reaction
    if reaction == '🔇':
        await changeStage(member, voiceChannel, Stage.Round)

    #Meeting reaction
    if reaction == '⏮':
        await changeStage(member, voiceChannel, Stage.Lobby)


'''
    Commands: start - start game
              join - join game
              joinall - join everyone in vc
              dead - set dead
              round - change to round
              meeting - change to meeting
              lobby - change to lobby
              endgame - end the game
              kick - kick player
              leave - leave game
              promote - promote player to host
'''

@client.command()
async def test(ctx):
    voiceChannel = ctx.message.author.voice.channel
    game = gameExist(voiceChannel)

    time = datetime.datetime.now()
    oldTime = game.getTime()
    diff = (time - oldTime).seconds
    hourDiff = (diff//60) % 60
    print(diff)
    print(hourDiff)


@client.command()
async def start(ctx):
    try:
        voiceChannel = ctx.message.author.voice.channel
    except:
        await ctx.send('Join voice channel to start.')
        return


    #Check if game exists
    if gameExist(voiceChannel) is not False:
        await ctx.send("Game already exists. \nDon't know where it is? Type `am.endgame` to terminate it.")
        return

    #Get all variables
    host = ctx.message.author
    voiceChannel = ctx.message.author.voice.channel
    textChannel = ctx.message.channel

    #Create game
    game = Game(voiceChannel, textChannel, host)
    #Send game
    await sendEmbed(game, textChannel)

    games[voiceChannel] = game

@client.command()
async def join(ctx):
    try:
        voiceChannel = ctx.message.author.voice.channel
    except:
        await ctx.send('Join voice channel to join the game.')
        return

    #Get the game
    game = gameExist(voiceChannel)
    if(game is False):
        await ctx.send("Game doesn't exist. Type `am.start` to start a game.")
        return

    #See if player is already in
    member = ctx.message.author
    player = game.getPlayer(member)
    if player is not False:
        return

    #Add player
    game.addPlayer(member)

    try:
        #Delete previous embed
        msg = game.getMsg()
        await msg.delete()

        #Send embed
        textChannel = game.getText()
        await sendEmbed(game, textChannel)

    except Exception as e:
        print(e)

@client.command()
async def joinall(ctx):
    try:
        voiceChannel = ctx.message.author.voice.channel
    except:
        return

    member = ctx.message.author

    game, player = gameRequirements(member, voiceChannel)
    if game is False:
        await ctx.send("Game doesn't exist. Type `am.start` to start a game.")
        return

    if player is not game.getHost():
        await ctx.send("Only host can join all.")
        return

    #List of all members in channel
    members = voiceChannel.members

    #Remove all bots
    for member in members:
        if member.bot == True:
            members.remove(member)

    if len(members) >= 10:
        await ctx.send("Failed: More than 10 people are in the voice channel.")
        return

    for member in members:
        player = game.getPlayer(member)
        #If player is already in the game
        if player is not False:
            continue

        else:
            #Add player
            game.addPlayer(member)

    try:
        #Delete previous embed
        msg = game.getMsg()
        await msg.delete()

        #Send embed
        textChannel = game.getText()
        await sendEmbed(game, textChannel)

    except Exception:
        pass

@client.command()
async def dead(ctx):
    try:
        voiceChannel = ctx.message.author.voice.channel
    except:
        return

    member = ctx.message.author

    await deadWorker(member, voiceChannel)

@client.command(aliases=['round'])
async def _round(ctx):
    try:
        voiceChannel = ctx.message.author.voice.channel
    except:
        return

    member = ctx.message.author

    await changeStage(member, voiceChannel, Stage.Round)

@client.command()
async def meeting(ctx):
    try:
        voiceChannel = ctx.message.author.voice.channel
    except:
        return

    member = ctx.message.author

    await changeStage(member, voiceChannel, Stage.Meeting)

@client.command()
async def lobby(ctx):
    try:
        voiceChannel = ctx.message.author.voice.channel
    except:
        return

    member = ctx.message.author

    await changeStage(member, voiceChannel, Stage.Lobby)

@client.command()
async def endgame(ctx):
    try:
        voiceChannel = ctx.message.author.voice.channel
    except:
        return

    member = ctx.message.author
    #Get game and player
    game, player = gameRequirements(member, voiceChannel)
    if(game is False):
        await ctx.send("Game doesn't exist.")
        return

    #Get current time and game creation time
    time = datetime.datetime.now()
    oldTime = game.getTime()

    #Get hour difference
    diff = (time - oldTime).seconds
    hourDiff = (diff//60) % 60




    #Player is not in the game
    if player is False:
        #If hour diff is <= 6 then return because only players should be able to end the game
        if hourDiff <= 6:
            await ctx.send("Only players in the game can end the game during the first 6 hours of creation.\nYou can create a new game in a new voice channel.")
            return

    voiceChannel = game.getVoice()
    del games[voiceChannel]

    msg = game.getMsg()
    await msg.delete()

    await ctx.send("Game ended.")

@client.command()
async def kick(ctx, *, kicked: discord.Member):
    #Make sure game exists and person kicking is in the game
    try:
        voiceChannel = ctx.message.author.voice.channel
    except:
        return

    member = ctx.message.author
    #Get game and player
    game, player = gameRequirements(member, voiceChannel)
    if(game is False or player is False):
        return

    player = game.getPlayer(kicked)
    if player is False:
        await ctx.send(str(kicked) + " is not in the game.")
        return

    player = Player(kicked)
    game.removePlayer(player)
    await ctx.send(str(player) + " was removed from the game.")

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Invalid member. Type `am.kick <@user>` to remove a player.")

@client.command()
async def leave(ctx):
    try:
        voiceChannel = ctx.message.author.voice.channel
    except:
        return

    member = ctx.message.author

    game, player = gameRequirements(member, voiceChannel)
    if game is False:
        await ctx.send("Game doesn't exist in: " + voiceChannel.name + ".")
        return
    if player is False:
        await ctx.send("You are not in the game in: " + voiceChannel.name + ".")
        return

    if game.getHost() is player:
        await ctx.send("You are the host. Promote someone else to host before leaving using `am.promote <@user>`.")
        return

    game.removePlayer(player)
    await ctx.send("Removed from game in: " + voiceChannel.name + ".")

@client.command()
async def promote(ctx, promote: discord.Member):
    try:
        voiceChannel = ctx.message.author.voice.channel
    except:
        return

    host = ctx.message.author

    game, player = gameRequirements(host, voiceChannel)

    #Game exist?
    if game is False:
        await ctx.send("Game doesn't exist in: " + voiceChannel.name)
        return

    #Player is host?
    if player is not game.getHost():
        await ctx.send("Only host can promote.")
        return

    newHost = game.getPlayer(promote)

    #New host is in game?
    if newHost is False:
        await ctx.send(str(promote) + " is not in the game.")
        return

    #Finally promote player
    game.setHost(newHost)
    await ctx.send(str(promote) + " is the new host.")

@promote.error
async def promote_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Invalid member. Type `am.promote <@user>` to promote a player.")

@client.command()
async def update(ctx):
    try:
        voiceChannel = ctx.message.author.voice.channel
    except:
        return

    member = ctx.message.author
    game, player = gameRequirements(member, voiceChannel)
    if(game is False or player is False):
        return

    textChannel = game.getText()
    await sendEmbed(game, textChannel)

'''
    HELP METHODS: changeStage - meeting, round, lobby changer
                  deadWorker - set yourself dead
                  gameExist - find game/make sure it exists
                  gameRequirements - when you need to get player and game
'''


async def changeStage(member, voiceChannel, stage):
    #Get game and player
    game, player = gameRequirements(member, voiceChannel)
    if game is False:
        return

    if(player is False):
        return

    if player is not game.getHost():
        return

    #Delete prior message
    msg = game.getMsg()
    await msg.delete()

    #If lobby
    if stage == Stage.Lobby:
        aliveBool = False
        deadBool = False
    #If round
    elif stage == Stage.Round:
        aliveBool = True
        deadBool = False
    #If meeting
    elif stage == Stage.Meeting:
        aliveBool = False
        deadBool = True

    textChannel = game.getText()

    #Get all players
    players = game.getAllPlayers()
    for player in players:

        status = player.isAlive()
        member = player.getMember()

        #Try to change voice states
        try:
            if status == True:
                await member.edit(deafen = aliveBool)
            elif status == False:
                await member.edit(mute = deadBool)
        except Exception as e:
            if isinstance(e, discord.errors.HTTPException):
                mention = member.mention
                await textChannel.send("Error! " + mention + " is not in the voice channel.\nType `am.kick @user` to remove a player.\n")
            else:
                await textChannel.send("Failed")
                print(e)

            continue


    if stage == Stage.Lobby:
        game.setAllAlive()

    #Set stage
    game.setStage(stage)

    #Send embed
    await sendEmbed(game, textChannel)


async def deadWorker(member, voiceChannel):
    #Get game and player
    game, player = gameRequirements(member, voiceChannel)
    if(game is False or player is False):
        return

    #Set them to opposite
    player.setAlive(not player.isAlive())

    stage = game.getStage()
    #Edit voice state
    member = player.getMember()

    if player.isAlive() is False:
        muteBool = True
        deafenBool = False
    else:
        muteBool = False
        deafenBool = True

    if stage == Stage.Meeting:
        await member.edit(mute = muteBool)
    if stage == Stage.Round:
        await member.edit(deafen = deafenBool)

#Returns game if exists, if not returns false
def gameExist(voiceChannel):
    #Check dictionary
    if voiceChannel in games.keys():
        return games[voiceChannel]
    else:
        return False

def gameRequirements(member, voiceChannel):
    #Check for game
    game = gameExist(voiceChannel)
    if game is False:
        player = False
        return game, player

    player = game.getPlayer(member)
    return game, player

#Sends embed of interface to text channel
async def sendEmbed(game, textChannel):

    msg = await textChannel.send(embed=game.getInterface())
    await msg.add_reaction('☠')
    await msg.add_reaction('🔇')
    await msg.add_reaction('📢')
    await msg.add_reaction('⏮')

    game.prevMsg(msg)

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
