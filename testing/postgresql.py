import psycopg2
import tinydb
from datetime import datetime
from multiprocessing import Process
import time as T

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


if __name__ == "__main__":
    try:
        #createTables(cursor)
        readRow("INIT")
        incrementPoints = Process(target=incrementPoints, args=(), daemon=True)
        decrementPoints = Process(target=decrementPoints, args=(), daemon=True)
        getClip = Process(target=getClip, args=(), daemon=True)
        input("ARE YOU READY?!")
        incrementPoints.start()
        decrementPoints.start()
        #getClip.start()
        T.sleep(0.05)
        exit()
        #incrementPoints(cursor)
        #connection.commit()
        input("WAIT")

    except psycopg2.DatabaseError as e:
        if connection:
            connection.rollback()
        print("Error", e)
        exit()

    if connection:
        connection.close()
