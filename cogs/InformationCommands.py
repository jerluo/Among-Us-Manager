import random
import os
import discord
from discord.ext import commands

class InformationCommands(commands.Cog):

    def __init__(self, client):
        self.client = client

        #Get tips from text document
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        imposter_file = os.path.join(THIS_FOLDER, 'impostertips.txt')
        crew_file = os.path.join(THIS_FOLDER, 'crewtips.txt')

        with open(imposter_file, 'r') as reader:
            self.imposterTips = reader.readlines()

        with open(crew_file, 'r') as reader:
            self.crewmateTips = reader.readlines()

    @commands.command()
    async def info(self, ctx):
        await ctx.send(r"https://github.com/jerryluoaustin/Among-Us-Manager")

    @commands.command()
    async def wiki(self, ctx):
        await ctx.send(r'https://among-us.fandom.com/wiki/Among_Us_Wiki')

    @commands.command(aliases = ['map'])
    async def _map(self, ctx, map):

        mapString = map.lower()

        embed = discord.Embed(colour = discord.Colour.blue())

        if(mapString == 'mira' or mapString == 'mirahq'):
            embed.set_image(url = r'https://i.imgur.com/iUf6FDq.png')
        elif(mapString == 'polus'):
            embed.set_image(url = r'https://i.imgur.com/sQr5DPK.png')
        elif(mapString == 'skeld'):
            embed.set_image(url = r'https://i.imgur.com/xvbDIP5.jpg')

        else:
            await ctx.send('Map `' + map + '` not found! Use either skeld, mira, or polus.')
            return

        await ctx.send(embed=embed)

    @commands.command(aliases=['tips'])
    async def tip(self, ctx, group):

        groupString = group.lower()

        if(groupString == 'imposter'):
            tip = random.choice(self.imposterTips)
        elif(groupString == 'crewmate' or groupString == 'crew'):
            tip = random.choice(self.crewmateTips)
        else:
            tip = '`' + group + '` is not valid. Use `am.tip imposter` or `am.tip crewmate`'

        await ctx.send(tip)


def setup(bot):
    bot.add_cog(InformationCommands(bot))
