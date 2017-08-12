# BlaskBot v0.3 #

The nascent stages of a custom-built fully-fledged Twitch bot.

## Current features: ##
* Connection to twitch IRC given an account name and OAuth
* The ability to send chat messages and IRC commands
* The ability to read commands from the chat and execute functions based on the user's request
* A rudimentary permissions engine that restricts certain commands from being executed by non-mods

## Current commands: ##
* !bb: BEEP BOOP
* !calc: CALCULATED
* !dece: DECE
* !wa: WEIGH ANCHOR!!!
* !discord: Outputs discord link
* !roll X: rolls a dX for a random integer
* !schedule: Outputs the schedule information
* !help: Outputs the list of commands that the user has permission to run

## To do: ##
* !subscribe: Read and output a random line from a text file of useful notifications
* !nowplaying: Read and output the currently playing song data (can be from file, or directly from VLC)
* !twitter: Use twitter's API to dump the latest tweet to chat
* !uptime: Use twitch's API to get the live time for the current stream
* Notify on host, follow, sub
* Count live minutes and store as offline database to re-implement BlasKoins (import latest data from AnkhBot)
* !harrass-esque minigame for people to gamble BlasKoins on
* Some way of interfacing with clips.twitch.tv to generate and output random clips


## Patch Notes: ##
v0.1: Created basic bot and required networking to interface with Twitch

v0.2: Split bot commands out of the functions module and added rudimentary op permissions

v0.3: Removed sensitive data from repo and released under GPL 3.0


## License: ##
This code is released under GPL 3.0. See LICENSE.txt for more details.
Feel free to raise an issue in this repo if you have a problem using BlaskBot or have a feature that you would like me to add!
Better yet, why not fork the repo and add the functionality yourself? If I like it, I'd be happy to incorporate it!
