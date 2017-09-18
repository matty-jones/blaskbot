import cfg
import discord
from discord.ext import commands
import random as R
from functions import loadClipsDatabase as getClipsDB
from functions import loadViewersDatabase as getViewersDB
from tinydb import TinyDB, Query

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
    clipDB = getClipsDB()
    clipNo = int(R.randrange(len(clipDB))) + 1
    author = clipDB.get(eid=clipNo)['author']
    url = "https://clips.twitch.tv/" + clipDB.get(eid=clipNo)['url']
    await client.say("Check out this awesome clip from " + author[0].upper() + author[1:] + "! (#" + str(clipNo - 1) + "): " + url)


@client.command(pass_context=True)
async def blaskoins(context):
    '''Check how many blaskoins you have for the stream minigames.'''
    userName = context.message.author.display_name.lower()
    userNameCap = context.message.author.display_name
    viewerDB = getViewersDB()
    discordDB = TinyDB('./databases/discordNames.db')
    twitchUserName = discordDB.search(Query().discordName == userName)
    if len(twitchUserName) > 0:
        userName = twitchUserName[0]['twitchName']
    try:
        currentPoints = viewerDB.search(Query().name == userName)[0]['points']
        totalPoints = viewerDB.search(Query().name == userName)[0]['totalPoints']
        currencyUnits = cfg.currencyName
        if currentPoints > 1:
            currencyUnits += "s"
        currentRank = viewerDB.search(Query().name == userName)[0]['rank']
        currentMultiplier = viewerDB.search(Query().name == userName)[0]['multiplier']
        nextRank = None
        pointsForNextRank = None
        for rankPoints in cfg.ranks.keys():
            nextRank = cfg.ranks[rankPoints]
            pointsForNextRank = rankPoints
            if totalPoints < rankPoints:
                break
        secondsToNextRank = (pointsForNextRank - totalPoints) * int(cfg.awardDeltaT /\
                                (cfg.pointsToAward * currentMultiplier))
        mins, secs = divmod(secondsToNextRank, 60)
        hours, mins = divmod(mins, 60)
        timeDict = {'hour': int(hours), 'minute': int(mins), 'second': int(secs)}
        timeArray = []
        for key, value in timeDict.items():
            if value > 1:
                timeArray.append(str(value) + " " + str(key) + "s")
            elif value > 0:
                timeArray.append(str(value) + " " + str(key))
        timeToNext = ' and '.join(timeArray[-2:])
        if len(timeArray) == 3:
            timeToNext = timeToNext[0] + ", " + timeToNext
        rankMod = ' '
        if currentRank[0] in ['a', 'e', 'i', 'o', 'u']:
            rankMod = 'n '
        outputLine = "On your twitch account, " + userNameCap + ", you currently have " + str(currentPoints) +\
                " " + str(currencyUnits) + "!"
        await client.say(outputLine)
    except IndexError:
        await client.say(sock, "I'm sorry, " + userNameCap + ", but I don't have any " + _cfg.currencyName +\
              " data for you yet! Please try again later (and also welcome to the stream ;)).")


@client.command(pass_context=True)
async def rank(context):
    '''Check to see how long you've watched BlaskatronicTV for.'''
    userName = context.message.author.display_name.lower()
    userNameCap = context.message.author.display_name
    viewerDB = getViewersDB()
    discordDB = TinyDB('./databases/discordNames.db')
    twitchUserName = discordDB.search(Query().discordName == userName)
    if len(twitchUserName) > 0:
        userName = twitchUserName[0]['twitchName']
    try:
        totalPoints = viewerDB.search(Query().name == userName)[0]['totalPoints']
        currentRank = viewerDB.search(Query().name == userName)[0]['rank']
        currentMultiplier = viewerDB.search(Query().name == userName)[0]['multiplier']
        nextRank = None
        pointsForNextRank = None
        for rankPoints in cfg.ranks.keys():
            nextRank = cfg.ranks[rankPoints]
            pointsForNextRank = rankPoints
            if totalPoints < rankPoints:
                break
        secondsToNextRank = (pointsForNextRank - totalPoints) * int(cfg.awardDeltaT /\
                                (cfg.pointsToAward * currentMultiplier))
        totalSecondsSoFar = totalPoints * int(cfg.awardDeltaT / cfg.pointsToAward)
        totalMins, totalSecs = divmod(totalSecondsSoFar, 60)
        totalHours, totalMins = divmod(totalMins, 60)
        totalTimeDict = {'hour': int(totalHours), 'minute': int(totalMins), 'second': int(totalSecs)}
        totalTimeArray = []
        mins, secs = divmod(secondsToNextRank, 60)
        hours, mins = divmod(mins, 60)
        timeDict = {'hour': int(hours), 'minute': int(mins), 'second': int(secs)}
        timeArray = []
        for key, value in totalTimeDict.items():
            if value > 1:
                totalTimeArray.append(str(value) + " " + str(key) + "s")
            elif value > 0:
                totalTimeArray.append(str(value) + " " + str(key))
        totalTime = ' and '.join(totalTimeArray[-2:])
        if len(totalTimeArray) == 3:
            totalTime = totalTime[0] + ", " + totalTime
        for key, value in timeDict.items():
            if value > 1:
                timeArray.append(str(value) + " " + str(key) + "s")
            elif value > 0:
                timeArray.append(str(value) + " " + str(key))
        timeToNext = ' and '.join(timeArray[-2:])
        if len(timeArray) == 3:
            timeToNext = timeToNext[0] + ", " + timeToNext
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

@client.command(pass_context=True)
async def drinks(context):
    '''Check how many drinks you have to enjoy on stream.'''
    userName = context.message.author.display_name.lower()
    userNameCap = context.message.author.display_name
    viewerDatabase = getViewersDB()
    discordDB = TinyDB('./databases/discordNames.db')
    twitchUserName = discordDB.search(Query().discordName == userName)
    if len(twitchUserName) > 0:
        userName = twitchUserName[0]['twitchName']
    numberOfDrinks = int(viewerDatabase.search(Query().name == userName)[0]['drinks'])
    if numberOfDrinks == 0:
        await client.say("You don't have any drinks to use on stream, " + userNameCap + "! Maybe a kind soul will buy you one...")
        return 0
    elif numberOfDrinks == 1:
        drinkString = "1 drink"
    else:
        drinkString = str(numberOfDrinks) + " drinks"
    await client.say("On your twitch account, you have " + drinkString + " to enjoy on stream, " + userNameCap + "!")


@client.command(pass_context=True)
async def schedule(context):
    '''Use if you've forgotten the schedule.'''
    _chat(sock, "Blaskatronic TV goes live at 2:30am UTC on Wednesdays and Fridays and 5:30pm UTC on Saturdays!")


def execute():
    client.run(cfg.DISCORDPASS)


if __name__ == "__main__":
    client.run(cfg.DISCORDPASS)

