import discord
from discord.ext import commands

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from objects import *
from GameManager import *

class StartCommands(commands.Cog):

    def __init__(self, client):
        self.client = client

    '''
    Commands: start - start game
              join - join game
              joinall - join everyone in vc
              endgame - end the game
    '''

    @commands.command()
    async def start(self, ctx, code):
        try:
            voiceChannel = ctx.message.author.voice.channel
        except:
            await ctx.send('Join voice channel to start.')
            return

        manage = self.client.get_cog('ManagementCommands')

        #Check if game exists
        if gameExist(voiceChannel) is not False:
            await ctx.send("Game already exists. \nDon't know where it is? Type `am.endgame` to terminate it.")
            return

        #Get all variables
        host = ctx.message.author
        voiceChannel = ctx.message.author.voice.channel
        textChannel = ctx.message.channel

        #Create game
        game = Game(voiceChannel, textChannel, host, code)
        #Send game
        await manage.sendEmbed(game, textChannel)

        addGame(game)

    @commands.command()
    async def endgame(self, ctx):
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

        await ctx.send("Game in `" + str(voiceChannel) + "` ended.")

    @commands.command()
    async def join(self, ctx):
        try:
            voiceChannel = ctx.message.author.voice.channel
        except:
            await ctx.send('Join voice channel to join the game.')
            return

        manage = self.client.get_cog('ManagementCommands')

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
            await manage.sendEmbed(game, textChannel)

        except Exception as e:
            return

    @commands.command()
    async def joinall(self, ctx):
        try:
            voiceChannel = ctx.message.author.voice.channel
        except:
            return

        manage = self.client.get_cog('ManagementCommands')

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

        if not members:
            await ctx.send("Unfortunately due to a bot restart, `am.joinall` is broken. To fix this, switch voice channels (or leave and join the same one), OR have everyone manually type `am.join`.")
            return

        #Remove all bots
        for member in members:
            if member.bot == True:
                members.remove(member)

        if len(members) > 10:
            await ctx.send("Failed: More than 10 people are in the voice channel.")
            return

        #Kick everyone except host first
        playerList = game.getAllPlayers
        for player in playerList:
            if str(player) is not str(member):
                game.removePlayer(player)

        #Now add everyone back
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
            await manage.sendEmbed(game, textChannel)

        except Exception:
            return


def setup(bot):
    bot.add_cog(StartCommands(bot))
