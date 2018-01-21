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
from multiprocessing import Value
import xml.etree.ElementTree as ET
import psycopg2
from psycopg2.extensions import AsIs

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
    #printv(sendType + ": " + msg, 1)
    try:
        sock.send("PRIVMSG #{} :{}\r\n".format(cfg.JOIN, msg).encode('utf-8'))
    except:
        printv("ERROR: " + repr(sys.exc_info()[0]) + ", MESSAGE NOT SENT", 1)


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


def checkDatabaseExists():
    try:
        connection = psycopg2.connect(database=cfg.JOIN.lower(), user=cfg.NICK.lower())
    except psycopg2.OperationalError:
        printv("The database '" + cfg.JOIN + "' doesn't exist! Creating it now using the postgres superadmin user...", 1)
        tempConnect = psycopg2.connect(database='postgres', user='postgres')
        tempConnect.autocommit = True
        tempConnect.cursor().execute('CREATE DATABASE {} OWNER {};'.format(cfg.JOIN, cfg.NICK))
        tempConnect.close()
        connection = psycopg2.connect(database=cfg.JOIN.lower(), user=cfg.NICK.lower())
        cursor = connection.cursor()
        printv("Constructing the Viewers Table...", 1)
        cursor.execute("CREATE TABLE Viewers (ID SERIAL PRIMARY KEY, Name VARCHAR(25), Points SMALLINT, Rank VARCHAR(25), Multiplier FLOAT, Lurker BIT, TotalPoints SMALLINT, DrinkExpiry TIME, Drinks SMALLINT, Discord VARCHAR(25));")
        printv("Constructing the Clips Table...", 1)
        cursor.execute("CREATE TABLE Clips (ID SERIAL PRIMARY KEY, URL VARCHAR(70), Author VARCHAR(25));")
        printv("Empty database created. Returning to main program.", 1)
    connection.close()


def threadUpdateDatabase(sock):
    printv("Loading the viewer database...", 5)
    connection = psycopg2.connect(database=cfg.JOIN.lower(), user=cfg.NICK.lower())
    cursor = connection.cursor()
    printv("Database loaded!", 5)
    skipViewers = cfg.skipViewers
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
                        cursor.execute("SELECT EXISTS (SELECT 1 FROM Viewers WHERE Name='" + viewer.lower() + "');")
                        if not cursor.fetchone()[0]:
                            printv("Adding " + viewer + " to database...", 4)
                            insert = {'Name': viewer.lower(), 'Points': 0, 'Rank': 'Chump',
                                      'Multiplier': 1.0, 'Lurker': 'B1', 'TotalPoints': 0,
                                      'Drinks': 0, 'Discord': viewer.lower()}
                            cursor.execute("INSERT INTO Viewers (%s) VALUES %s;", (AsIs(', '.join(insert.keys())), AsIs(tuple(insert.values()))))
                        cursor.execute("SELECT Points FROM Viewers WHERE name='" + viewer.lower() + "';")
                        currentPoints = cursor.fetchone()[0]
                        printv(viewer + " has " + str(currentPoints) + " points.", 5)
                        printv("Incrementing " + viewer + "'s points...", 4)
                        cursor.execute("UPDATE Viewers SET points=points + " + str(cfg.pointsToAward) + " WHERE name='" + viewer.lower() + "';")
                        # Also increment `totalPoints' which is used to keep track of
                        # view time without taking into account minigame losses
                        cursor.execute("SELECT totalpoints FROM Viewers WHERE name='" + viewer.lower() + "';")
                        currentTotalPoints = cursor.fetchone()[0]
                        cursor.execute("UPDATE Viewers SET totalpoints=totalpoints + " + str(cfg.pointsToAward) + " WHERE name='" + viewer.lower() + "';")
                        if viewer.lower() in skipViewers:
                            continue
                        printv("Calculating " + viewer + "'s rank...", 5)
                        currentPoints += cfg.pointsToAward
                        currentTotalPoints += cfg.pointsToAward
                        cursor.execute("SELECT rank FROM Viewers WHERE name='" + viewer.lower() + "';")
                        oldRank = cursor.fetchone()[0]
                        newRank = str(oldRank)
                        for rankPoints in sorted(cfg.ranks.keys()):
                            if int(currentTotalPoints) < int(rankPoints):
                                break
                            newRank = cfg.ranks[rankPoints]
                        if newRank != oldRank:
                            cursor.execute("UPDATE Viewers SET rank=(%s) WHERE name='" + viewer.lower() + "';", tuple([newRank]))
                            cursor.execute("SELECT lurker FROM Viewers WHERE name='" + viewer.lower() + "';")
                            lurker = bool(int(cursor.fetchone()[0]))
                            if not lurker:
                                currencyUnits = cfg.currencyName
                                if currentPoints > 1:
                                    currencyUnits += "s"
                                chat(sock, "Congratulations " + viewer + ", you have been promoted" +\
                                     " to the rank of " + newRank + "! You now have " +\
                                     str(currentPoints) + " " + currencyUnits + " to spend!")
                        cursor.execute("SELECT (points, totalpoints) FROM Viewers WHERE name='" + viewer.lower() + "';")
                        data = cursor.fetchone()[0]
                        (currentPoints, currentTotalPoints) = eval(data)
                        printv(viewer + " now has " + str(currentTotalPoints) + " points, and " + \
                               str(currentPoints) + " to spend on minigames.", 5)
                previousViewers = flattenedViewerList[:]
        else:
            printv("Stream not currently up. Not adding points.", 4)
        connection.commit()
        cursor.execute("SELECT * FROM Viewers;")
        allViewers = cursor.fetchall()
        printv("Database now looks like this: " + repr(allViewers), 5)
        T.sleep(cfg.awardDeltaT)


def updateLurkerStatus(viewer):
    connection = psycopg2.connect(database=cfg.JOIN.lower(), user=cfg.NICK.lower())
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT lurker FROM Viewers WHERE name='" + viewer.lower() + "';")
        lurker = bool(int(cursor.fetchone()[0]))
        if lurker:
            printv(viewer + " spoke, so disabling lurker mode.", 5)
            cursor.execute("UPDATE Viewers SET lurker=(%s) WHERE name='" + viewer.lower() + "';", tuple(['B0']))
    except:
        # Happens when the response is not yet in DB
        printv("Error updating lurker status for " + viewer + ": " + repr(sys.exc_info()[0]), 5)
        pass
    connection.commit()
    connection.close()


def setAllToLurker():
    connection = psycopg2.connect(database=cfg.JOIN.lower(), user=cfg.NICK.lower())
    cursor = connection.cursor()
    cursor.execute("UPDATE Viewers SET lurker=(%s);", tuple(['B1']))
    connection.commit()
    connection.close()


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
    except:
        return None


def getStreamsOfCurrentGame(game, currentViewers):
    streamsData = queryAPI("https://api.twitch.tv/kraken/streams/?game=" + game + "&limit=100")
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
    if streamData is None:
        return None
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
            previousUsername = latestUsername
        T.sleep(5)


if __name__ == "__main__":
    threadFillOpList()
