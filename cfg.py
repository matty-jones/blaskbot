import os

# Contains BlaskBot's config

# Core interface variables
HOST = "irc.chat.twitch.tv"  # The twitch IRC, don't change this.
PORT = 6667                  # The twitch IRC port, don't change this either.
NICK = os.getenv["BOTNICK"]  # The bot's name! Must match the twitch account associated with the bot.
JOIN = os.getenv["BOTCHAT"]  # The channel BlaskBot is to look after (your twitch account name).
PASS = os.getenv["BOTAUTH"]  # The OAuth for your twitch account (needed to push updates and get more deets).
RATE = 1  # Messages per second - Don't reduce this below 1 or your bot will get banned.
VERB = 2  # Verbosity of outputs while the bot is running (1 - 5).

# Function interface variables
twitchAPIClientID = os.getenv["BOTAPIID"]  # The bot needs a clientID for the twitch API
owner = 'Blaskatronic'  # Dev name (will grant this person op in the bot to help troubleshoot)
twitterUsername = os.getenv["BOTTWIT"]  # The name of the twitter channel to pull latest tweets from
opList = []  # List of ops. You can leave this empty - BlaskBot will populate this list when the stream is live
opOnlyCommands = ['subscribe']  # Any commands that you want to be op-only (i.e. viewers can't use them)
VLCLUAPASS = os.getenv["VLCLUAPASS"]  # This is the password for the LUA HTTP interface created by vlc.
                                      # If you don't know what this is, add 'nowplaying' to the opOnlyCommands
                                      # and never use it.

# Viewer Points Database
pointsToAward = 1  # Award this many points to a viewer...
awardDeltaT = 60   # ...after they have watched for this many seconds
currencyName = "BlasKoin"  # Custom currenty name
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
         3000: 'NaN'}  # Set the ranks to whatever you want! Syntax = points: rankName
