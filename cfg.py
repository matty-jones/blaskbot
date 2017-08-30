import os

# Contains BlaskBot's config

# Core interface variables
HOST = "irc.chat.twitch.tv"
PORT = 6667
NICK = os.environ["BOTNICK"]
PASS = os.environ["BOTAUTH"]
JOIN = os.environ["BOTCHAT"]
RATE = 1  # Messages per second
VERB = 2

# Function interface variables
twitchAPIClientID = os.environ["BOTAPIID"]
owner = 'Blaskatronic'
twitterUsername = os.environ["BOTTWIT"]
opList = []
opOnlyCommands = ['subscribe']

# Viewer Points Database
pointsToAward = 1
awardDeltaT = 60
currencyName = "BlasKoin"
ranks = {10: 'Probe',
         50: 'Zealot',
         100: 'Adept',
         150: 'Sentry',
         200: 'Stalker',
         300: 'Warp Prism',
         400: 'Immortal',
         500: 'Phoenix',
         600: 'Oracle',
         700: 'Disruptor',
         800: 'Void Ray',
         900: 'Colossus',
         1000: 'Tempest',
         1100: 'High Templar',
         1200: 'Dark Templar',
         1300: 'Archon',
         1400: 'Dark Archon',
         1500: 'Carrier',
         2000: 'Mothership',
         2500: 'MissingNo.',
         3000: 'NaN'}
