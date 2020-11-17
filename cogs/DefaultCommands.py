import discord
from discord.ext import commands

class DefaultCommands(commands.Cog):

    def __init__(self, client):
        self.client = client

    '''
    Commands: help - help
              ping - pong
    '''

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.client.latency * 1000)}ms')

    @commands.command()
    async def help(self, ctx, page=None):

        embed = discord.Embed(
            colour = discord.Colour.orange(),
            description = '**| Page 1: Quick Start | Page 2: Additional Commands | Page 3: Full List |**'
        )

        embed.set_footer(text = 'Created by Jerry#5922',)

        #Quick start (1)
        if page is None or int(page) == 1:
            embed.set_author(name = 'Among Us Manager - Quick Start: | Page 1 / 3')
            embed.add_field(name= '📝 Bot description', value="""This bot uses 'games' in voice channels and an 'interface' message with reactions to manage muting. The muting is done by deafening users.
                                                                \n***Things to know:***
                                                                \n**•** Every discord server can only handle 10 voice changes (muting or deafening) every ~5 seconds. If you missclick and surpass this limit there will be a 5 second delay (by Discord) until the next voice changes happen.
                                                                \n**•** The bot has routine restart every 24 hours; if your game is deleted and commands stop working, simply create a new game.""", inline = False)
            embed.add_field(name = '▶️ Start new game', value='''`am.start <code>` - host new game in current voice channel. *Code optional*
                                                                \n`am.joinall` - joins everyone in the voice channel into the game.
                                                                \n`am.startall <code>` - combines start and joinall into one command. *Code optional*''', inline = False)
            embed.add_field(name = '🛠️ Host commands', value='''\n`am.round   or 🔇` - mute everyone alive (tasks).
                                                                \n`am.meeting or 📢` - unmutes everyone alive (meeting).
                                                                \n`am.lobby   or ⏮` - restart game (lobby). Sets everyone alive and unmutes all.''', inline = False)
            embed.add_field(name='🧑 Player commands',value='''`am.dead or ☠` - toggle status to dead: lets you hear everyone during rounds.''', inline = False)

        #Additional (2)
        elif int(page) == 2:
            embed.set_author(name = 'Among Us Manager - Additional Commands: | Page 2 / 3')
            embed.add_field(name="🛑 Ending commands:", value = '''`am.endgame` - ends the game in the voice channel.
                                                                 \n`am.leave` - leave game.''', inline = False)
            embed.add_field(name='👨‍⚖️ Management commands:', value ='''`am.promote <@user>` - promotes player to host.
                                                                 \n`am.kick <@user>` - removes player from game.
                                                                 \n`am.update` - resend interface.
                                                                 \n`am.code <code>` - change the code.''', inline = False)

            embed.add_field(name='📚 Wiki commands:', value = '''`am.wiki` - link to the Wiki.
                                                            \n`am.map <map>` - detailed map.
                                                            \n`am.tip <imposter OR crewmate>` - returns random tip.''', inline = False)

        #All commands (3)
        elif int(page) == 3:
            embed.set_author(name = 'Among Us Manager - Full List: | Page 3 / 3')

            #Starting commands
            embed.add_field(name='Getting started:',value='''`am.start <code>` - host new game in current voice channel. Only one game is allowed in each voice channel. *Code optional*
                                                          \n`am.join` - joins existing game in the voice channel.
                                                          \n`am.joinall` - joins everyone in the voice channel into the game. *Kicks everyone in the game but not in the voice channel*
                                                          \n`am.endgame` - ends the game in the voice channel. ''', inline = False)

            #Host game commands
            embed.add_field(name='Host game commands:',value='''\n`am.round   or 🔇` - mute everyone alive (tasks).
                                                                \n`am.meeting or 📢` - unmutes everyone alive (meeting).
                                                                \n`am.lobby   or ⏮` - restart game (lobby). Sets everyone alive and unmutes all.
                                                                \n`am.dead <@user>` - set someone to dead. Players can do this themselves without the <@user> ''', inline = False)

            #Player game commands
            embed.add_field(name='Player game commands:',value='''`am.dead or ☠` - toggle status to dead: lets you hear everyone during rounds.
                                                                \n`am.leave` - leave game.''', inline = False)

            #Management commands
            embed.add_field(name='Management commands:', value ='''`am.promote <@user>` - promotes player to host. **Host only**
                                                                 \n`am.kick <@user>` - removes player from game.
                                                                 \n`am.update` - resends embed (interface with reactions).
                                                                 \n`am.code <code>` - change the code displayed on the interface.''', inline = False)

            embed.add_field(name='Wiki commands:', value = '''`am.wiki` - link to the official Among Us Fandom Wiki.
                                                            \n`am.map <map>` - image of map with vents, common tasks, and more.
                                                            \n`am.tip <imposter OR crewmate>` - returns random tip for either the imposter or crewmate.''', inline = False)

            embed.add_field(name="Information:", value = '''`am.prefix <prefix>` - change the prefix used to call the bot.
                                                          \n`am.info` - github link and invite link.
                                                          \n`am.vote` - vote to support the bot!''')
        else:
            await ctx.send(page + " is not a valid page. `am.help` for main page, `1` for starting, `2` for all commands.")
            return

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(DefaultCommands(bot))
