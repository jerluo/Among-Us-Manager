import os
import dbl
import discord
from discord.ext import commands, tasks


class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        KEY = os.environ.get('API')
        self.token = KEY
        self.dblpy = dbl.DBLClient(self.bot, self.token)

    @tasks.loop(minutes=30.0)
    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count"""
        try:
            await self.dblpy.post_guild_count(guild_count=len(self.bot.guilds), shard_count=len(self.bot.shards))
            print('Posted server count ({})'.format(self.dblpy.guild_count()))
        except Exception as e:
            print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

def setup(bot):
    bot.add_cog(TopGG(bot))
