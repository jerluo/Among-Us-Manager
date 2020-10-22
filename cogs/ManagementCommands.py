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
    '''

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

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            try:
                await ctx.send("Invalid member. Type `am.kick <@user>` to remove a player.")
            except:
                return
        else:
            print(error)

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

    @promote.error
    async def promote_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            try:
                await ctx.send("Invalid member. Type `am.promote <@user>` to promote a player.")
            except:
                return
        else:
            print(error)

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

        textChannel = game.getText()
        await self.sendEmbed(game, textChannel)


    #Sends embed of interface to text channel
    async def sendEmbed(self, game, textChannel):

        msg = await textChannel.send(embed=game.getInterface())
        await msg.add_reaction('☠')
        await msg.add_reaction('🔇')
        await msg.add_reaction('📢')
        await msg.add_reaction('⏮')

        game.prevMsg(msg)

def setup(bot):
    bot.add_cog(ManagementCommands(bot))
