import os

# Contains BlaskBot's config

HOST = "irc.chat.twitch.tv"
PORT = 6667
NICK = os.environ["BOTNICK"]
PASS = os.environ["BOTAUTH"]
JOIN = os.environ["BOTCHAT"]
RATE = 1  # Messages per second
VERB = 5

twitchAPIClientID = os.environ["BOTAPIID"]
owner = 'Blaskatronic'
twitterUsername = os.environ["BOTTWIT"]
opList = []
opOnlyCommands = ['subscribe']
