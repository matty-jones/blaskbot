'''
This module contains all of the !commands that the users
can call upon for execution.
'''

from functions import chat as _chat
import sys as _sys
import cfg as _cfg
import inspect as _inspec
import random as _R
import time as _T
import urllib.request


def time(args):
    sock = args[0]
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
    dsides = int(args[2])
    rollNumber = _R.randint(1, dsides)
    _chat(sock, "I rolled a D" + str(dsides) + ", and got " + str(rollNumber))


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
    fileName = './NowPlaying.txt'
    with open(fileName, 'r') as subFile:
        lines = subFile.readlines()
        _chat(sock, "We're currently listening to the following song: " + lines[0][:-1])


def twitter(args):
    sock = args[0]
    if "<YOUR TWITTER USERNAME HERE>" not in str(_cfg.twitterUsername):
        latestTweetURL = "https://decapi.me/twitter/latest.php?name=" +\
                        str(_cfg.twitterUsername)
        tweetHandle = urllib.request.Request(latestTweetURL,
                                headers={"accept": "*/*"})
        latestTweet = urllib.request.urlopen(tweetHandle).read().decode("utf-8")
        _chat(sock, "Latest tweet from " + str(_cfg.twitterUsername) +
                ": " + latestTweet)


# TODO an !uptime function that reads the twitch API and gives the current uptime
#       Format: The stream has been live for $UPTIME
