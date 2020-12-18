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
        Commands: code - set code
                  dead - set member to dead
                  round - change to round
                  meeting - change to meeting
                  lobby - change to lobby
    '''

    @commands.command()
    async def code(self, ctx, code: str):
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

        try:
            #Delete prior message
            msg = game.getMsg()
            await msg.delete()
        except:
            pass

        await manage.sendEmbed(game, textChannel)

    @commands.command()
    async def dead(self, ctx, member: discord.Member=None):
        if member is None:
            member = ctx.message.author

        try:
            voiceChannel = ctx.message.author.voice.channel
        except:
            return

        #Get game and player
        game, player = gameRequirements(member, voiceChannel)
        if game is False or player is False:
            return

        await self.changeDead(game, player)

    @commands.command(aliases=['round', 'mute', 'm'])
    async def _round(self, ctx):
        try:
            voiceChannel = ctx.message.author.voice.channel
        except:
            return

        member = ctx.message.author

        #Get game and player
        game, player = gameRequirements(member, voiceChannel)
        if game is False or player is False:
            return

        await self.changeStage(game, player, Stage.Round)

    @commands.command(aliases=['unmute', 'u'])
    async def meeting(self, ctx):
        try:
            voiceChannel = ctx.message.author.voice.channel
        except:
            return

        member = ctx.message.author

        #Get game and player
        game, player = gameRequirements(member, voiceChannel)
        if game is False or player is False:
            return

        await self.changeStage(game, player, Stage.Meeting)

    @commands.command(aliases=['restart'])
    async def lobby(self, ctx):
        try:
            voiceChannel = ctx.message.author.voice.channel
        except:
            return

        member = ctx.message.author

        #Get game and player
        game, player = gameRequirements(member, voiceChannel)
        if game is False or player is False:
            return

        await self.changeStage(game, player, Stage.Lobby)

    #Changing methods
    async def changeStage(self, game, player, stage):

        manage = self.client.get_cog('ManagementCommands')
        textChannel = game.getText()

        #Already doing actions
        if game.cooldown is True:
            await textChannel.send("Attempting commands too fast!")
            return

        if player is not game.getHost():
            return

        game.setCooldown(True)

        try:
            #Delete prior message
            msg = game.getMsg()
            await msg.delete()
        except:
            pass

        #Error embeds
        permEmbed = discord.Embed(
            colour = discord.Colour.orange(),
            description = 'Reinvite bot to regain bot permissions or check text channel permissions.\nUse `am.info` to get invite link.'
        )
        permEmbed.set_author(name = 'Missing permissions!')

        #Move channel setting
        if game.muteSetting == Muting.Move:
            await self.changeMove(game, textChannel, stage, permEmbed)

        #Muting or deafening setting
        else:
            await self.changeMute(game, textChannel, stage, permEmbed)

        if stage == Stage.Lobby:
            game.setAllAlive()

        #Set stage
        game.setStage(stage)

        try:
            #Send embed
            await manage.sendEmbed(game, textChannel)
        except discord.errors.Forbidden:
            game.setCooldown(False)
            return

        game.setCooldown(False)

    async def changeMove(self, game, textChannel, stage, permEmbed):
        if not isinstance(game.deadVC, discord.VoiceChannel):
            embed = discord.Embed(
                colour = discord.Colour.orange(),
                description = "Set a dead channel using `am.channel <channel>`."
            )
            embed.set_author(name = 'Error!')
            await textChannel.send(embed=embed)
            game.setCooldown(False)
            return

        if stage == Stage.Lobby:
            aliveBool = False
            deadChannel = game.voiceChannel

        if stage == Stage.Round:
            aliveBool = True
            deadChannel = game.deadVC

        if stage == Stage.Meeting:
            aliveBool = False
            deadChannel = game.voiceChannel

        players = game.getAllPlayers()
        deadPlayers = []

        for player in players:
            status = player.isAlive()
            member = player.getMember()

            try:
                #If user isn't connected to voice
                if member.voice == None:
                    embed = discord.Embed(
                        colour = discord.Colour.orange(),
                        description = str(member) + ' is not connected to the voice channel!\nType `am.kick @user` to remove a player.'
                    )
                    embed.set_author(name = 'Oops!')
                    await textChannel.send(embed=embed)
                    continue

                #Alive actions
                if status == True:
                    #Mute them if we're in a round
                    if member.voice.mute != aliveBool:
                        await member.edit(mute = aliveBool)

                #Dead actions
                elif status == False:
                    #For later to unmute
                    deadPlayers.append(member)

                    if member.voice.channel != deadChannel:
                        await member.move_to(deadChannel)

            except discord.errors.Forbidden:
                await textChannel.send(embed=permEmbed)
                game.setCooldown(False)
                return

            except discord.errors.HTTPException:
                await textChannel.send("Error: Voice channel deleted?")
                deleteVC(game.deadVC)
                game.setDeadVC("None")
                game.setCooldown(False)
                return

        #Unmute dead players unless we're in a meeting.
        if stage != Stage.Meeting:
            for member in deadPlayers:
                try:
                    if member.voice.mute != False:
                        await member.edit(mute = False)
                except:
                    continue

    async def changeMute(self, game, textChannel, stage, permEmbed):
        #If lobby
        if stage == Stage.Lobby:
            aliveBool = False
            deadBool = False
        #If round
        elif stage == Stage.Round:
            if game.muteSetting == Muting.Deafen:
                aliveBool = True
                deadBool = False
            else:
                aliveBool = True
                deadBool = True
        #If meeting
        elif stage == Stage.Meeting:
            aliveBool = False
            deadBool = True

        #Get all players
        players = game.getAllPlayers()
        for player in players:

            status = player.isAlive()
            member = player.getMember()

            #Try to change voice states
            try:
                #If user isn't connected to voice
                if member.voice == None:
                    embed = discord.Embed(
                        colour = discord.Colour.orange(),
                        description = str(member) + ' is not connected to the voice channel!\nType `am.kick @user` to remove a player.'
                    )
                    embed.set_author(name = 'Oops!')
                    await textChannel.send(embed=embed)
                    continue

                if status == True:
                    #Deafen setting
                    if game.muteSetting == Muting.Deafen:
                        if member.voice.deaf != aliveBool:
                            await member.edit(deafen = aliveBool)
                    #Mute setting
                    else:
                        if member.voice.mute != aliveBool:
                            await member.edit(mute = aliveBool)

                elif status == False:
                    if member.voice.mute != deadBool:
                        await member.edit(mute = deadBool)

            except discord.errors.Forbidden:
                await textChannel.send(embed=permEmbed)
                game.setCooldown(False)
                return

            except discord.errors.HTTPException:
                await textChannel.send(embed=embed)
                continue

    async def changeDead(self, game, player):
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

        try:
            if stage == Stage.Meeting:
                await member.edit(mute = muteBool)
            if stage == Stage.Round:
                await member.edit(deafen = deafenBool)
        except:
            pass


def setup(bot):
    bot.add_cog(GameCommands(bot))
