import discord
from discord.ext import commands

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)


from objects import *
from GameManager import *

class GameCommands(commands.Cog):

    def __init__(self, client):
        self.client = client

    '''
        Commands: dead - set dead
                  round - change to round
                  meeting - change to meeting
                  lobby - change to lobby
    '''

    @commands.command()
    async def code(self, ctx, code):
        try:
            voiceChannel = ctx.message.author.voice.channel
        except:
            return

        member = ctx.message.author


        game, player = gameRequirements(member, voiceChannel)
        if game is False or player is False:
            await ctx.send("Create a game with `am.start`")
            return


        game.setCode(code)
        manage = self.client.get_cog('ManagementCommands')
        textChannel = game.getText()
        await manage.sendEmbed(game, textChannel)

    @commands.command()
    async def dead(self, ctx):
        try:
            voiceChannel = ctx.message.author.voice.channel
        except:
            return

        member = ctx.message.author

        await self.changeDead(member, voiceChannel)

    @commands.command(aliases=['round'])
    async def _round(self, ctx):
        try:
            voiceChannel = ctx.message.author.voice.channel
        except:
            return

        member = ctx.message.author

        await self.changeStage(member, voiceChannel, Stage.Round)

    @commands.command()
    async def meeting(self, ctx):
        try:
            voiceChannel = ctx.message.author.voice.channel
        except:
            return

        member = ctx.message.author

        await self.changeStage(member, voiceChannel, Stage.Meeting)

    @commands.command()
    async def lobby(self, ctx):
        try:
            voiceChannel = ctx.message.author.voice.channel
        except:
            return

        member = ctx.message.author

        await self.changeStage(member, voiceChannel, Stage.Lobby)

    #Changing methods

    async def changeStage(self, member, voiceChannel, stage):

        manage = self.client.get_cog('ManagementCommands')

        #Get game and player
        game, player = gameRequirements(member, voiceChannel)
        if game is False:
            return

        if(player is False):
            return

        if player is not game.getHost():
            return

        try:
            #Delete prior message
            msg = game.getMsg()
            await msg.delete()
        except:
            pass

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
            except discord.errors.Forbidden:
                await textChannel.send("Missing Permissions! Reinvite the bot or give back roles.")
                return

            except discord.errors.HTTPException:
                mention = member.mention
                await textChannel.send("Error! " + mention + " is not in the voice channel.\nType `am.kick @user` to remove a player.\n")
                continue
            except Exception as e:
                print(e)


        if stage == Stage.Lobby:
            game.setAllAlive()

        #Set stage
        game.setStage(stage)

        #Send embed
        await manage.sendEmbed(game, textChannel)

    async def changeDead(self, member, voiceChannel):
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


def setup(bot):
    bot.add_cog(GameCommands(bot))
