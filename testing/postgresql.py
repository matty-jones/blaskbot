import psycopg2
import tinydb
from datetime import datetime

connection = None

def readNumberOfDrinks(cursor):
    #cursor.execute("SELECT Drinks FROM Viewers WHERE Name='blaskatronic'")
    #row = cursor.fetchone()
    #print(row)
    cursor.execute("SELECT * FROM Viewers WHERE Name='blaskatronic'")
    row = cursor.fetchone()
    print(row)


def createTables(cursor):
    cursor.execute("CREATE TABLE Clips (ID SMALLINT PRIMARY KEY, URL VARCHAR(70), Author VARCHAR(25));")
    cursor.execute("INSERT INTO Clips VALUES (%s, %s, %s);", (1, 'YawningEnthusiasticTriangleDXAbomb', 'blaskatronic'))

    cursor.execute("CREATE TABLE Viewers (ID SMALLINT PRIMARY KEY, Name VARCHAR(25), Points SMALLINT, Rank VARCHAR(25), Multiplier FLOAT, Lurker BIT, TotalPoints SMALLINT, DrinkExpiry TIME, Drinks SMALLINT);")
    cursor.execute("INSERT INTO Viewers VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);", (1, 'blaskatronic', 4847, 'Prelate', 1.0, '1', 4787, datetime.now().time(), 38))


if __name__ == "__main__":
    try:
        connection = psycopg2.connect(database='testdb', user='blaskbot')
        cursor = connection.cursor()
        #createTables(cursor)
        readNumberOfDrinks(cursor)

    except psycopg2.DatabaseError as e:
        if connection:
            connection.rollback()
        print("Error", e)
        exit()


    if connection:
        connection.close()
