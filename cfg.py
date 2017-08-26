import os

# Contains BlaskBot's config

# Core interface variables
HOST = "irc.chat.twitch.tv"
PORT = 6667
NICK = os.environ["BOTNICK"]
PASS = os.environ["BOTAUTH"]
JOIN = os.environ["BOTCHATTEST"]
RATE = 1  # Messages per second
VERB = 5

# Function interface variables
twitchAPIClientID = os.environ["BOTAPIID"]
owner = 'Blaskatronic'
twitterUsername = os.environ["BOTTWIT"]
opList = []
opOnlyCommands = ['subscribe']

# Viewer Points Database
pointsToAward = 1
awardDeltaT = 60
