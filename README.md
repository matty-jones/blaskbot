# BlaskBot v0.3 #


The nascent stages of a custom-built fully-fledged Twitch bot.


## Current features: ##
* Connection to twitch IRC given an account name and OAuth
* The ability to send chat messages and IRC commands
* The ability to read commands from the chat and execute functions based on the user's request
* A rudimentary permissions engine that restricts certain commands from being executed by non-mods
* A load of fun/useful bot commands (listed below)
* Connection to twitch and twitter APIs


## Current commands: ##
* !bb: BEEP BOOP
* !blaskoins: Outputs your current blaskoins and rank information
* !calc: CALCULATED
* !clip: Outputs a random clip. Can also output a clip with specific ID (!clip <ID>) or from a specific viewer (!clip <VIEWER>), and mods can add clips using !clip add <SLUG> <AUTHOR>.
* !dece: DECE
* !discord: Outputs discord link
* !help: Outputs the list of commands that the user has permission to run
* !roll X: rolls a dX for a random integer
* !schedule: Outputs the schedule information
* !subscribe: Outputs a random line from a text file of useful notifications, on a timer providing at least one non-command chat message has been sent since the last time it output.
* !time: Outputs the current local time
* !twitter: Uses the Twitter API to output the latest tweet
* !uptime: Outputs the uptime of the current stream
* !wa: WEIGH ANCHOR!!!


## To do: ##
* Allow the streamer to send messages from the bot terminal window
* Allow the streamer to update the title, game, and communities either from the cfg file or the bot terminal window
* Notify on host, follow, sub
* !harrass-esque minigame for people to gamble BlasKoins on
* !slot minigame with a jackpot where people can win steam keys located in a database
* !streamrank command that parses all streams for the current game and outputs the current rank based on viewers (maybe run this as a thread so that it keeps updating in the background for stats)


## Patch Notes: ##
v0.1: Created basic bot and required networking to interface with Twitch

v0.2: Split bot commands out of the functions module and added rudimentary op permissions

v0.3: Removed sensitive data from repo and released under GPL 3.0

v0.4: Added a database to keep track of live viewers and award a custom number of points at custom intervals

v0.5: Added the clip database engine

## License: ##
This code is released under GPL 3.0. See LICENSE.txt for more details.
Feel free to raise an issue in this repo if you have a problem using BlaskBot or have a feature that you would like me to add!
Better yet, why not fork the repo and add the functionality yourself? If I like it, I'd be happy to incorporate it!
