import psycopg2
import discord
from discord.ext import commands

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from objects import *
from GameManager import *


class Database(commands.Cog):

    def __init__(self, bot):
        self.client = bot

    @commands.command()
    async def default(self, ctx):
        #Get game and make sure it's the host
        try:
            voiceChannel = ctx.message.author.voice.channel
        except:
            return

        host = ctx.message.author

        game, player = gameRequirements(host, voiceChannel)

        if game is False or player is not game.getHost():
            return

        #Settings
        muting = game.muteSetting.name
        interface = game.interfaceSetting.name
        control = game.controlSetting.name
        guildID = ctx.message.guild.id

        #Get current settings
        sql_query = '''SELECT FROM prefixes
                        WHERE id = (%s)'''
        c.execute(sql_query, (guildID,))
        settings = c.fetchone()

        #Guild isn't already in database
        if settings is None:
            sql_query = '''INSERT INTO prefixes (id, prefix, mute, interface, control)
                            VALUES (%s, %s, %s, %s, %s)'''
            c.execute(sql_query, (guildID, 'am.', muting, interface, control))
        #Update values
        else:
            sql_query = '''UPDATE prefixes
                            SET mute = %s, interface = %s, control = %s
                            WHERE id = %s'''

            c.execute(sql_query, (muting, interface, control, guildID))

        conn.commit()

        guild = ctx.message.guild.name
        embed = discord.Embed(
            colour = discord.Colour.orange(),
            title = "⚙️ Set `" + guild + "` default settings:",
            description = "🔇 **Muting:** " + game.muteSetting.name +
                   "\n" + "🖥️ **Interface:** " + game.interfaceSetting.name +
                   "\n" + "🎮 **Controls:** " + game.controlSetting.name
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def prefix(self, ctx, prefix):

        userPrefix = str(prefix)

        try:
            guildID = ctx.message.guild.id
        except AttributeError:
            await ctx.send("Changing prefix is only possible in servers!")
            return

        sql_query = '''SELECT FROM prefixes
                        WHERE id = (%s)'''
        c.execute(sql_query, (guildID,))
        prefix = c.fetchone()

        #Check if prefix exists
        if prefix is not None:
            #Delete prior prefix
            sql_execute = '''DELETE FROM prefixes
                              WHERE id = (%s)'''
            c.execute(sql_execute, (guildID,))

        #Add prefix to list
        sql_execute = '''INSERT INTO prefixes (id, prefix)
                          VALUES (%s, %s)'''
        c.execute(sql_execute, (guildID, userPrefix))
        await ctx.send("Successfully changed prefix to " + userPrefix)

        conn.commit()


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        guildID = guild.id
        sql_execute = '''DELETE FROM prefixes
                          WHERE id = (%s)'''
        c.execute(sql_execute, (guildID,))

        conn.commit()

def setup(bot):
    bot.add_cog(Database(bot))
