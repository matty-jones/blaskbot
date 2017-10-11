import cfg
import discord
from discord.ext import commands
import random as R
import psycopg2

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
    cursor = connection.cursor(cursor_factory=_dictCursor)
    cursor.execute("SELECT * FROM Clips;")
    clipList = cursor.fetchall()
    clipNo = int(_R.randrange(len(clipList)))
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


@client.command(pass_context=True)
async def test(context):
    '''Use if you've forgotten the schedule.'''
    await client.send_message(discord.Object(id='358106199129980929'), "This is a test")


def execute():
    client.run(cfg.DISCORDPASS)


if __name__ == "__main__":
    client.run(cfg.DISCORDPASS)

