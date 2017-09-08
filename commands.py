'''
This module contains all of the !commands that the users
can call upon for execution.
'''

from functions import chat as _chat
from functions import request as _request
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
    except(IndexError, ValueError) as e:
        if isinstance(e, IndexError):
            _chat(sock, "The bartender doesn't know how many drinks you want to buy! Try saying something like: !buydrink <number> <recipient>")
        elif isinstance(e, ValueError):
            _chat(sock, "The bartender looks at you quizzically. Try saying something like !buydrink <number> <recipient>")
        return 0
    viewersRequested = args[3:]
    if len(viewersRequested) == 0:
        viewersToBuyFor = [userName]
        cannotFind = []
    else:
        viewerList = []
        viewersToBuyFor = []
        cannotFind = []
        attempts = 0
        while viewerList is not None:
            viewerList = _getViewerList()
            attempts += 1
            if attempts == 10:
                _chat(sock, "The bartender is busy serving someone else. Try again shortly!")
                return 0
        for viewer in viewersRequested:
            if viewer == 'all':
                viewersToBuyFor = viewerList
                break
            if viewer in viewerList:
                viewersToBuyFor.append(viewer)
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
        _chat(sock, userName + " gives " + str(totalCost) + " " +\
              _cfg.currencyName + " to the barman.")
        viewerDatabase.update(_tdbo.subtract('points', totalCost), \
                              Query().name == userName)
        if viewersRequested[0] == 'all':
            for viewer in viewerList:
                viewerDatabase.update(_tdbo.add('drinks', numberOfDrinks), \
                                      Query().name == viewer)
            _chat(sock, "Drinks for everyone courtesy of " + userName + "!")
        else:
            viewersString = ""
            for viewer in viewersToBuyFor:
                viewerDatabase.update(_tdbo.add('drinks', numberOfDrinks), \
                                      Query().name == viewer)
                if len(viewersToBuyFor) == 0:
                    viewersString += viewer
                elif viewer == viewersToBuyFor[-1]:
                    viewersString += " and " + viewer
                else:
                    viewersString += ", " + viewer
            _chat(sock, userName + " just bought " + viewerString + " " + str(numberOfDrinks) +\
                  " drinks!")


#def drink(args):
#    sock = args[0]
#    userName = args[1]
#    try:
#        numberOfDrinks = int(args[2])



#!buydrink <numDrinks> [ <username0> ( <username1> <username2> ) | "all" ]
#<numDrinks> - The number of drinks to buy at ?? blaskoins per drink.
#<username0>, <username1>, etc - User(s) to buy drink(s) for. May increase the drink counter for each person mentioned by the amount bought.
#"all" - triggers "<numDrinks> Rounds for everyone! Courtesy of [user triggering command]!"
#
#!drink ( <numDrinks> )
#<numDrinks> - Number of drinks to drink. If greater than a number within reason, cancel drink and warn user. Else decrease drinks counter for user by requested amount with message of how much they drank. If omitted, defaults to 0.



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
    streamDataURL = "https://api.twitch.tv/kraken/streams/" + _cfg.JOIN
    streamData = _request(streamDataURL)
    if not streamData['stream']:
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
        currentPoints = viewerDB.search(_Query().name == userName)[0]['totalPoints']
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
            if currentPoints < rankPoints:
                break
        secondsToNextRank = (pointsForNextRank - currentPoints) * int(_cfg.awardDeltaT /\
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
        outputLine = userName + " currently has " + str(currentPoints) + " " +\
                str(currencyUnits) + " and is a" + rankMod + str(currentRank) +\
                " (" + timeToNext + " until next rank!)"
        _chat(sock, outputLine)
    except IndexError:
        _chat(sock, "I'm sorry, " + userName + ", but I don't have any " + _cfg.currencyName +\
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
            if (clipNo > 0) and (clipNo <= len(clipDB)):
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
                " of the machine!"
    elif payout > 1:
        responseLine += " " + str(payout) + " " + _cfg.currencyName + "s clatter out" +\
                " of the machine!"
    viewerDatabase.update(_tdbo.add('points', -10 + payout), _Query().name == userName)
    _chat(sock, responseLine)


# TODO: Create an op-only command !streamrank that parses all streams for this game and outputs our current rank based on viewers.
#       Extension: Run this as a thread and keep it updating in the background to keep track of rank over time
