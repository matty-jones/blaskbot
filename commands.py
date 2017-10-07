'''
This module contains all of the !commands that the users
can call upon for execution.
'''

from functions import chat as _chat
from functions import queryAPI as _queryAPI
from functions import getXMLAttributes as _getXMLAttributes
from functions import loadViewersDatabase as _getViewersDB
from functions import loadClipsDatabase as _getClipsDB
from functions import isOp as _isOp
from functions import printv as _printv
from functions import getViewerList as _getViewerList
import sys as _sys
import os as _os
import cfg as _cfg
import random as _R
import time as _T
import requests as _requests
from datetime import datetime as _datetime
import re as _re
from html import unescape as _uesc
from tinydb import Query as _Query
import tinydb.operations as _tdbo


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
    viewerDatabase = _getViewersDB()
    currentPoints = viewerDatabase.search(_Query().name == userName)[0]['points']
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
        viewerDatabase.update(_tdbo.subtract('points', totalCost), \
                              _Query().name == userName)
        if viewersToBuyFor == 'all':
            for viewer in viewerList:
                viewerDatabase.update(_tdbo.add('drinks', numberOfDrinks), \
                                      _Query().name == viewer)
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
                viewerDatabase.update(_tdbo.add('drinks', numberOfDrinks), \
                                      _Query().name == viewer)
            if numberOfDrinks == 1:
                drinkString = "a drink"
            else:
                drinkString = str(numberOfDrinks) + " drinks"
            _chat(sock, giveMoneyString + " to buy " + viewersString + " " + drinkString + "!")


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
    viewerDatabase = _getViewersDB()
    totalNumberAllowed = viewerDatabase.search(_Query().name == userName)[0]['drinks']
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
    viewerDatabase.update(_tdbo.subtract('drinks', numberOfDrinks), \
                          _Query().name == userName)


def drinks(args):
    sock = args[0]
    userName = args[1]
    viewerDatabase = _getViewersDB()
    numberOfDrinks = int(viewerDatabase.search(_Query().name == userName)[0]['drinks'])
    if numberOfDrinks == 0:
        _chat(sock, "You don't have any drinks, " + userName + "! Maybe a kind soul will buy you one...")
        return 0
    elif numberOfDrinks == 1:
        drinkString = "1 drink"
    else:
        drinkString = str(numberOfDrinks) + " drinks"
    _chat(sock, "You have " + drinkString + ", " + userName + "!")


def schedule(args):
    sock = args[0]
    _chat(sock, "Blaskatronic TV goes live at 2:30am UTC on Wednesdays and Fridays and 5:30pm UTC on Saturdays!")


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
    VLCLUAURL = "http://127.0.0.1:8080/requests/status.xml"
    try:
        nowPlayingData = _requests.get(VLCLUAURL, auth=('',_cfg.VLCLUAPASS))
        VLCDict = _getXMLAttributes(nowPlayingData.content)
        nowPlayingLine = _uesc(VLCDict['information']['meta']['title']) + " by " +\
                _uesc(VLCDict['information']['meta']['artist'])
        _chat(sock, "We're currently listening to the following song: " + nowPlayingLine)
    except _requests.exceptions.ConnectionError:
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
        componentDict = {'hour': int(components.group(1)),
                         'minute': int(components.group(2)),
                         'second': int(components.group(3))}
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
    viewerDB = _getViewersDB()
    try:
        currentPoints = viewerDB.search(_Query().name == userName)[0]['points']
        totalPoints = viewerDB.search(_Query().name == userName)[0]['totalPoints']
        currencyUnits = _cfg.currencyName
        if currentPoints > 1:
            currencyUnits += "s"
        currentRank = viewerDB.search(_Query().name == userName)[0]['rank']
        currentMultiplier = viewerDB.search(_Query().name == userName)[0]['multiplier']
        nextRank = None
        pointsForNextRank = None
        for rankPoints in _cfg.ranks.keys():
            nextRank = _cfg.ranks[rankPoints]
            pointsForNextRank = rankPoints
            if totalPoints < rankPoints:
                break
        secondsToNextRank = (pointsForNextRank - totalPoints) * int(_cfg.awardDeltaT /\
                                (_cfg.pointsToAward * currentMultiplier))
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
        outputLine = userName + " currently has " + str(currentPoints) + " " + str(currencyUnits) + "!"
        _chat(sock, outputLine)
    except IndexError:
        _chat(sock, "I'm sorry, " + userName + ", but I don't have any " + _cfg.currencyName +\
              " data for you yet! Please try again later (and also welcome to the stream ;)).")


def rank(args):
    sock = args[0]
    userName = args[1]
    viewerDB = _getViewersDB()
    try:
        totalPoints = viewerDB.search(_Query().name == userName)[0]['totalPoints']
        currentRank = viewerDB.search(_Query().name == userName)[0]['rank']
        currentMultiplier = viewerDB.search(_Query().name == userName)[0]['multiplier']
        nextRank = None
        pointsForNextRank = None
        for rankPoints in _cfg.ranks.keys():
            nextRank = _cfg.ranks[rankPoints]
            pointsForNextRank = rankPoints
            if totalPoints < rankPoints:
                break
        secondsToNextRank = (pointsForNextRank - totalPoints) * int(_cfg.awardDeltaT /\
                                (_cfg.pointsToAward * currentMultiplier))
        totalSecondsSoFar = totalPoints * int(_cfg.awardDeltaT / _cfg.pointsToAward)
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
        outputLine = userName + " has currently watched for " + totalTime +\
                " and is a" + rankMod + str(currentRank) +\
                " (" + timeToNext + " until next rank!)"
        _chat(sock, outputLine)
    except IndexError:
        _chat(sock, "I'm sorry, " + userName + ", but I don't have any rank" +\
              " data for you yet! Please try again later (and also welcome to the stream ;)).")



def clip(args):
    sock = args[0]
    additionalArgs = args[1:]
    userName = additionalArgs[0]
    clipDB = _getClipsDB()
    if len(additionalArgs) == 1:
        # Just return a random clip (indexed from 1)
        clipNo = int(_R.randrange(len(clipDB))) + 1
        url = "https://clips.twitch.tv/" + clipDB.get(eid=clipNo)['url']
        author = clipDB.get(eid=clipNo)['author']
        _printv("Clip request: " + url, 4)
        _chat(sock, "Check out this awesome clip (#" + str(clipNo - 1) + "): " + url)
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
                clipsDB.insert({'url': url, 'author': author})
        else:
            _chat(sock, "A moderator will take a look at your clip and " +\
                  "add it to my database if they like it!")
    elif len(additionalArgs) == 2:
        try:
            clipNo = int(additionalArgs[1]) + 1
            if (clipNo > -len(clipDB)) and (clipNo <= len(clipDB)):
                url = "https://clips.twitch.tv/" + clipDB.get(eid=clipNo)['url']
                _printv("Clip request: " + url, 4)
                _chat(sock, "Here is clip #" + str(clipNo - 1) + ": " + url)
            else:
                _chat(sock, "Valid clip #s are 0 to " + str(len(clipDB) - 1) + " inclusive.")
        except ValueError:
            clipFromUser = str(additionalArgs[1])
            userClips = clipDB.search(_Query().author == clipFromUser)
            if len(userClips) > 0:
                clipToShow = _R.choice(userClips)
                url = "https://clips.twitch.tv/" + clipToShow['url']
                _printv("Clip request: " + url, 4)
                _chat(sock, "Check out " + clipFromUser + "'s awesome clip (#" +\
                      str(clipToShow.eid - 1) + "): " + url)
            else:
                _chat(sock, "Sorry, there are no clips from " + clipFromUser + " yet.")
    else:
        _chat(sock, "The correct syntax is !clip, !clip #, or !clip <NAME>.")


def pay(args):
    sock = args[0]
    userName = args[1]
    viewerDatabase = _getViewersDB()
    try:
        userToPay = args[2]
        amountToPay = int(args[3])
        if amountToPay < 0:
            raise IndexError
        viewerJSON = _getViewerList()
        viewerList = [viewerName for nameRank in [viewerJSON['chatters'][x] \
                                    for x in viewerJSON['chatters'].keys()] for viewerName \
                                    in nameRank]
        if userToPay not in viewerList:
            _chat(sock, "I don't see " + userToPay + " in chat!")
            return 0
        viewerDatabase.update(_tdbo.add('points', amountToPay), _Query().name == userToPay)
        viewerDatabase.update(_tdbo.subtract('points', amountToPay), _Query().name == userName)
        payString = userName + " very kindly gives " + userToPay + " " + str(amountToPay) + " of" +\
             " their " + _cfg.currencyName + "s"
        _chat(sock, payString + "!")
    except:
        _chat(sock, "The correct syntax: !pay <USERNAME> <AMOUNT>. There are no defaults!")


def slot(args):
    sock = args[0]
    userName = args[1]
    viewerDatabase = _getViewersDB()
    currentPoints = viewerDatabase.search(_Query().name == userName)[0]['points']
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
    viewerDatabase.update(_tdbo.subtract('points', 10), _Query().name == userName)
    viewerDatabase.update(_tdbo.add('points', payout), _Query().name == userName)
    _printv("Username = " + userName + ", Result = " + responseLine + ", Winnings = " + str(payout), 1)
    _chat(sock, responseLine)
