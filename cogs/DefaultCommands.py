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
            description = '**| Pg 1: Quick Start | Pg 2: Game Settings | Pg 3: Other Commands |**'
        )

        embed.set_footer(text = 'Created by Jerry#5922',)

        try:
            pgNum = int(page)
        except:
            pgNum = -1;

        #Quick start (1)
        if page is None or pgNum == 1:
            embed.set_author(name = 'Among Us Manager - Quick Start: | Page 1 / 4')
            embed.add_field(name= '📝 Bot description', value="""This bot uses 'games' in voice channels and an 'interface' message with reactions to manage muting. The muting is done by deafening users.
                                                                \n***Things to know:***
                                                                  **•** Discord rate limits every discord server to 10 voice changes every ~5 seconds. If you missclick and surpass this limit there will be a 5 second throttle until the next voice changes go through.
                                                                \n**•** The bot has a routine restart every 24 hours; if your game is deleted and commands stop working, simply create a new game.""", inline = False)
            embed.add_field(name = '▶️ Start new game', value='''`am.start <code>` - host new game in current voice channel. *Code optional*
                                                                \n`am.joinall` - joins everyone in the voice channel into the game.
                                                                \n`am.startall <code>` - combines start and joinall into one command. *Code optional*''', inline = False)
            embed.add_field(name = '🛠️ Host commands', value='''\n`am.round   or 🔇` - mute everyone alive (tasks).
                                                                \n`am.meeting or 📢` - unmutes everyone alive (meeting).
                                                                \n`am.lobby   or ⏮` - restart game (lobby). Sets everyone alive and unmutes all.''', inline = False)
            embed.add_field(name='🧑 Player commands',value='''`am.dead or ☠` - toggle status to dead.''', inline = False)

        elif pgNum == 2:
            embed.set_author(name = 'Among Us Manager - Game Settings: | Page 2 / 4')
            embed.add_field(name="📝 Game Settings:", value = '''Each game has default settings to deafen on muting, display player vitals, and use reactions to control the muting. However, you can change these settings using `am.settings`. *Channel muting will not mute dead people due to discord rate limits.*''', inline = False)
            embed.add_field(name='⚙️‍ Setting commands:', value ='''`am.settings` - display game settings.''', inline = False)
            embed.add_field(name='🔇 Muting:', value ='''`am.settings deafen` - deafen on muting.
                                                        \n`am.settings mute` - deafen on muting.
                                                        \n`am.settings move` - move channels on muting. You need to set a dead channel for this setting.
                                                        \n`am.channel <channel>` - set dead channel. *Leave <channel> blank to create new channel*''', inline = False)
            embed.add_field(name="🖥️ Interface:", value = '''`am.settings show` - show player vitals.
                                                            \n`am.settings hide` - only show player list.''', inline = False)
            embed.add_field(name="🎮 Controls:", value = '''`am.settings reactions` - use reactions to control muting.
                                                           \n`am.settings host` - bot follows host's personal muting. Automatically changes muting setting to mute.''', inline = False)

        #Additional (3)
        elif pgNum == 3:
            embed.set_author(name = 'Among Us Manager - Other Commands: | Page 3 / 4')
            embed.add_field(name="🛑 Ending commands:", value = '''`am.endgame` - ends the game in the voice channel.
                                                                 \n`am.leave` - leave game.''', inline = False)
            embed.add_field(name='👨‍⚖️ Management commands:', value ='''`am.promote <@user>` - promotes player to host.
                                                                 \n`am.kick <@user>` - removes player from game.
                                                                 \n`am.update` - resend interface.
                                                                 \n`am.code <code>` - change the code.''', inline = False)

            embed.add_field(name='📚 Wiki commands:', value = '''`am.wiki` - link to the Wiki.
                                                            \n`am.map <map>` - detailed map.
                                                            \n`am.controls` - default Among Us keybinds.
                                                            \n`am.tip <imposter OR crewmate>` - returns random tip.''', inline = False)
            embed.add_field(name="Information:", value = '''`am.prefix <prefix>` - change the prefix used to call the bot.
                                                            \n`am.info` - github link and invite link.
                                                            \n`am.vote` - vote to support the bot!''')

        #All commands (4)
        elif pgNum == 4:
            embed.set_author(name = 'Among Us Manager - Full List: | Page 4 / 4')

            #Starting commands
            embed.add_field(name='Getting started:',value='''`am.start <code>` - host new game in current voice channel. Only one game is allowed in each voice channel. *Code optional*
                                                          \n`am.join` - joins existing game in the voice channel.
                                                          \n`am.joinall` - joins everyone in the voice channel into the game. *Kicks everyone in the game but not in the voice channel*
                                                          \n`am.startall <code>` - combines start and joinall into one command. *Code optional*
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
                                                            \n`am.controls` - default Among Us keybinds.
                                                            \n`am.tip <imposter OR crewmate>` - returns random tip for either the imposter or crewmate.''', inline = False)

            embed.add_field(name="Information:", value = '''`am.prefix <prefix>` - change the prefix used to call the bot.
                                                          \n`am.info` - github link and invite link.
                                                          \n`am.vote` - vote to support the bot!''')
        else:
            await ctx.send(page + " is not a valid page. `am.help` for main page, `am.help 2` for additional commands, `am.help 3` for all commands.")
            return

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(DefaultCommands(bot))
