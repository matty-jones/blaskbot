import cfg
import discord
from discord.ext import commands
import random as R
import psycopg2
import collections
from psycopg2.extras import DictCursor as dictCursor
from datetime import datetime
import numpy as np


commandPrefix = "!"
client = commands.Bot(command_prefix=commandPrefix)
client.change_presence(game=discord.Game(name="with Blasky's stream!"))

@client.command(pass_context=True)
async def bb(context):
    '''Use when you want to be a robot.'''
    await client.say("BEEP BOOP!")

@client.command(pass_context=True)
async def wa(context):
    '''Use when you want to be a pirate.'''
    await client.say("WEIGH ANCHOR!!!")


@client.command(pass_context=True)
async def calc(context):
    '''Use when something was VERY calculated.'''
    await client.say("Calculated. Calculated. Calculated. Calculated. Chat disabled for 1 seconds")


@client.command(pass_context=True)
async def dece(context):
    '''Use when something was proper dece.'''
    await client.say("That was dece, lad!")


@client.command(pass_context=True)
async def clip(context):
    '''Display a random clip for everyone's enjoyment.'''
    connection = psycopg2.connect(database=cfg.JOIN.lower(), user=cfg.NICK.lower())
    cursor = connection.cursor(cursor_factory=dictCursor)
    cursor.execute("SELECT * FROM Clips;")
    clipList = cursor.fetchall()
    clipNo = int(R.randrange(len(clipList)))
    author = clipList[clipNo]['author']
    url = "https://clips.twitch.tv/" + clipList[clipNo]['url']
    connection.close()
    await client.say("Check out this awesome clip from " + author[0].upper() + author[1:] + "! (#" + str(clipNo - 1) + "): " + url)


@client.command(pass_context=True)
async def blaskoins(context):
    '''Check how many blaskoins you have for the stream minigames.'''
    userName = context.message.author.display_name.lower()
    userNameCap = context.message.author.display_name
    connection = psycopg2.connect(database=cfg.JOIN.lower(), user=cfg.NICK.lower())
    cursor = connection.cursor()
    cursor.execute("SELECT Name FROM Viewers WHERE Discord='" + userName.lower() + "';")
    userName = str(cursor.fetchone()[0])
    try:
        cursor.execute("SELECT points FROM Viewers WHERE name='" + userName.lower() + "';")
        currentPoints = int(cursor.fetchone()[0])
        cursor.execute("SELECT totalpoints FROM Viewers WHERE name='" + userName.lower() + "';")
        totalPoints = int(cursor.fetchone()[0])
        currencyUnits = cfg.currencyName
        if currentPoints > 1:
            currencyUnits += "s"
        cursor.execute("SELECT multiplier FROM Viewers WHERE name='" + userName.lower() + "';")
        currentMultiplier = float(cursor.fetchone()[0])
        outputLine = "On your Twitch account, " + userNameCap + ", you currently have " + str(currentPoints) + " " + str(currencyUnits) + "!"
        if currentMultiplier > 1.01:
            outputLine += ", with an active bonus of {:.2%}!".format(currentMultiplier - 1)
        else:
            outputLine += "!"
        await client.say(outputLine)
    except IndexError:
        await client.say("I'm sorry, " + userNameCap + ", but I don't have any " + cfg.currencyName +\
              " data for you yet! Please try again later (and also welcome to the stream ;)).")
    connection.close()


@client.command(pass_context=True)
async def rank(context):
    '''Check to see how long you've watched BlaskatronicTV for.'''
    userName = context.message.author.display_name.lower()
    userNameCap = context.message.author.display_name
    connection = psycopg2.connect(database=cfg.JOIN.lower(), user=cfg.NICK.lower())
    cursor = connection.cursor()
    cursor.execute("SELECT Name FROM Viewers WHERE Discord='" + userName.lower() + "';")
    userName = str(cursor.fetchone()[0])
    try:
        cursor.execute("SELECT totalpoints FROM Viewers WHERE name='" + userName.lower() + "';")
        totalPoints = int(cursor.fetchone()[0])
        cursor.execute("SELECT rank FROM Viewers WHERE name='" + userName.lower() + "';")
        currentRank = str(cursor.fetchone()[0])
        cursor.execute("SELECT multiplier FROM Viewers WHERE name='" + userName.lower() + "';")
        currentMultiplier = float(cursor.fetchone()[0])
        nextRank = None
        pointsForNextRank = None
        for rankPoints in sorted(cfg.ranks.keys()):
            nextRank = cfg.ranks[rankPoints]
            pointsForNextRank = rankPoints
            if totalPoints < rankPoints:
                break
        secondsToNextRank = (pointsForNextRank - totalPoints) * int(cfg.awardDeltaT /\
                                (cfg.pointsToAward * currentMultiplier))
        totalSecondsSoFar = totalPoints * int(cfg.awardDeltaT / cfg.pointsToAward)
        totalMins, totalSecs = divmod(totalSecondsSoFar, 60)
        totalHours, totalMins = divmod(totalMins, 60)
        totalTimeDict = collections.OrderedDict()
        totalTimeDict['hour'] = int(totalHours)
        totalTimeDict['minute'] = int(totalMins)
        totalTimeDict['second'] = int(totalSecs)
        totalTimeArray = []
        mins, secs = divmod(secondsToNextRank, 60)
        hours, mins = divmod(mins, 60)
        timeDict = collections.OrderedDict()
        timeDict['hour'] = int(hours)
        timeDict['minute'] = int(mins)
        timeDict['second'] = int(secs)
        timeArray = []
        for key, value in totalTimeDict.items():
            if value > 1:
                totalTimeArray.append(str(value) + " " + str(key) + "s")
            elif value > 0:
                totalTimeArray.append(str(value) + " " + str(key))
        totalTime = ' and '.join(totalTimeArray[-2:])
        if len(totalTimeArray) == 3:
            totalTime = totalTimeArray[0] + ", " + totalTime
        for key, value in timeDict.items():
            if value > 1:
                timeArray.append(str(value) + " " + str(key) + "s")
            elif value > 0:
                timeArray.append(str(value) + " " + str(key))
        timeToNext = ' and '.join(timeArray[-2:])
        if len(timeArray) == 3:
            timeToNext = timeArray[0] + ", " + timeToNext
        rankMod = ' '
        if currentRank[0] in ['a', 'e', 'i', 'o', 'u']:
            rankMod = 'n '
        outputLine = "On your twitch account, " + userNameCap + ", you have currently watched the stream for " + totalTime +\
                " and are a" + rankMod + str(currentRank) +\
                " (" + timeToNext + " until next rank!)"
        await client.say(outputLine)
    except IndexError:
        await client.say("I'm sorry, " + userNameCap + ", but I don't have any rank" +\
              " data for you yet! Have you checked out the stream yet?")
    connection.close()


@client.command(pass_context=True)
async def drinks(context):
    '''Check how many drinks you have to enjoy on stream.'''
    userName = context.message.author.display_name.lower()
    userNameCap = context.message.author.display_name
    connection = psycopg2.connect(database=cfg.JOIN.lower(), user=cfg.NICK.lower())
    cursor = connection.cursor()
    cursor.execute("SELECT Name FROM Viewers WHERE Discord='" + userName.lower() + "';")
    userName = str(cursor.fetchone()[0])
    cursor.execute("SELECT drinks FROM Viewers WHERE name='" + userName.lower() + "';")
    numberOfDrinks = int(cursor.fetchone()[0])
    if numberOfDrinks == 0:
        await client.say("You don't have any drinks, " + userName + "! Maybe a kind soul will buy you one...")
        return 0
    elif numberOfDrinks == 1:
        drinkString = "1 drink"
    else:
        drinkString = str(numberOfDrinks) + " drinks"
    await client.say("On your twitch account, you have " + drinkString + " to enjoy on stream, " + userNameCap + "!")
    connection.close()


@client.command(pass_context=True)
async def schedule(context):
    '''Use if you've forgotten the schedule.'''
    await client.say("Blaskatronic TV goes live at 2:30am UTC on Wednesdays and Fridays and 5:30pm UTC on Saturdays!")


#@client.command(pass_context=True)
#async def test(context):
#    '''Use if you've forgotten the schedule.'''
#    await client.send_message(discord.Object(id='358106199129980929'), "This is a test")

@client.command(pass_context=True)
async def top(context):
    '''Same as !leaderboard'''
    await leaderboard.callback(context)


@client.command(pass_context=True)
async def leaderboard(context):
    '''See the current leaderboard!'''
    connection = psycopg2.connect(database=cfg.JOIN.lower(), user=cfg.NICK.lower())
    cursor = connection.cursor(cursor_factory=dictCursor)
    cursor.execute("SELECT * FROM Viewers WHERE name NOT IN (" + ', '.join([repr(x) for x in cfg.skipViewers]) + ") ORDER BY totalpoints DESC LIMIT 5;")
    topRanked = cursor.fetchall()
    leaderboardLine = "```------====== MOST MINUTES WATCHED ======----- \n"
    for i, viewerDetails in enumerate(topRanked):
        leaderboardLine += "%1d) %19s %15s %6d \n" % (i + 1, viewerDetails['rank'], viewerDetails['name'], viewerDetails['totalpoints'])
    leaderboardLine = leaderboardLine[:-2] + "```"
    connection.close()
    await client.say(leaderboardLine)


@client.command(pass_context=True)
async def next(context):
    '''Tells you how long until the next stream! Now you have no excuse =P'''
    now = list(map(int, datetime.utcnow().strftime("%H %M").split(' ')))
    today = int(datetime.utcnow().date().weekday())
    nowArray = np.array([today] + now)
    timeDeltaArray = np.array(cfg.streamSchedule) - nowArray
    modulos = [7, 24, 60]
    changed = True
    while changed == True:
        changed = False
        for (x, y), element in np.ndenumerate(timeDeltaArray):
            if element < 0:
                timeDeltaArray[x, y] = element%modulos[y]
                # Decrement the next time level up to reflect this change
                timeDeltaArray[x, y-1] -= 1
                changed = True
    nextStreamTime = timeDeltaArray[timeDeltaArray[:,0].argsort()][0]
    nextStreamDict = collections.OrderedDict()
    nextStreamDict['day'] = int(nextStreamTime[0])
    nextStreamDict['hour'] = int(nextStreamTime[1])
    nextStreamDict['minute'] = int(nextStreamTime[2])
    outputString = "The next scheduled stream starts in "
    nonZeroIndices = [index for index, value in enumerate(nextStreamDict.values()) if value != 0]
    if len(nonZeroIndices) == 1:
        if nonZeroIndices[0] == 2:
            outputString += "just "
        else:
            outputString += "exactly "
    timeStrings = []
    for key, value in nextStreamDict.items():
        if value > 1:
            timeStrings.append(str(value) + " " + str(key) + "s")
        elif value > 0:
            timeStrings.append(str(value) + " " + str(key))
    totalTime = ' and '.join(timeStrings[-2:])
    if len(timeStrings) == 3:
        totalTime = timeStrings[0] + ", " + totalTime
    outputString += totalTime
    await client.say(outputString)


def execute():
    client.run(cfg.DISCORDPASS)


if __name__ == "__main__":
    client.run(cfg.DISCORDPASS)

