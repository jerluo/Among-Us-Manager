import time
import datetime
import discord
from discord.ext import commands

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from objects import *
from GameManager import *

class ManagementCommands(commands.Cog):

    def __init__(self, client):
        self.client = client

    '''
        Commands: kick - kick player
                  leave - leave game
                  promote - promote player to host
                  update - update interface
                  settings - display/change game settings
                  channel - dead channel
    '''

    @commands.command(aliases = ['setting'])
    async def settings(self, ctx, setting: str=None):
        #Get game and make sure it's the host
        try:
            voiceChannel = ctx.message.author.voice.channel
        except:
            return

        host = ctx.message.author

        game, player = gameRequirements(host, voiceChannel)

        #Game exist?
        if game is False:
            await ctx.send("Game doesn't exist in `" + voiceChannel.name + "`")
            return

        if setting == None:
            await ctx.send(embed=game.getSettings())

        else:
            #Player is host?
            if player is not game.getHost():
                await ctx.send("Only host can change settings.")
                return

            settings = setting.lower()

            if settings == "mute" or settings == "deafen" or settings == "move":
                game.setMute(settings)

            elif settings == "show" or settings == "hide":
                game.setInterface(settings)

            elif settings == "reactions" or settings == "host":
                game.setControls(settings)

                if settings == "host":
                    game.setMute("mute")

            else:
                await ctx.send("`" + settings + "` is not a valid setting.")
                return

            await ctx.send(embed=game.getSettings())
            await self.update(ctx)

    @commands.command()
    async def channel(self, ctx, *, vc=None):

        #Get game and make sure it's the host
        try:
            voice = ctx.message.author.voice.channel
        except:
            return

        host = ctx.message.author

        game, player = gameRequirements(host, voice)

        if game is False or player is False:
            return

        #Create new channel
        if vc is None:
            guild = ctx.message.guild
            category = ctx.message.author.voice.channel.category
            try:
                voiceChannel = await guild.create_voice_channel("Dead Channel",category=category)
            except discord.errors.Forbidden:
                permEmbed = discord.Embed(
                    colour = discord.Colour.orange(),
                    description = 'Reinvite bot to regain bot permissions or check text channel permissions.\nUse `am.info` to get invite link.'
                )
                permEmbed.set_author(name = 'Missing permissions!')
                await ctx.send(embed=permEmbed)
                return
            except discord.errors.HTTPException:
                await ctx.send("Error creating voice channel.")
                return

            deleteVC(game.deadVC)
            secondVC(game, voiceChannel)
            game.setDeadVC(voiceChannel)

        #Inputted channel
        else:
            voiceChannel = None
            for channel in ctx.guild.voice_channels:
                if channel.name == vc:
                    voiceChannel = channel

            if voiceChannel is None:
                await ctx.send("Voice channel not found (make sure capitalization is correct).")
                return

            if player is not game.getHost():
                await ctx.send("Only host can change settings.")
                return

            if voiceChannel == game.getVoice():
                await ctx.send("Dead voice channel must be different channel than the main voice channel.")
                return
            else:
                deleteVC(game.deadVC)
                secondVC(game, voiceChannel)
                game.setDeadVC(voiceChannel)

        await self.update(ctx)


    @commands.command()
    async def leave(self, ctx):
        try:
            voiceChannel = ctx.message.author.voice.channel
        except:
            return

        member = ctx.message.author

        game, player = gameRequirements(member, voiceChannel)
        if game is False or player is False:
            return

        if game.getHost() is player:
            await ctx.send("You are the host. Promote someone else to host before leaving using `am.promote <@user>`.")
            return

        game.removePlayer(player)

        try:
            #Delete previous embed
            msg = game.getMsg()
            await msg.delete()

            #Send embed
            textChannel = game.getText()
            await self.sendEmbed(game, textChannel)

        except Exception as e:
            return

        await ctx.send("Removed from game in `" + voiceChannel.name + "`")

    @commands.command()
    async def kick(self, ctx, *, kicked: discord.Member):
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

        try:
            #Delete previous embed
            msg = game.getMsg()
            await msg.delete()

            #Send embed
            textChannel = game.getText()
            await self.sendEmbed(game, textChannel)

        except Exception as e:
            return

        await ctx.send(str(player) + " was removed from the game.")

    @commands.command()
    async def promote(self, ctx, member: discord.Member):
        try:
            voiceChannel = ctx.message.author.voice.channel
        except:
            return

        host = ctx.message.author

        game, player = gameRequirements(host, voiceChannel)

        #Game exist?
        if game is False:
            await ctx.send("Game doesn't exist in `" + voiceChannel.name + "`")
            return

        #Player is host?
        if player is not game.getHost():
            await ctx.send("Only host can promote.")
            return

        newHost = game.getPlayer(member)

        #New host is in game?
        if newHost is False:
            await ctx.send(str(member) + " is not in the game.")
            return

        #Finally promote player
        game.setHost(newHost)
        await ctx.send(str(member) + " is the new host in `" + str(voiceChannel) + "`")

    @commands.command()
    async def update(self, ctx):
        try:
            voiceChannel = ctx.message.author.voice.channel
        except:
            return

        member = ctx.message.author
        game, player = gameRequirements(member, voiceChannel)
        if(game is False or player is False):
            return

        try:
            msg = game.getMsg()
            msg.type
            await msg.delete()
        except:
            pass

        textChannel = game.getText()
        await self.sendEmbed(game, textChannel)


    #Sends embed of interface to text channel
    async def sendEmbed(self, game, textChannel):

        msg = await textChannel.send(embed=game.getInterface())

        try:
            await msg.add_reaction('☠')
            await msg.add_reaction('🔇')
            await msg.add_reaction('📢')
            await msg.add_reaction('⏮')
        except Exception as e:
            if "Missing Permissions" in str(e):
                await textChannel.send('Missing permissions (most likely sending reactions), try reinviting the bot.')
            else:
                await textChannel.send('Unexpected error! Try `am.update` if interface is missing.')

        game.prevMsg(msg)

def setup(bot):
    bot.add_cog(ManagementCommands(bot))
