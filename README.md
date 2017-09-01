# BlaskBot v0.5 #


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
* Add Gibu's !buydrinks command! Because everyone loves to get wasted during our streams.
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


## Installation Instructions: ##

### Environment Variables ###
Perhaps the most important thing is to set the correct environment variables specified in the cfg.py.
These allow the bot to see your twitch account and authentication details without them being stored in plain text in the repo.
As you'll notice when you run the bot for the first time right out of the repo, an error message will suggest that you either create the environment variables yourself, or place them directly in the relevant places in the cfg.py.
The latter is strongly not recommended as you don't want to accidently commit an update to the cfg.py and then broadcast your twitch login details to the whole internet, so be very careful if you choose to do this.

* Setting environment variables in Linux/Unix:
    * Update your .bashrc (.bash\_profile if using Mac OSX) to include the following lines:
         ```
         # BlaskBot stuff
         export BOTNICK="<BOT TWITCH ACCOUNT NAME GOES HERE>"
         export BOTCHAT="<YOUR TWITCH ACCOUNT NAME GOES HERE>"
         export BOTAUTH="oauth:<OAUTH FOR BOT TWITCH GOES HERE>"
         export HOSTAUTH="oauth:<OAUTH FOR YOUR TWITCH GOES HERE>"
         export BOTTWIT="<YOUR TWITTER ACCOUNT NAME GOES HERE>"
         export VLCLUAPASS="<YOUR VLC LUA HTTP INTERFACE PASSWORD GOES HERE>"
         export BOTAPIID="<YOUR BOT TWITCH API CLIENT-ID GOES HERE>"
         ```
    * The `BOTNICK`, `BOTCHAT` and `BOTTWIT` variables should be pretty self explanatory - note that the bot will need its own twitch account for everything to work properly. Note that if you don't want to link the bot to twitter, just put whatever you want in `BOTTWIT` and add the `twitter` command to the opOnlyCommands list in cfg.py to disable it for your users.
    * If you don't already have an OAuth key for your twitch account or have forgotten it, you can create a new one by authorising your twitch account at http://www.twitchapps.com/tmi/. Do this for both the bot account (`BOTAUTH`) and the host account (`HOSTAUTH`) to get your keys. Note that you need to keep the "oauth:" in front of it otherwise it won't parse correctly.
    * The `BOTAPIID` variable can be obtained by registering your version of BlaskBot using https://dev.twitch.tv/dashboard/apps/create. Note that you should be logged in as your bot at this point to get the right clientID.
    * The `VLCLUAPASS` variable is used to communicate with VLC using it's LUA HTTP interface. This has to be set up externally in VLC, information about which can be readily found online. When it is set up correctly, BlaskBot should be able to parse the "now playing" information from VLC, which is bound to the !nowplaying command to allow users to query the current song that is playing on stream. As with the !twitter command, you can just put any string in here and put `nowplaying` in the opOnlyCommands list to disable it if you don't want to set this up/use it.


### Python Modules ###
There are a couple of non-standard python modules currently in use in BlaskBot, namely `requests` for handling communication to and from the various APIs and servers, and `tinydb`, which is used to store the rank, points and clip details for the channel.
As more functions are added, more modules might be used so the best way to account for this is to use an environment manager to create a virtual python environment that can be kept up to date with all the requisite modules.
The prerequisites are stored in requirements.yml and this file will be updated with any new modules that are needed to run BlaskBot.

* Installing Requisite Python Modules (on Linux/Unix, check the Conda documentation for how to activate and install environments on Windows):
    * First install miniconda for your machine from https://conda.io/miniconda.html (python 3.6 is recommended)
    * When miniconda has been installed and the `PYTHONPATH` environment variable updated to miniconda's location (should be done automatically), the environment can be set up by using `conda env create -f requirements.yml` from BlaskBot's root directory.
    * After installation, the environment can be activated using `source activate blaskbot`. The environment will need to be active for the bot the run.


### Running the bot ###
Simple! Activate the blaskbot conda environment and invoke `python blaskbot.py`!


## License: ##
This code is released under GPL 3.0. See LICENSE.txt for more details.
Feel free to raise an issue in this repo if you have a problem using BlaskBot or have a feature that you would like me to add!
Better yet, why not fork the repo and add the functionality yourself? If I like it, I'd be happy to incorporate it!
