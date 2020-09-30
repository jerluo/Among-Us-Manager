import discord
import datetime
import enum

class Stage(enum.Enum):
    Lobby = 1
    Round = 2
    Meeting = 3

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

    def __init__(self, voiceChannel, textChannel, host):
        self.voiceChannel = voiceChannel
        self.textChannel = textChannel
        self.host = Player(host)
        self.stage = Stage.Lobby
        self.players = {str(self.host) : self.host}
        self.msg = None
        self.timestamp = datetime.datetime.now()

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

    def getInterface(self):
        embed = discord.Embed(
            colour = discord.Colour.orange(),
            title = 'Among Us Manager',
            description = "**Voice Channel:** " + self.voiceChannel.name + "\n" +  "**Game stage:** " + self.stage.name + "\n",
            timestamp = self.timestamp
        )

        embed.set_footer(text='Host: ' + str(self.host))

        #Get all players and their states

        for player in self.players.values():
            if player.isAlive() == True:
                embed.add_field(name = player, value='`❤ Alive`', inline = False)
            elif player.isAlive() == False:
                embed.add_field(name = player, value='`☠ Dead`', inline = False)

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
        return self.players.values()

    def setAllAlive(self):
        playerList = self.players.values()
        for player in playerList:
            player.setAlive(True)

    def removePlayer(self, player):
        del self.players[str(player)]
