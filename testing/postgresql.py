import psycopg2
#import tinydb
from datetime import datetime
from multiprocessing import Process
import time as T
from psycopg2.extras import DictCursor
from psycopg2.extensions import AsIs
import sys
sys.path.append('../')
import cfg
import collections
import datetime
import numpy as np

connection = None

def readRow(extra):
    #cursor.execute("SELECT Drinks FROM Viewers WHERE Name='blaskatronic'")
    #row = cursor.fetchone()
    #print(row)
    connection = psycopg2.connect(database='testdb', user='blaskbot')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Viewers WHERE Name='blaskatronic'")
    row = cursor.fetchone()
    print(extra, row)
    connection.close()


def incrementPoints():
    connection = psycopg2.connect(database='testdb', user='blaskbot')
    cursor = connection.cursor()
    while True:
        cursor.execute("UPDATE Viewers SET Points = Points + 1 WHERE Name='blaskatronic'")
        connection.commit()
        readRow("INCREMENT")
    connection.close()


def decrementPoints():
    connection = psycopg2.connect(database='testdb', user='blaskbot')
    cursor = connection.cursor()
    while True:
        cursor.execute("UPDATE Viewers SET Points = Points - 2 WHERE Name='blaskatronic'")
        connection.commit()
        readRow("DECREMENT")
    connection.close()


def getClip():
    connection = psycopg2.connect(database='testdb', user='blaskbot')
    cursor = connection.cursor()
    while True:
        cursor.execute("SELECT * FROM Clips WHERE ID=1")
        row = cursor.fetchone()
        connection.commit()
        print("CLIP", row)
    connection.close()


def createTables():
    connection = psycopg2.connect(database='testdb', user='blaskbot')
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE Clips (ID SMALLINT PRIMARY KEY, URL VARCHAR(70), Author VARCHAR(25));")
    cursor.execute("INSERT INTO Clips VALUES (%s, %s, %s);", (1, 'YawningEnthusiasticTriangleDXAbomb', 'blaskatronic'))

    cursor.execute("CREATE TABLE Viewers (ID SMALLINT PRIMARY KEY, Name VARCHAR(25), Points SMALLINT, Rank VARCHAR(25), Multiplier FLOAT, Lurker BIT, TotalPoints SMALLINT, DrinkExpiry TIME, Drinks SMALLINT);")
    cursor.execute("INSERT INTO Viewers VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);", (1, 'blaskatronic', 4847, 'Prelate', 1.0, '1', 4787, datetime.now().time(), 38))


def checkViewerExists():
    connection = psycopg2.connect(database='testdb', user='blaskbot')
    cursor = connection.cursor()
    viewer = 'cheeseman'
    cursor.execute("SELECT EXISTS (SELECT 1 FROM Viewers WHERE Name='" + viewer + "');")
    data = cursor.fetchone()
    print(data[0])


def getPoints(viewer='blaskatronic'):
    connection = psycopg2.connect(database='testdb', user='blaskbot')
    cursor = connection.cursor()
    cursor.execute("SELECT Points FROM Viewers WHERE name='" + viewer + "';")
    data = cursor.fetchone()
    print(data)
    return data[0]


def updatePoints():
    connection = psycopg2.connect(database='testdb', user='blaskbot')
    cursor = connection.cursor()
    viewer = 'blaskatronic'
    currentPoints = getPoints(viewer)
    readRow("BEFORE =")
    cursor.execute("UPDATE Viewers SET points=(%s) WHERE name='" + viewer + "';", tuple([currentPoints + 10]))
    cursor.execute("UPDATE Viewers SET totalpoints=(%s) WHERE name='" + viewer + "';", tuple([currentPoints + 100]))
    cursor.execute("UPDATE Viewers SET rank=(%s) WHERE name='" + viewer + "';", tuple(['Chump']))

    cursor.execute("UPDATE Viewers SET lurker=(%s) WHERE name='" + viewer + "';", tuple(['B1']))
    cursor.execute("SELECT Lurker FROM Viewers WHERE name='" + viewer + "';")
    lurkerStatus = cursor.fetchone()[0]
    print(bool(int(lurkerStatus)))
    cursor.execute("UPDATE Viewers SET lurker=(%s) WHERE name='" + viewer + "';", tuple(['B0']))
    cursor.execute("SELECT Lurker FROM Viewers WHERE name='" + viewer + "';")
    lurkerStatus = cursor.fetchone()[0]
    print(bool(int(lurkerStatus)))
    connection.commit()
    readRow("AFTER =")
    newPoints = getPoints(viewer)


def updateLurker(viewer='blaskatronic'):
    connection = psycopg2.connect(database='testdb', user='blaskbot')
    cursor = connection.cursor()
    cursor.execute("UPDATE Viewers SET lurker=(%s) WHERE name='" + viewer + "';", tuple(['B0']))
    cursor.execute("SELECT Lurker FROM Viewers WHERE name='" + viewer + "';")
    lurkerStatus = cursor.fetchone()[0]
    print(bool(int(lurkerStatus)))
    cursor.execute("UPDATE Viewers SET lurker=(%s);", tuple(['B1']))
    cursor.execute("SELECT Lurker FROM Viewers WHERE name='" + viewer + "';")
    lurkerStatus = cursor.fetchone()[0]
    print(bool(int(lurkerStatus)))


def getBoth(viewer='blaskatronic'):
    connection = psycopg2.connect(database='testdb', user='blaskbot')
    cursor = connection.cursor()
    cursor.execute("SELECT (points, totalPoints) FROM Viewers WHERE name='" + viewer + "';")
    data = cursor.fetchone()[0]
    print(eval(data))
    (currentPoints, currentTotalPoints) = eval(data)
    print(currentPoints, currentTotalPoints)


def buyDrink(viewer='blaskatronic'):
    connection = psycopg2.connect(database='testdb', user='blaskbot')
    cursor = connection.cursor()
    numberOfDrinks = 5
    cursor.execute("SELECT Drinks FROM Viewers WHERE name='" + viewer + "';")
    currentDrinks = cursor.fetchone()[0]
    print(currentDrinks)
    print(cursor.mogrify("UPDATE Viewers SET drinks=drinks + " + str(numberOfDrinks) + " WHERE name='" + viewer.lower() + "';"))
    cursor.execute("UPDATE Viewers SET drinks=drinks + " + str(numberOfDrinks) + " WHERE name='" + viewer.lower() + "';")
    cursor.execute("SELECT Drinks FROM Viewers WHERE name='" + viewer + "';")
    currentDrinks = cursor.fetchone()[0]
    print(currentDrinks)


def getRandomClip():
    connection = psycopg2.connect(database='blaskatronic', user='blaskbot')
    cursor = connection.cursor(cursor_factory=DictCursor)
    cursor.execute("SELECT * FROM Clips")
    clips = cursor.fetchall()
    index = -1
    print(clips[index]['url'])


def getTop():
    connection = psycopg2.connect(database='blaskatronic', user='blaskbot')
    forbidden = ['blaskatronic', 'blaskbot', 'doryx']
    cursor = connection.cursor(cursor_factory=DictCursor)
    cursor.execute("SELECT * FROM Viewers WHERE name NOT IN (" + ', '.join([repr(x) for x in forbidden]) + ") ORDER BY totalpoints DESC LIMIT 10;")
    topRanked = cursor.fetchall()
    for i, viewerDetails in enumerate(topRanked):
        #print(i, "|", viewerDetails['name'], "|", viewerDetails['totalpoints'])
        print("%1d | %15s | %5d" % (i, viewerDetails['name'], viewerDetails['totalpoints']))


def fixViewerDB():
    connection = psycopg2.connect(database='blaskytest', user='blaskbot')
    forbidden = ['blaskatronic', 'blaskbot', 'doryx']
    cursor = connection.cursor()
    viewer = 'chumpzilla'
    insert = {'Name': viewer.lower(), 'Points': 0, 'Rank': 'Chump',
              'Multiplier': 1.0, 'Lurker': 'B1', 'TotalPoints': 0,
              'Drinks': 0, 'Discord': viewer.lower()}
    cursor.execute("INSERT INTO Viewers (%s) VALUES %s;", (AsIs(', '.join(insert.keys())), AsIs(tuple(insert.values()))))
    cursor.execute("SELECT * FROM Viewers WHERE name='" + viewer.lower() + "';")
    currentViewer = cursor.fetchone()
    print(currentViewer)


def untilNextCalculation():
    connection = psycopg2.connect(database='blaskytest', user='blaskbot')
    userName = 'doryx'
    cursor = connection.cursor()
    cursor.execute("SELECT totalpoints FROM Viewers WHERE name='" + userName.lower() + "';")
    totalPoints = int(cursor.fetchone()[0])
    cursor.execute("SELECT rank FROM Viewers WHERE name='" + userName.lower() + "';")
    currentRank = str(cursor.fetchone()[0])
    cursor.execute("SELECT multiplier FROM Viewers WHERE name='" + userName.lower() + "';")
    currentMultiplier = float(cursor.fetchone()[0])
    nextRank = None
    pointsForNextRank = None
    print(totalPoints)
    for rankPoints in sorted(cfg.ranks.keys()):
        print("iter", rankPoints)
        nextRank = cfg.ranks[rankPoints]
        pointsForNextRank = rankPoints
        if totalPoints < rankPoints:
            print(totalPoints, rankPoints, "break")
            break
    return

    secondsToNextRank = (pointsForNextRank - totalPoints) * int(cfg.awardDeltaT /\
                            (cfg.pointsToAward * currentMultiplier))
    totalSecondsSoFar = totalPoints * int(cfg.awardDeltaT / cfg.pointsToAward)
    totalMins, totalSecs = divmod(totalSecondsSoFar, 60)
    totalHours, totalMins = divmod(totalMins, 60)
    totalTimeDict = collections.OrderedDict()
    totalTimeDict['hour'] = int(totalHours)
    totalTimeDict['minute'] = int(totalMins)
    totalTimeDict['second'] = int(totalSecs)
    totalTimeArray = []
    mins, secs = divmod(secondsToNextRank, 60)
    hours, mins = divmod(mins, 60)
    timeDict = collections.OrderedDict()
    timeDict['hour'] = int(hours)
    timeDict['minute'] = int(mins)
    timeDict['second'] = int(secs)
    print("Current Points =", totalPoints)
    print("Points for next rank =", pointsForNextRank)
    print("Seconds to next rank =", secondsToNextRank)
    print("Total Seconds So Far =", totalSecondsSoFar)
    print(totalTimeDict)
    print(timeDict)
    return

    timeArray = []
    for key, value in totalTimeDict.items():
        if value > 1:
            totalTimeArray.append(str(value) + " " + str(key) + "s")
        elif value > 0:
            totalTimeArray.append(str(value) + " " + str(key))
    totalTime = ' and '.join(totalTimeArray[-2:])
    if len(totalTimeArray) == 3:
        totalTime = totalTimeArray[0] + ", " + totalTime
    for key, value in timeDict.items():
        if value > 1:
            timeArray.append(str(value) + " " + str(key) + "s")
        elif value > 0:
            timeArray.append(str(value) + " " + str(key))
    timeToNext = ' and '.join(timeArray[-2:])
    if len(timeArray) == 3:
        timeToNext = timeArray[0] + ", " + timeToNext
    rankMod = ' '
    if currentRank[0] in ['a', 'e', 'i', 'o', 'u']:
        rankMod = 'n '
    outputLine = userName + " has currently watched for " + totalTime +\
            " and is a" + rankMod + str(currentRank) +\
            " (" + timeToNext + " until next rank!)"
    print(outputLine)


def timeToNextStream():
    #streamSchedule = np.array([[1, 20, 30], [3, 20, 30], [5, 11, 30]]) # Pretend this is UTC
    #now = list(map(int, datetime.datetime.now().strftime("%H %M").split(' ')))
    streamSchedule = np.array([[1, 20, 30], [3, 20, 30], [5, 11, 30]]) # Pretend this is UTC
    now = list(map(int, datetime.datetime.now().strftime("%H %M").split(' ')))
    today = int(datetime.datetime.today().weekday())
    nowArray = np.array([today] + now)
    print(nowArray)
    timeDeltaArray = streamSchedule - nowArray
    print(timeDeltaArray)
    modulos = [7, 24, 60]
    for (x, y), element in np.ndenumerate(timeDeltaArray):
        if element < 0:
            timeDeltaArray[x, y] = element%modulos[y]
            try:
                # If we can, decrement the next time level up to reflect this change
                timeDeltaArray[x, y-1] -= 1
            except:
                # Don't need to do this for the number of days
                pass
    print(timeDeltaArray)
    print(timeDeltaArray[timeDeltaArray[:,0].argsort()])


if __name__ == "__main__":
    #try:
    #    #createTables(cursor)
    #    readRow("INIT")
    #    incrementPoints = Process(target=incrementPoints, args=(), daemon=True)
    #    decrementPoints = Process(target=decrementPoints, args=(), daemon=True)
    #    getClip = Process(target=getClip, args=(), daemon=True)
    #    input("ARE YOU READY?!")
    #    incrementPoints.start()
    #    decrementPoints.start()
    #    #getClip.start()
    #    T.sleep(0.05)
    #    exit()
    #    #incrementPoints(cursor)
    #    #connection.commit()
    #    input("WAIT")

    #except psycopg2.DatabaseError as e:
    #    if connection:
    #        connection.rollback()
    #    print("Error", e)
    #    exit()


    #checkViewerExists()
    #updatePoints()
    #updateLurker()
    #getBoth()
    #buyDrink()
    #getRandomClip()
    #getTop()
    #fixViewerDB()
    #untilNextCalculation()
    timeToNextStream()

    if connection:
        connection.close()
