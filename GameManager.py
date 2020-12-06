import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')

#LOAD DATABASE
try:
    global conn, c
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    c = conn.cursor()
except:
    print("Failed to connect to database")

games = {}

#Returns game if exists, if not returns false
def gameExist(voiceChannel):
    #Check dictionary
    if voiceChannel in list(games.keys()):
        return games[voiceChannel]
    else:
        return False

def gameRequirements(member, voiceChannel):
    #Check for game
    game = gameExist(voiceChannel)
    if game is False:
        player = False
        return game, player

    player = game.getPlayer(member)
    return game, player

def addGame(game):
    voiceChannel = game.getVoice()
    games[voiceChannel] = game

def endGame(game):
    voiceChannel = game.getVoice()
    del games[voiceChannel]

def secondVC(game, voiceChannel):
    games[voiceChannel] = game

def deleteVC(voiceChannel):
    try:
        del games[voiceChannel]
    except:
        return
