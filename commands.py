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
    _chat(sock, "Calculated. Calculated. Calculated. Calculated. _chat disabled for 1 seconds")


def dece(args):
    sock = args[0]
    _chat(sock, "That was dece, lad!")


def discord(args):
    sock = args[0]
    _chat(sock, "_chat to us on Discord at: www.discord.me/blaskatronic")


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

# TODO !subscribe function: Read a random line from a text file and output it

# TODO !nowplaying funcion: Read the line from the NowPlaying.txt
#       Format: We're currently listening to the following song: XXX

# TODO a !twitter function that reads the twitter API and outputs the latest tweet

# TODO an !uptime function that reads the twitch API and gives the current uptime
#       Format: The stream has been live for $UPTIME
