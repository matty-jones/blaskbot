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

headers = {"Authorization":'OAuth ' + os.environ['BOTAUTH'].split(':')[1]}

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

def chat(sock, msg):
    '''
    Sends a chat message to the server.
    Inputs:
        sock -- The socket over which to send the message
        msg -- (str) The message to send
    '''
    msg = "/me : " + msg
    printv("Sending message '" + msg + "' to chat server...", 5)
    sock.send("PRIVMSG #{} :{}\r\n".format(cfg.JOIN, msg).encode('utf-8'))


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


def threadUpdateDatabase(pointsDatabase):
    previousViewers = []
    while True:
        if streamIsUp():
            printv("Stream is active. Getting viewer list...", 5)
            viewerList = getViewerList()
            flattenedViewerList = [viewerName for nameRank in [viewerList['chatters'][x] \
                                    for x in viewerList['chatters'].keys()] for viewerName \
                                    in nameRank]
            printv("Previous Viewers = " + repr(previousViewers), 5)
            printv("Current Viewers = " + repr(flattenedViewerList), 5)
            for viewer in flattenedViewerList:
                if viewer in previousViewers:
                    printv(viewer + " in both lists. Adding "  + cfg.pointsToAward +\
                           " points...", 5)
                    pointsDatabase[viewer] += int(cfg.pointsToAward)
                    printv(viewer + " now at "  + str(pointsDatabase[viewer]) +\
                           " points.", 5)
            previousViewers = flattenedViewerList[:]
            savePointsDatabase(pointsDatabase)
        else:
            printv("Stream not currently up. Not adding points.", 5)
        T.sleep(cfg.awardDeltaT)


def savePointsDatabase(pointsDatabase):
    raise SystemError("SAVE THE DATABASE")


def loadPointsDatabase():
    raise SystemError("LOAD THE DATABASE")


def getViewerList():
    try:
        viewerURL = "http://tmi.twitch.tv/group/user/" +\
                   "blaskatronic/chatters"
        viewerData = request(viewerURL, header={"accept": "*/*"})
        if "error" in viewerData.keys():
            raise URLError(response)
        printv("Json loaded!", 5)
        return viewerData
    except URLError as e:
        errorDetails = e.args[0]
        printv("URLError with status " + errorDetails['status'] +
               ", '" + errorDetails['error'] + "'!", 4)
        printv("Error Message: " + errorDetails['message'], 4)
        return None


def isOp(user):
    '''
    Return a user's op status to see if they have op permissions
    '''
    return user in cfg.opList


def streamIsUp():
    streamDataURL = "https://api.twitch.tv/kraken/streams/" + _cfg.JOIN
    streamData = request(streamDataURL)
    if not streamData['stream']:
        return False
    return True


def request(URL, header=headers):
    printv("Reading from URL: '" + URL + "'...", 5)
    req = requests.get(URL, headers=header)
    printv("Loading user_data json...", 5)
    return req.json()


if __name__ == "__main__":
    threadFillOpList()
