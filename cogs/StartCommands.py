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
              startall - start and joinall
    '''

    def muteDefault(self, guildID):
        try:
            sql_query = '''SELECT * FROM prefixes
                            WHERE id = (%s)'''
            c.execute(sql_query, (guildID,))
            setting = c.fetchone()

            if setting is None:
                return Muting.Deafen

            else:
                default = setting[2]
                if default == "Mute":
                    return Muting.Mute
                elif default == "Deafen":
                    return Muting.Deafen
                elif default == "Move":
                    return Muting.Move

        except:
            return Muting.Deafen

    def interfaceDefault(self, guildID):
        try:
            sql_query = '''SELECT * FROM prefixes
                            WHERE id = (%s)'''
            c.execute(sql_query, (guildID,))
            setting = c.fetchone()

            if setting is None:
                return Interface.Show

            else:
                default = setting[3]
                if default == "Show":
                    return Interface.Show
                elif default == "Hide":
                    return Interface.Hide

        except:
            return Interface.Show

    def controlDefault(self, guildID):
        try:
            sql_query = '''SELECT * FROM prefixes
                            WHERE id = (%s)'''
            c.execute(sql_query, (guildID,))
            setting = c.fetchone()

            if setting is None:
                return Controls.Reactions

            else:
                default = setting[4]
                if default == "Reactions":
                    return Controls.Reactions
                elif default == "Host":
                    return Controls.Host

        except:
            return Controls.Reactions

    @commands.command()
    async def startall(self, ctx, code=None):
        if code == None:
            code = "`am.code <code>`"
        await self.start(ctx, code)
        await self.joinall(ctx)

    @commands.command()
    async def start(self, ctx, code=None):
        if code == None:
            code = "`am.code <code>`"

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
        guildID = ctx.message.guild.id
        mute = self.muteDefault(guildID)
        interface = self.interfaceDefault(guildID)
        control = self.controlDefault(guildID)

        #Create game
        game = Game(voiceChannel, textChannel, host, code, mute, interface, control)
        #Send game
        await manage.sendEmbed(game, textChannel)

        addGame(game)

    @commands.command(aliases=['end', 'stop'])
    async def endgame(self, ctx):
        try:
            voiceChannel = ctx.message.author.voice.channel
            vcString = str(voiceChannel)
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

        #Delete game
        del games[voiceChannel]

        try:
            msg = game.getMsg()
            await msg.delete()
        except:
            pass

        await ctx.send("Game in `" + vcString + "` ended.")

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

        if len(members) > 15:
            await ctx.send("Failed: More than 15 people are in the voice channel.")
            return

        #Get all players in game
        playerList = game.getAllPlayers()

        #Kick everyone not including host
        for player in list(playerList):
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
