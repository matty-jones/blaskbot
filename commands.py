'''
This module contains all of the !commands that the users
can call upon for execution.
'''

from functions import chat as _chat
from functions import queryAPI as _queryAPI
from functions import getXMLAttributes as _getXMLAttributes
from functions import isOp as _isOp
from functions import printv as _printv
from functions import getViewerList as _getViewerList
from functions import streamIsUp as _streamIsUp
import sys as _sys
import os as _os
import cfg as _cfg
import random as _R
import time as _T
import requests as _requests
from datetime import datetime as _datetime
import re as _re
from html import unescape as _uesc
import psycopg2
from psycopg2.extras import DictCursor as _dictCursor
import collections as _collections
import numpy as _np


def time(args):
    sock = args[0]
    # TODO: Get rid of time and replace it with datetime instead
    _chat(sock, "At Blaskatronic HQ, it is currently " + _T.strftime("%I:%M %p %Z on %A, %B, %d, %Y."))


def bb(args):
    sock = args[0]
    _chat(sock, "BEEP BOOP")


def wa(args):
    sock = args[0]
    _chat(sock, "WEIGH ANCHOR!!!")


def calc(args):
    sock = args[0]
    _chat(sock, "Calculated. Calculated. Calculated. Calculated. Chat disabled for 1 seconds")


def dece(args):
    sock = args[0]
    _chat(sock, "That was dece, lad!")


def discord(args):
    sock = args[0]
    _chat(sock, "Chat to us on Discord at: www.discord.me/blaskatronic")


def roll(args):
    sock = args[0]
    try:
        dsides = int(args[2])
        rollNumber = _R.randint(1, dsides)
        rollString = "I rolled a D" + str(dsides)
        if dsides > 20:
            rollString += " (it was a REALLY big one)"
        rollString += ", and got " + str(rollNumber) + "."
        _chat(sock, rollString)
    except (IndexError, ValueError) as e:
        if isinstance(e, IndexError):
            _chat(sock, "I don't know what to roll! Try specifying a die using something like: !roll 20")
        elif isinstance(e, ValueError):
            _chat(sock, "Pfff, it makes no sense to roll that. I'm not doing it.")


def buydrink(args):
    sock = args[0]
    userName = args[1]
    connection = psycopg2.connect(database=_cfg.JOIN.lower(), user=_cfg.NICK.lower())
    cursor = connection.cursor()
    cursor.execute("SELECT points FROM Viewers WHERE name='" + userName.lower() + "';")
    currentPoints = int(cursor.fetchone()[0])
    try:
        numberOfDrinks = int(args[2])
        viewersRequested = args[3:]
        if numberOfDrinks <= 0:
            raise IndexError
    except(IndexError, ValueError) as e:
        _chat(sock, "The bartender doesn't know how many drinks you want to buy, but begins pouring you a drink anyway.")
        numberOfDrinks = 1
        viewersRequested = args[2:]
    viewerList = []
    attempts = 0
    while len(viewerList) == 0:
        viewerJSON = _getViewerList()
        viewerList = [viewerName for nameRank in [viewerJSON['chatters'][x] \
                                    for x in viewerJSON['chatters'].keys()] for viewerName \
                                    in nameRank]
        attempts += 1
        if attempts == 10:
            _chat(sock, "The bartender is busy serving someone else. Try again shortly!")
            return 0
    if 'all' in viewersRequested:
        viewersToBuyFor = viewerList
    else:
        if len(viewersRequested) == 0:
            viewersRequested = [userName]
        viewersToBuyFor = []
        cannotFind = []
        for viewer in viewersRequested: # Put in a .lower here?
            if viewer.lower() in viewerList:
                viewersToBuyFor.append(viewer.lower())
            else:
                cannotFind.append(viewer)
        if len(cannotFind) == 1:
            _chat(sock, "The bartender looks around but cannot see " +\
                 cannotFind[0] + "!")
        elif len(cannotFind) == len(viewersToBuyFor):
            _chat(sock, "The bartender looks around but cannot see " +\
                 "any of the people you'd like to buy drinks for!")
            return 0
        elif len(cannotFind) == 2:
            _chat(sock, "The bartender looks around but cannot see " +\
                 cannotFind[0] + " or " + cannotFind[1] + "!")
        elif len(cannotFind) > 2:
            _chat(sock, "The bartender looks around but cannot see " +\
                  ", ".join(cannotFind[:-1]) + ", or " + cannotFind[-1] + "!")
    if len(viewersToBuyFor) == 0:
        return 0
    totalCost = numberOfDrinks * (len(viewersToBuyFor) * _cfg.drinksCost)
    if currentPoints < totalCost:
        _chat(sock, "Sorry, " + userName + ", but you do not have " + str(totalCost) + " " + _cfg.currencyName + "s to buy that many drinks!")
    else:
        giveMoneyString = userName + " gives " + str(totalCost) + " " +\
              _cfg.currencyName + "s to the bartender"
        cursor.execute("UPDATE Viewers SET points=points - " + str(totalCost) + " WHERE name='" + userName.lower() + "';")
        if viewersToBuyFor == 'all':
            for viewer in viewerList:
                cursor.execute("UPDATE Viewers SET drinks=drinks + " + str(numberOfDrinks) + " WHERE name='" + viewer.lower() + "';")
            _chat(sock, giveMoneyString + ". Drinks for everyone!")
        else:
            viewersString = viewersToBuyFor[0]
            if len(viewersToBuyFor) > 1:
                for viewer in viewersToBuyFor[1:]:
                    if viewer == viewersToBuyFor[-1]:
                        viewersString += " and " + viewer
                    else:
                        viewersString += ", " + viewer
            viewersString = _re.sub(r'\b' + userName + r'\b', 'themselves', viewersString)
            for viewer in viewersToBuyFor:
                cursor.execute("UPDATE Viewers SET drinks=drinks + " + str(numberOfDrinks) + " WHERE name='" + viewer.lower() + "';")
            if numberOfDrinks == 1:
                drinkString = "a drink"
            else:
                drinkString = str(numberOfDrinks) + " drinks"
            _chat(sock, giveMoneyString + " to buy " + viewersString + " " + drinkString + "!")
    connection.commit()
    connection.close()


def drink(args):
    sock = args[0]
    userName = args[1]
    try:
        numberOfDrinks = int(args[2])
        if numberOfDrinks <= 0:
            _chat(sock, userName + " takes a deep breath and decides not to drink anything.")
            return 0
    except (IndexError, ValueError) as e:
        if isinstance(e, IndexError):
            numberOfDrinks = 1
        elif isinstance(e, ValueError):
            _chat(sock, "You can't drink that!")
            return 0
    if numberOfDrinks > 5:
        _chat(sock, "That's way too many drinks to have all at once! You'll be chundering " +\
             "everywhere!")
        return 0
    connection = psycopg2.connect(database=_cfg.JOIN.lower(), user=_cfg.NICK.lower())
    cursor = connection.cursor()
    cursor.execute("SELECT drinks FROM Viewers WHERE name='" + userName.lower() + "';")
    totalNumberAllowed = int(cursor.fetchone()[0])
    if totalNumberAllowed == 0:
        _chat(sock, "You don't have any drinks, " + userName + "! Maybe a kind soul will buy you one...")
        return 0
    if numberOfDrinks > totalNumberAllowed:
        if totalNumberAllowed == 1:
            allowed = "1 drink"
        else:
            allowed = str(totalNumberAllowed) + " drinks"
        _chat(sock, "You only have " + allowed + " drink in front of you, " + userName + "!")
        return 0
    drinkString = userName + " takes a deep breath and then downs a drink"
    if numberOfDrinks > 1:
        drinkString += "...or " + str(numberOfDrinks) + "! It doesn't do anything yet except make you feel woozy..."
    else:
        drinkString += "! It doesn't do anything yet except make you feel woozy..."
    _chat(sock, drinkString)
    cursor.execute("UPDATE Viewers SET drinks=drinks - " + str(numberOfDrinks) + " WHERE name='" + userName.lower() + "';")
    connection.commit()
    connection.close()


def drinks(args):
    sock = args[0]
    userName = args[1]
    connection = psycopg2.connect(database=_cfg.JOIN.lower(), user=_cfg.NICK.lower())
    cursor = connection.cursor()
    cursor.execute("SELECT drinks FROM Viewers WHERE name='" + userName.lower() + "';")
    numberOfDrinks = int(cursor.fetchone()[0])
    if numberOfDrinks == 0:
        _chat(sock, "You don't have any drinks, " + userName + "! Maybe a kind soul will buy you one...")
        return 0
    elif numberOfDrinks == 1:
        drinkString = "1 drink"
    else:
        drinkString = str(numberOfDrinks) + " drinks"
    _chat(sock, "You have " + drinkString + ", " + userName + "!")
    connection.close()


def schedule(args):
    sock = args[0]
    _chat(sock, "Blaskatronic TV goes live at 2:30am UTC on Wednesdays and Fridays and 5:30pm UTC on Saturdays!")


def commands(args):
    help(args)


def help(args):
    sock = args[0]
    username = args[1]
    commandsList = sorted([o for o in dir(_sys.modules[__name__])
            if o[0] != '_'])
    if username not in _cfg.opList:
        for command in _cfg.opOnlyCommands:
            commandsList.remove(command)
    commandString = ""
    _chat(sock, username + " can access the following commands: " +
            ', '.join(['!' + command for command in commandsList]) +
            '.')


def subscribe(args):
    sock = args[0]
    fileName = './Subscribe.txt'
    with open(fileName, 'r') as subFile:
        lines = subFile.readlines()
        lineToDisplay = None
        while True:
            lineToDisplay = _R.choice(lines)
            if lineToDisplay[0] == '#':
                continue
            break
        _chat(sock, lineToDisplay[:-1])


def nowplaying(args):
    sock = args[0]
    VLCLUAURL = "http://" + _cfg.EXTERNALIP + ":8080/requests/status.xml"
    #VLCLUAURL = "http://127.0.0.1:8080/requests/status.xml"
    try:
        nowPlayingData = _requests.get(VLCLUAURL, auth=('',_cfg.VLCLUAPASS))
        VLCDict = _getXMLAttributes(nowPlayingData.content)
        nowPlayingLine = _uesc(VLCDict['information']['meta']['title']) + " by " +\
                _uesc(VLCDict['information']['meta']['artist'])
        _chat(sock, "We're currently listening to the following song: " + nowPlayingLine)
        _printv(nowPlayingLine, 1)
    except:
        _chat(sock, "I can't read the now playing data right now! Sorry!")


def twitter(args):
    sock = args[0]
    if "<YOUR TWITTER USERNAME HERE>" not in str(_cfg.twitterUsername):
        latestTweetURL = "https://decapi.me/twitter/latest.php?name=" +\
                        str(_cfg.twitterUsername)
        tweetHandle = _requests.get(latestTweetURL)
        latestTweet = tweetHandle.text
        _chat(sock, "Latest tweet from " + str(_cfg.twitterUsername) +
                ": " + latestTweet)


def uptime(args):
    sock = args[0]
    streamData = _queryAPI("https://api.twitch.tv/kraken/streams/" + _cfg.JOIN)
    if (streamData is None) or (not streamData['stream']):
        _chat(sock, "The stream isn't online, or the Twitch API hasn't" +\
              " been updated yet!")
    else:
        createdTime = _datetime.strptime(streamData['stream']['created_at'],
                                         "%Y-%m-%dT%H:%M:%SZ")
        currentTime = _datetime.utcnow()
        deltaTime = str(currentTime - createdTime)
        components = _re.match(r"(.*)\:(.*)\:(.*)\.(.*)", deltaTime)
        componentDict = _collections.OrderedDict()
        componentDict['hour'] = int(components.group(1))
        componentDict['minute'] = int(components.group(2))
        componentDict['second'] = int(components.group(3))
        upArray = []
        for key, value in componentDict.items():
            if value > 1:
                upArray.append(str(value) + " " + str(key) + "s")
            elif value > 0:
                upArray.append(str(value) + " " + str(key))
        uptime = ' and '.join(upArray[-2:])
        if len(upArray) == 3:
            uptime = upArray[0] + ", " + uptime
        _chat(sock, "The stream has been live for: " + uptime + "!")


def blaskoins(args):
    sock = args[0]
    userName = args[1]
    connection = psycopg2.connect(database=_cfg.JOIN.lower(), user=_cfg.NICK.lower())
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT points FROM Viewers WHERE name='" + userName.lower() + "';")
        currentPoints = int(cursor.fetchone()[0])
        cursor.execute("SELECT totalpoints FROM Viewers WHERE name='" + userName.lower() + "';")
        totalPoints = int(cursor.fetchone()[0])
        currencyUnits = _cfg.currencyName
        if currentPoints > 1:
            currencyUnits += "s"
        cursor.execute("SELECT multiplier FROM Viewers WHERE name='" + userName.lower() + "';")
        currentMultiplier = float(cursor.fetchone()[0])
        outputLine = userName + " currently has " + str(currentPoints) + " " + str(currencyUnits)
        if currentMultiplier > 1.01:
            outputLine += ", with an active bonus of {:.2%}!".format(currentMultiplier - 1)
        else:
            outputLine += "!"
        _chat(sock, outputLine)
    except (IndexError, TypeError):
        _chat(sock, "I'm sorry, " + userName + ", but I don't have any " + _cfg.currencyName +\
              " data for you yet! Please try again later (and also welcome to the stream ;)).")
    connection.close()


def rank(args):
    sock = args[0]
    userName = args[1]
    connection = psycopg2.connect(database=_cfg.JOIN.lower(), user=_cfg.NICK.lower())
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT totalpoints FROM Viewers WHERE name='" + userName.lower() + "';")
        totalPoints = int(cursor.fetchone()[0])
        cursor.execute("SELECT rank FROM Viewers WHERE name='" + userName.lower() + "';")
        currentRank = str(cursor.fetchone()[0])
        cursor.execute("SELECT multiplier FROM Viewers WHERE name='" + userName.lower() + "';")
        currentMultiplier = float(cursor.fetchone()[0])
        nextRank = None
        pointsForNextRank = None
        for rankPoints in sorted(_cfg.ranks.keys()):
            nextRank = _cfg.ranks[rankPoints]
            pointsForNextRank = rankPoints
            if totalPoints < rankPoints:
                break
        secondsToNextRank = (pointsForNextRank - totalPoints) * int(_cfg.awardDeltaT /\
                                (_cfg.pointsToAward * currentMultiplier))
        totalSecondsSoFar = totalPoints * int(_cfg.awardDeltaT / _cfg.pointsToAward)
        totalMins, totalSecs = divmod(totalSecondsSoFar, 60)
        totalHours, totalMins = divmod(totalMins, 60)
        totalTimeDict = _collections.OrderedDict()
        totalTimeDict['hour'] = int(totalHours)
        totalTimeDict['minute'] = int(totalMins)
        totalTimeDict['second'] = int(totalSecs)
        totalTimeArray = []
        mins, secs = divmod(secondsToNextRank, 60)
        hours, mins = divmod(mins, 60)
        timeDict = _collections.OrderedDict()
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
        outputLine = userName + " has currently watched for " + totalTime +\
                " and is a" + rankMod + str(currentRank) +\
                " (" + timeToNext + " until next rank!)"
        _chat(sock, outputLine)
    except (IndexError, TypeError):
        _chat(sock, "I'm sorry, " + userName + ", but I don't have any rank" +\
              " data for you yet! Please try again later (and also welcome to the stream ;)).")
    connection.close()


def clip(args):
    sock = args[0]
    additionalArgs = args[1:]
    userName = additionalArgs[0]
    connection = psycopg2.connect(database=_cfg.JOIN.lower(), user=_cfg.NICK.lower())
    cursor = connection.cursor(cursor_factory=_dictCursor)
    cursor.execute("SELECT * FROM Clips;")
    clipList = cursor.fetchall()
    if len(additionalArgs) == 1:
        # Just return a random clip
        clipNo = int(_R.randrange(len(clipList)))
        url = "https://clips.twitch.tv/" + clipList[clipNo]['url']
        author = clipList[clipNo]['author']
        _printv("Clip request: " + url, 4)
        _chat(sock, "Check out this awesome clip (#" + str(clipNo) + "): " + url)
    elif additionalArgs[1] == 'add':
        if userName is _isOp():
            try:
                url = additionalArgs[2]
                author = additionalArgs[3]
                if len(author) > len(url):
                    raise IndexError
            except IndexError:
                _chat(sock, "The correct syntax is !clip add <CLIP SLUG> <AUTHOR>.")
            else:
                cursor.execute("INSERT INTO Clips VALUES (%s, %s);", (url, author))
                connection.commit()
        else:
            _chat(sock, "A moderator will take a look at your clip and " +\
                  "add it to my database if they like it!")
    elif len(additionalArgs) == 2:
        try:
            clipNo = int(additionalArgs[1])
            if (clipNo > -len(clipList)) and (clipNo <= len(clipList)):
                url = "https://clips.twitch.tv/" + clipList[clipNo]['url']
                _printv("Clip request: " + url, 4)
                _chat(sock, "Here is clip #" + str(clipNo) + ": " + url)
            else:
                _chat(sock, "Valid clip #s are 0 to " + str(len(clipList) - 1) + " inclusive.")
        except ValueError:
            # Username specified instead
            clipFromUser = str(additionalArgs[1])
            cursor.execute("SELECT * FROM Clips WHERE author='" + clipFromUser + "';")
            userClips = cursor.fetchall()
            userClips = clipDB.search(_Query().author == clipFromUser)
            if len(userClips) > 0:
                clipToShow = _R.choice(userClips)
                url = "https://clips.twitch.tv/" + clipToShow['url']
                _printv("Clip request: " + url, 4)
                _chat(sock, "Check out " + clipFromUser + "'s awesome clip (#" +\
                      str(clipToShow['id'] - 1) + "): " + url)
            else:
                _chat(sock, "Sorry, there are no clips from " + clipFromUser + " yet.")
    else:
        _chat(sock, "The correct syntax is !clip, !clip #, or !clip <NAME>.")
    connection.close()


def pay(args):
    sock = args[0]
    userName = args[1]
    connection = psycopg2.connect(database=_cfg.JOIN.lower(), user=_cfg.NICK.lower())
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT points FROM Viewers WHERE name='" + userName.lower() + "';")
        coinsAvailable = int(cursor.fetchone()[0])
        userToPay = args[2].lower()
        amountToPay = int(args[3])
        if amountToPay < 0:
            raise IndexError
        if amountToPay > coinsAvailable:
            errorString = "You only have", coinsAvailable, _cfg.currencyName
            if coinsAvailable > 1:
                errorString += "s"
            errorString += " available, " + userName + "!"
            _chat(sock, errorString)
        viewerJSON = _getViewerList()
        viewerList = [viewerName for nameRank in [viewerJSON['chatters'][x] \
                                    for x in viewerJSON['chatters'].keys()] for viewerName \
                                    in nameRank]
        if userToPay not in viewerList:
            _chat(sock, "I don't see " + userToPay + " in chat!")
            return 0
        cursor.execute("UPDATE Viewers SET points=points + " + str(amountToPay) + " WHERE name='" + userToPay.lower() + "';")
        cursor.execute("UPDATE Viewers SET points=points - " + str(amountToPay) + " WHERE name='" + userName.lower() + "';")
        payString = userName + " very kindly gives " + userToPay + " " + str(amountToPay) + " of" +\
             " their " + _cfg.currencyName + "s"
        _chat(sock, payString + "!")
    except:
        _chat(sock, "The correct syntax: !pay <USERNAME> <AMOUNT>. There are no defaults!")
    connection.commit()
    connection.close()


def slot(args):
    sock = args[0]
    userName = args[1]
    if len(args) > 2:
        return
    streamStatus = _streamIsUp()
    if streamStatus is not None:
        if streamStatus is False:
            _chat(sock, "Sorry, " + userName + ", but you can't win anything off stream! Try using !next to see when you can next play with the slot machine!")
            return
    connection = psycopg2.connect(database=_cfg.JOIN.lower(), user=_cfg.NICK.lower())
    cursor = connection.cursor()
    cursor.execute("SELECT points FROM Viewers WHERE name='" + userName.lower() + "';")
    currentPoints = int(cursor.fetchone()[0])
    if currentPoints < _cfg.slotCost:
        _chat(sock, "Sorry, " + userName + ", but you do not have enough" + _cfg.currencyName +\
              " to play! You need at least " + str(_cfg.slotCost) + ".")
        return 0
    _chat(sock, "You insert " + str(_cfg.slotCost) + " " + _cfg.currencyName +\
          "s and pull the slot machine arm...")
    with open('./slotWin.txt', 'r') as winFile:
        winLines = winFile.readlines()
    with open('./slotLose.txt', 'r') as loseFile:
        loseLines = loseFile.readlines()
    results = []
    for i in range(_cfg.slotNReels):
        results.append(_R.choice(_cfg.slotStops))
    _chat(sock, "| " + " | ".join([x for x in results]) + " |")
    responseLine = _R.choice(winLines)[:-1]
    if (len(list(set(results))) == _cfg.slotNReels) and (results != _cfg.slotJackpot):
        # None are matching
        responseLine = _R.choice(loseLines)[:-1]
        payout = _cfg.slotPayout[0]
    elif len(list(set(results))) == 3:
        # Exactly 2 are matching
        responseLine += " A pair!"
        payout = _cfg.slotPayout[2]
    elif len(list(set(results))) == 2:
        # Could be 2x2 or exactly 3 matching
        if results.count(list(set(results))[0]) == 2:
            # 2x2 are matching
            responseLine += " Two pairs!"
            payout = _cfg.slotPayout[1]
        else:
            # 3 are matching
            responseLine += " Trips!"
            payout = _cfg.slotPayout[3]
    elif len(list(set(results))) == 1:
        # All 4 match
        responseLine += " 4-of-a-kind!"
        payout = _cfg.slotPayout[4]
    elif results == _cfg.slotJackpot:
        responseLine = "YOU HAVE WON THE JACKPOT!"
        payout = 0
        # TODO Add the game keys to the database
    if payout == 1:
        responseLine += " A single" + _cfg.currencyName + " clatters out" +\
                " of the machine for " + userName + "!"
    elif payout > 1:
        responseLine += " " + str(payout) + " " + _cfg.currencyName + "s clatter out" +\
                " of the machine for " + userName + "!"
    cursor.execute("UPDATE Viewers SET points=points - " + str(_cfg.slotCost) + " WHERE name='" + userName.lower() + "';")
    cursor.execute("UPDATE Viewers SET points=points + " + str(payout) + " WHERE name='" + userName.lower() + "';")
    _printv("Username = " + userName + "," + responseLine + ", Winnings = " + str(payout), 1)
    _chat(sock, responseLine)
    connection.commit()
    connection.close()


def leaderboard(args):
    sock = args[0]
    userName = args[1]
    connection = psycopg2.connect(database=_cfg.JOIN.lower(), user=_cfg.NICK.lower())
    cursor = connection.cursor(cursor_factory=_dictCursor)
    cursor.execute("SELECT * FROM Viewers WHERE name NOT IN (" + ', '.join([repr(x) for x in _cfg.skipViewers]) + ") ORDER BY totalpoints DESC LIMIT 5;")
    topRanked = cursor.fetchall()
    leaderboardLine = "--== MOST MINUTES WATCHED ==-- "
    for i, viewerDetails in enumerate(topRanked):
        leaderboardLine += " %1d) %15s %15s, %5d | " % (i + 1, viewerDetails['rank'], viewerDetails['name'], viewerDetails['totalpoints'])
    _chat(sock, leaderboardLine[:-3])
    connection.close()


def top(args):
    leaderboard(args)


def next(args):
    sock = args[0]
    userName = args[1]
    if _cfg.streamScheduleOverride is not None:
        _chat(sock, _cfg.streamScheduleOverride)
        return
    now = list(map(int, _datetime.utcnow().strftime("%H %M").split(' ')))
    today = int(_datetime.utcnow().date().weekday())
    nowArray = _np.array([today] + now)
    timeDeltaArray = _np.array(_cfg.streamSchedule) - nowArray
    modulos = [7, 24, 60]
    changed = True
    while changed == True:
        changed = False
        for (x, y), element in _np.ndenumerate(timeDeltaArray):
            if element < 0:
                timeDeltaArray[x, y] = element%modulos[y]
                # Decrement the next time level up to reflect this change
                timeDeltaArray[x, y-1] -= 1
                changed = True
    nextStreamTime = timeDeltaArray[timeDeltaArray[:,0].argsort()][0]
    nextStreamDict = _collections.OrderedDict()
    nextStreamDict['day'] = int(nextStreamTime[0])
    nextStreamDict['hour'] = int(nextStreamTime[1])
    nextStreamDict['minute'] = int(nextStreamTime[2])
    outputString = "The next scheduled stream starts"
    nonZeroIndices = [index for index, value in enumerate(nextStreamDict.values()) if value != 0]
    if len(nonZeroIndices) == 0:
        outputString += " right the hell now!"
    elif len(nonZeroIndices) == 1:
        if nonZeroIndices[0] == 2:
            outputString += " in just "
        else:
            outputString += " in exactly "
    else:
        outputString += " in "
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
    if len(_cfg.streamScheduleAdditional) > 0:
        outputString += " " + _cfg.streamScheduleAdditional
    _chat(sock, outputString)
