import discord
import datetime
import enum
from GameManager import *

class Stage(enum.Enum):
    Lobby = 1
    Round = 2
    Meeting = 3

class Muting(enum.Enum):
    Deafen = 1
    Mute = 2
    Move = 3

class Interface(enum.Enum):
    Show = 1
    Hide = 2

class Controls(enum.Enum):
    Reactions = 1
    Host = 2

class Player:

    def __init__(self, member):
        self.member = member
        self.alive = True

    def __str__(self):
        memberId = self.member.name + '#' + self.member.discriminator
        return memberId

    def setAlive(self, alive):
        self.alive = alive

    def isAlive(self):
        return self.alive

    def getMember(self):
        return self.member


class Game:

    def __init__(self, voiceChannel, textChannel, host, code, mute, interface, control):

        self.voiceChannel = voiceChannel #main voice channel (identifier)
        self.deadVC = None #dead voice channel (moving)
        self.textChannel = textChannel #text channel to send things to
        self.host = Player(host) #player host
        self.stage = Stage.Lobby #stage
        self.players = {str(self.host) : self.host} #player list with players
        self.playerNumber = len(self.players) #number of player
        self.msg = None #last interface sent
        self.timestamp = datetime.datetime.now() #game creation time
        self.code = code #game code in interface
        self.cooldown = False #cooldown on actions

        #Settings
        self.muteSetting = mute
        self.interfaceSetting = interface
        self.controlSetting = control

    def getTime(self):
        return self.timestamp

    def getText(self):
        return self.textChannel

    def getVoice(self):
        return self.voiceChannel

    def setStage(self, stage):
        self.stage = stage

    def getStage(self):
        return self.stage

    def prevMsg(self, msg):
        self.msg = msg

    def getMsg(self):
        return self.msg

    def getHost(self):
        return self.host

    def setHost(self, player):
        self.host = player

    def setCode(self, code):
        self.code = code

    def setText(self, channel):
        self.textChannel = channel

    def setDeadVC(self, channel):
        self.deadVC = channel

    def setCooldown(self, bool):
        self.cooldown = bool

    def setMute(self, muting):
        if muting == "deafen":
            self.muteSetting = Muting.Deafen

        if muting == "mute":
            self.muteSetting = Muting.Mute

        if muting == "move":
            self.muteSetting = Muting.Move

    def setInterface(self, setting):
        if setting == "show":
            self.interfaceSetting = Interface.Show

        if setting == "hide":
            self.interfaceSetting = Interface.Hide

    def setControls(self, setting):
        if setting == "reactions":
            self.controlSetting = Controls.Reactions

        if setting == "host":
            self.controlSetting = Controls.Host

    def getInterface(self):
        self.playerNumber = len(self.players)
        if self.stage == Stage.Lobby:
            emoji = "⏮"
        elif self.stage == Stage.Round:
            emoji = "🔇"
        elif self.stage == Stage.Meeting:
            emoji = "📢"

        embed = discord.Embed(
            colour = discord.Colour.orange(),
            title = "Game Code: " + self.code,
            description = "🔊 **Voice Channel:** " + self.voiceChannel.name +
                   "\n" + "☠ **Dead VC:** " + str(self.deadVC) +
                   "\n" + "👥 **Player Count:** " + str(self.playerNumber) +
                   "\n" + emoji + " **Game stage:** " + self.stage.name,
            timestamp = self.timestamp
        )

        embed.set_footer(text='Host: ' + str(self.host))

        if self.interfaceSetting == Interface.Show:
            #Get all players and their states
            for player in self.players.values():
                if player.isAlive() == True:
                    embed.add_field(name = player, value='`❤ Alive`', inline = False)
                elif player.isAlive() == False:
                    embed.add_field(name = player, value='`☠ Dead`', inline = False)
        else:
            playerList = list(self.players.values())
            players = "`" + str(playerList[0])
            for player in playerList[1:]:
                players = players + ", " + str(player)
            players += "`"

            embed.add_field(name = "Player List", value=players)

        return embed

    def getSettings(self):
        embed = discord.Embed(
            colour = discord.Colour.orange(),

            title = "⚙️ Settings: " + self.voiceChannel.name + " ⚙️",

            description = "🔇 **Muting:** " + self.muteSetting.name +
                   "\n" + "🖥️ **Interface:** " + self.interfaceSetting.name +
                   "\n" + "🎮 **Controls:** " + self.controlSetting.name
        )

        return embed

    def addPlayer(self, member):
        player = Player(member)
        playerList = self.players
        if(len(playerList) >= 10):
            return
        if str(player) not in playerList.keys():
            playerList[str(player)] = player

    #Return false if player is not in the game
    def getPlayer(self, member):
        newPlayer = Player(member)
        playerList = self.players
        if str(newPlayer) in playerList.keys():
            return playerList[str(newPlayer)]
        return False

    def getAllPlayers(self):
        #Returns player type list
        return list(self.players.values())

    def setAllAlive(self):
        playerList = list(self.players.values())
        for player in playerList:
            player.setAlive(True)

    def removePlayer(self, player):
        #Make sure you can't kick host
        if player == self.host:
            return
        del self.players[str(player)]
