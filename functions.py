'''
This is the main functions module that contains everything
we need for BlaskBot to be the most amazing thing the universe
has ever seen.

BEEP BOOP!
'''

import cfg
import requests
import time as T
import os
import sys
import socket
from tinydb import TinyDB, Query
import tinydb.operations as tdbo
from multiprocessing import Value
import xml.etree.ElementTree as ET

defaultHeader = {"Authorization":'OAuth ' + str(cfg.PASS).split(':')[1]}
# This is a global variable, but needs to be shared between timer subprocesses
# (read only, not modify) so use mp.Value()
numberOfChatMessages = Value('d', 0)

class URLError(Exception):
    pass


# ---=== HELPER FUNCTIONS ===---

def printv(msg, v):
    '''
    A custom print function that considers the set verbosity
    level before output
    Inputs:
        msg -- (str) The message
        v -- (int) The verbosity level of the message
    '''
    if cfg.VERB >= v:
        print(msg)

# ---========================---


# ---=== IRC FUNCTIONS ===---

def getSocket(nick, auth, channel):
    sock = socket.socket()
    sock.connect((cfg.HOST, cfg.PORT))
    sock.send("PASS {}\r\n".format(auth).encode("utf-8"))
    sock.send("NICK {}\r\n".format(nick).encode("utf-8"))
    sock.send("JOIN #{}\r\n".format(channel).encode("utf-8"))
    return sock


def hostChat(hostSock, stdin):
    sys.stdin = stdin
    while True:
        message = input("Send as " + cfg.JOIN + ": ")
        chat(hostSock, message, sendType='host')


def chat(sock, msg, sendType='bot'):
    '''
    Sends a chat message to the server.
    Inputs:
        sock -- The socket over which to send the message
        msg -- (str) The message to send
    '''
    command = False
    if sendType == 'bot':
        msg = "/me : " + msg
    else:
        if msg[0] == "!":
            command = True
    printv(sendType + ": " + msg, 1)
    try:
        sock.send("PRIVMSG #{} :{}\r\n".format(cfg.JOIN, msg).encode('utf-8'))
        if command is True:
            commandName = msg.split(' ')[0][1:]
            # THIS DOESN'T WORK YET, FIX IT
            exec("from commands import " + commandName + " as tempCommand")
            tempCommand([sock, cfg.JOIN])
    except:
        printv("ERROR MESSAGE NOT SENT", 1)


def ban(sock, user):
    '''
    Bans a user from the channel
    Inputs:
        sock -- The socket over which to send the message
        user -- (str) The name of the user to ban
    '''
    printv("Banning user '" + user + "'..." , 4)
    chat(sock, ".ban {}".format(user))


def unban(sock, user):
    '''
    Unbans/untimeouts a user from the channel
    Inputs:
        sock -- The socket over which to send the message
        user -- (str) The name of the user to ban
    '''
    printv("Unbanning user '" + user + "'..." , 4)
    chat(sock, ".unban {}".format(user))


def timeout(sock, user, time=600):
    '''
    Times a user out from the channel
    Inputs:
        sock -- The socket over which to send the message
        user -- (str) The name of the user to timeout
        time -- (int) The length of the timeout in seconds
                      (default 600)
    '''
    printv("Timing out user '" + user + "' for " + str(time) +
           " seconds..." , 4)
    chat(sock, ".timeout {}".format(user, seconds))

# ---=====================---

def threadFillOpList():
    '''
    In a separate thread, get the channel moderator list and
    keep it updated
    '''
    while True:
        viewerList = getViewerList()
        if viewerList is not None:
            VIPs = ["moderators", "staff", "admins", "global_mods"]
            for VIPType in VIPs:
                for viewer in viewerList["chatters"][VIPType]:
                    if viewer not in cfg.opList:
                        printv("Adding " + viewer + " with VIPType " +
                                VIPType + " to opList...", 4)
                        cfg.opList.append(viewer)
        T.sleep(5)


def threadUpdateDatabase(sock):
    printv("Loading the viewer database...", 5)
    viewerDatabase = loadViewersDatabase()
    printv("Database loaded!", 5)
    skipViewers = ['blaskatronic', 'blaskbot', 'doryx']
    previousViewers = []
    while True:
        if streamIsUp():
            printv("Stream is active. Getting viewer list...", 4)
            viewerList = getViewerList()
            if viewerList is not None:
                printv("viewerList = " + repr(viewerList), 4)
                flattenedViewerList = [viewerName for nameRank in [viewerList['chatters'][x] \
                                        for x in viewerList['chatters'].keys()] for viewerName \
                                        in nameRank]
                printv("Previous Viewers = " + repr(previousViewers), 4)
                printv("Current Viewers = " + repr(flattenedViewerList), 4)
                currentViewerCount = len(flattenedViewerList)
                rankString = getStreamRank(currentViewerCount)
                printv("Current Viewer Count = " + str(currentViewerCount) + " " +\
                       rankString, 1)
                for viewer in flattenedViewerList:
                    if viewer in previousViewers:
                        printv(viewer + " in both lists. Adding "  + str(cfg.pointsToAward) +\
                               " points...", 5)
                        printv("Checking if " + viewer + " is in database...", 4)
                        # Check if viewer is already in the database
                        if len(viewerDatabase.search(Query().name == viewer)) == 0:
                            printv("Adding " + viewer + " to database...", 4)
                            viewerDatabase.insert({'name': viewer, 'points': 0, 'rank': 'None',
                                                   'multiplier': 1, 'lurker': 'true', 'totalPoints': 0,
                                                   'drinks': 0, 'drinkExpiry': None})
                        printv(viewer + " has " + str(viewerDatabase.search(Query().name ==\
                                viewer)[0]['points']) + " points.", 5)
                        printv("Incrementing " + viewer + "'s points...", 4)
                        viewerDatabase.update(tdbo.add('points', cfg.pointsToAward), \
                                              Query().name == viewer)
                        # Also increment `totalPoints' which is used to keep track of
                        # view time without taking into account minigame losses
                        viewerDatabase.update(tdbo.add('totalPoints', cfg.pointsToAward), \
                                              Query().name == viewer)
                        if viewer in skipViewers:
                            continue
                        printv("Calculating " + viewer + "'s rank...", 5)
                        currentPoints = viewerDatabase.search(Query().name == viewer)[0]['points']
                        currentTotalPoints = viewerDatabase.search(Query().name == viewer)[0]['totalPoints']
                        oldRank = viewerDatabase.search(Query().name == viewer)[0]['rank']
                        newRank = str(oldRank)
                        for rankPoints in sorted(cfg.ranks.keys()):
                            if int(currentTotalPoints) < int(rankPoints):
                                break
                            newRank = cfg.ranks[rankPoints]
                        if newRank != oldRank:
                            viewerDatabase.update(tdbo.set('rank', newRank), Query().name == viewer)
                            if (viewerDatabase.search(Query().name == viewer)[0]['lurker'] == 'false') and\
                                (viewer not in skipViewers):
                                currencyUnits = cfg.currencyName
                                if currentPoints > 1:
                                    currencyUnits += "s"
                                chat(sock, "Congratulations " + viewer + ", you have been promoted" +\
                                     " to the rank of " + newRank + "! You now have " +\
                                     str(currentPoints) + " " + currencyUnits + " to spend!")
                        printv(viewer + " now has " + str(viewerDatabase.search(Query().name ==\
                                viewer)[0]['totalPoints']) + " points, and " + \
                               str(currentPoints) + " to spend on minigames.", 5)
                previousViewers = flattenedViewerList[:]
        else:
            printv("Stream not currently up. Not adding points.", 4)
        printv("Database now looks like this: " + repr(viewerDatabase.all()), 5)
        T.sleep(cfg.awardDeltaT)


def updateLurkerStatus(username):
    viewerDB = loadViewersDatabase()
    try:
        if viewerDB.search(Query().name == username)[0]['lurker'] == 'true':
            printv(username + " spoke, so disabling lurker mode.", 5)
            viewerDB.update(tdbo.set('lurker', 'false'), Query().name == username)
    except IndexError as e:
        # Happens when the response is not yet in DB
        printv("Error updating lurker status for " + username + ": " + str(e), 5)
        pass


def setAllToLurker():
    viewerDB = loadViewersDatabase()
    viewerDB.update(tdbo.set('lurker', 'true'), Query().name.exists())


def getStreamRank(currentViewerCount):
    currentGame = getCurrentGame()
    if currentGame is not None:
        returnString = getStreamsOfCurrentGame(currentGame, currentViewerCount)
    else:
        printv("No game found (check syntax)", 4)
        return "No game found for stream rank."
    if returnString is None:
        return "Stream rank error."
    return returnString


def loadViewersDatabase():
    viewerDB = TinyDB('./databases/' + cfg.JOIN + 'Viewers.db')
    return viewerDB


def loadClipsDatabase():
    clipsDB = TinyDB('./databases/' + cfg.JOIN + 'Clips.db')
    return clipsDB


def getViewerList():
    viewerData = queryAPI("http://tmi.twitch.tv/group/user/" +\
                          cfg.JOIN + "/chatters", header={"User-Agent": \
            "Mozilla/5.0 (X11;Ubuntu;Linux x86_64;rv:55.0) Gecko/20100101 Firefox/55.0",\
            "Cache-Control": "max-age=0", "Connection": "keep-alive"})
    return viewerData


def getCurrentGame():
    streamData = queryAPI("https://api.twitch.tv/kraken/channels/" + cfg.JOIN)
    try:
        return streamData['game']
    except KeyError:
        return None


def getStreamsOfCurrentGame(game, currentViewers):
    streamsData = queryAPI("https://api.twitch.tv/kraken/streams/?game=" + game)
    if streamsData is None:
        return None
    streamViewers = []
    for stream in streamsData['streams']:
        if stream['channel']['name'] != cfg.JOIN.lower():
            streamViewers.append(stream['viewers'])
    try:
        streamViewers.sort(reverse=True)
        rank = 1
        for viewerCount in streamViewers:
            if viewerCount > currentViewers:
                rank += 1
            else:
                break
        #rank = [streamViewers.index(x) for x in streamViewers if x < currentViewers][0] + 1
    except IndexError:
        rank = 1
    return "Current Rank = " + str(rank) + " of " + str(len(streamViewers) + 1) + "."


def isOp(user):
    '''
    Return a user's op status to see if they have op permissions
    '''
    return user in cfg.opList


def streamIsUp():
    streamData = queryAPI("https://api.twitch.tv/kraken/streams/" + cfg.JOIN)
    try:
        if not streamData['stream']:
            return False
    except:
        return False
    return True


def setStreamParams():
    streamParams = {'channel': {'status': cfg.streamTitle, 'game': cfg.gameTitle}}
    channelURL = "https://api.twitch.tv/kraken/channels/" + cfg.JOIN
    print("Setting stream title to: " + cfg.streamTitle + " and game to: " + cfg.gameTitle, 4)
    printv("Setting stream title to: " + cfg.streamTitle + " and game to: " + cfg.gameTitle, 4)
    put(channelURL, streamParams)
    print(queryAPI(channelURL))#["channel"]["status"])


def put(URL, dataDict, header=defaultHeader):
    printv("Sending " + repr(dataDict) + " to URL: '" + URL + "'...", 4)
    req = requests.put(URL, data=dataDict, headers=header)


def incrementNumberOfChatMessages():
    global numberOfChatMessages
    with numberOfChatMessages.get_lock():
        numberOfChatMessages.value += 1


def timer(command, delay, arguments):
    previousNumberOfChatMessages = 0
    try:
        exec("from commands import " + str(command))
        while True:
            # All timers must wait until 15 minutes after 1 chat message
            # has been sent before executing the command again.
            if numberOfChatMessages.value > previousNumberOfChatMessages:
                exec(str(command) + "(arguments)")
                previousNumberOfChatMessages = int(numberOfChatMessages.value)
                T.sleep(delay)
            else:
                printv("Not enough messages sent to run again (" + \
                       str(numberOfChatMessages.value) + " <= " + \
                       str(previousNumberOfChatMessages) + "). Sleeping.", 5)
                T.sleep(900)
    except (AttributeError, ImportError):
        printv("No function by the name " + command + "!", 4)


def getXMLAttributes(xmlData):
    attributeDict = {}
    elementTree = ET.fromstring(xmlData)
    for element in elementTree:
        if len(element) == 0:
            attributeDict[element.tag] = element.text
        else:
            attributeDict[element.tag] = {}
            for subelement in element:
                if subelement.tag == "category":
                    subattribute = attributeDict[element.tag][subelement.get("name")] = {}
                    for subsubelement in subelement:
                        subattribute[subsubelement.get("name")] = subsubelement.text
                else:
                    attributeDict[element.tag][subelement.tag] = subelement.text
    return attributeDict


def queryAPI(URL, header=defaultHeader):
    try:
        data = requests.get(URL, headers=header).json()
        if "error" in data.keys():
            raise URLError
        printv("Json loaded!", 5)
        return data
    except URLError as e:
        printv("URLError: " + str(e) + "!", 4)
    except:
        printv("UNEXPECTED ERROR: " + repr(sys.exc_info()[0]), 2)
    printv("Error from URL: " + URL, 2)
    return None


def thankLatest(sock):
    previousUsername = None
    while True:
        recentData = queryAPI("https://api.twitch.tv/kraken/channels/" + cfg.JOIN +\
                                 "/follows?direction=desc&limit=1")
        if recentData is None:
            continue
        latestUsername = recentData['follows'][0]['user']['name']
        if previousUsername is None:
            previousUsername = latestUsername
            continue
        if latestUsername != previousUsername:
            chat(sock, "Thank you for the follow, " + latestUsername +\
                 "! Welcome to the BlaskForce!")
            latestUsername = previousUsername
        T.sleep(5)


if __name__ == "__main__":
    threadFillOpList()
