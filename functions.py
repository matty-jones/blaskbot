'''
This is the main functions module that contains everything
we need for BlaskBot to be the most amazing thing the universe
has ever seen.

BEEP BOOP!
'''

import cfg
import urllib.request, urllib.error, urllib.parse
import json
import time as T



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
    msg = "/me " + msg
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
            user_url = "http://tmi.twitch.tv/group/user/" +\
                       "blaskatronic/chatters"
            user_handle = urllib.request.Request(user_url,
                                    headers={"accept": "*/*"})
            printv("Reading from url: '" + user_url + "'...", 5)
            user_response = urllib.request.urlopen(
                                    user_handle).read()
            printv("URL read successfully!", 5)
            printv("Loading user_data json...", 5)
            user_data = json.loads(user_response)
            printv("Json loaded!", 5)
            VIPs = ["moderators", "staff", "admins", "global_mods"]
            for VIPType in VIPs:
                for user in user_data["chatters"][VIPType]:
                    if user not in cfg.opList:
                        printv("Adding " + user + " with VIPType " +
                                VIPType + " to opList...", 4)
                        cfg.opList.append(user)
        except urllib.error.URLError as e:
            printv("URLError!", 5)
            printv("Error Message: " + e, 5)
        printv("Current opList = " + repr(cfg.opList), 5)
        printv("Op Loop complete. Sleeping for 5 seconds before resuming",
              5)
        T.sleep(5)


def isOp(user):
    '''
    Return a user's op status to see if they have op permissions
    '''
    return user in cfg.opList


if __name__ == "__main__":
    threadFillOpList()
