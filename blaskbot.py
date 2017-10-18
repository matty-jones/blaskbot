'''BlaskBot's Main Loop'''

try:
    import cfg
except TypeError as e:
    # Environment Variables not set
    print(e)
    print("NOTE: At least one of the required environment variables in cfg.py has not been set.")
    print("You have 2 options:")
    print("1) Create the `BOTNICK', `BOTCHAT', `BOTAUTH', `BOTAPIID', 'HOSTAUTH', and `BOTTWIT'" +\
          " environment variables on your host system (i.e. bashrc, bash_profile or" +\
          " whatever ridiculous hoops you have to jump through to get this kinda stuff" +\
          " working on windows [such as installing VirtualBox and running Linux instead])")
    print("2) DANGEROUS: Replace the os.getenv('XXXX') lines in the cfg.py with strings" +\
          " that describe the required variables.\n --==IF YOU DO THIS, NEVER ADD YOUR CFG.PY" +\
          " TO THE REPO.==--\n Otherwise, your twitch OAuth key will be publically available on" +\
          " the internet. You have been warned, and your use of BlaskBot in this way" +\
          " exonerates the devs from any blame for the chaos that ensues.")
    print("Program will now exit.")
    exit()
import functions
from functions import printv
import commands
import socket
import re
import time as T
import os
import sys
from multiprocessing import Process


def main():
    ''' The bot's main loop '''
    botComm = functions.getSocket(cfg.NICK, cfg.PASS, cfg.JOIN)
    hostComm = functions.getSocket(cfg.JOIN, cfg.HOSTPASS, cfg.JOIN)

    CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
    #functions.chat(sock, "Booting up...")

    # Fire the one-off functions to be performed on boot
    functions.checkDatabaseExists()
    functions.setAllToLurker()

    # Create asynchronous, recurring child processes...
    fillOpList = Process(target=functions.threadFillOpList, daemon=True)
    updateDatabase = Process(target=functions.threadUpdateDatabase, args=([botComm]),\
                            daemon=True)
    subscribeTimer = Process(target=functions.timer, args=('subscribe', 3600,\
                            [botComm, cfg.JOIN.lower()]), daemon=True)
    typeAsHost = Process(target=functions.hostChat, args=([hostComm,\
                            os.fdopen(os.dup(sys.stdin.fileno()))]), daemon=True)
    thankLatest = Process(target=functions.thankLatest, args=([botComm]),\
                         daemon=True)
    # ...and start them
    fillOpList.start()
    updateDatabase.start()
    subscribeTimer.start()
    typeAsHost.start()
    thankLatest.start()

    while True:
        hostResponse = hostComm.recv(1024).decode("utf-8")
        if hostResponse == "PING :tmi.twitch.tv\r\n":
            hostComm.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        response = botComm.recv(1024).decode("utf-8")
        if response == "PING :tmi.twitch.tv\r\n":
            botComm.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            try:
                username = re.search(r"\w+", response).group(0)
            except AttributeError:
                continue
            functions.updateLurkerStatus(username)
            message = CHAT_MSG.sub("", response)
            if username not in cfg.skipViewers + ['bot']:
                functions.printv(username + ": " + message, 1)
            if len(message) > 0:
                if message.strip()[0] == "!":
                    # A command has been issued
                    fullMessage = message.strip().split(' ')
                    command = fullMessage[0][1:]
                    username = response[response.index(':') + 1: response.index('!')]
                    arguments = [botComm, username] + fullMessage[1:]
                    if command in cfg.opOnlyCommands:
                        if not functions.isOp(username):
                            functions.chat(botComm, "You don't have permission to run that command!")
                            continue
                    try:
                        getattr(commands, command)(arguments)
                    except AttributeError as e:
                        functions.printv(e, 4)
                        functions.printv("No function by the name " + command + "!", 4)
                else:
                    # Increment the number of sent messages
                    if username.lower() not in ['tmi', cfg.NICK.lower(), cfg.JOIN.lower()]:
                        functions.incrementNumberOfChatMessages()
                        # Read chat and execute commands based on what people are talking about
                        if "discord" in message.lower():
                            getattr(commands, 'discord')([botComm, username])
                        elif "twitter" in message.lower():
                            getattr(commands, 'twitter')([botComm, username])
        # Sleep and then rerun loop
        T.sleep(1)


if __name__ == "__main__":
    main()
