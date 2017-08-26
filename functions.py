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
        try:
            viewerUrl = "http://tmi.twitch.tv/group/user/" +\
                       "blaskatronic/chatters"
            printv("Reading from url: '" + viewerUrl + "'...", 5)
            response = requests.get(viewerUrl, headers={"accept": "*/*"})
            printv("Loading user_data json...", 5)
            viewerData = response.json()
            if "error" in viewerData.keys():
                raise URLError(response)
            printv("Json loaded!", 5)
            VIPs = ["moderators", "staff", "admins", "global_mods"]
            for VIPType in VIPs:
                for viewer in viewerData["chatters"][VIPType]:
                    if viewer not in cfg.opList:
                        printv("Adding " + viewer + " with VIPType " +
                                VIPType + " to opList...", 4)
                        cfg.opList.append(viewer)
        except URLError as e:
            errorDetails = e.args[0]
            printv("URLError with status " + errorDetails['status'] +
                   ", '" + errorDetails['error'] + "'!", 5)
            printv("Error Message: " + errorDetails['message'], 5)
        printv("Current opList = " + repr(cfg.opList), 5)
        printv("Op Loop complete. Sleeping for 5 seconds before resuming",
              5)
        T.sleep(5)


def isOp(user):
    '''
    Return a user's op status to see if they have op permissions
    '''
    return user in cfg.opList


def request(url):
    req = requests.get(url, headers=headers)
    return req.json()


if __name__ == "__main__":
    threadFillOpList()
