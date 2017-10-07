import psycopg2
from tinydb import TinyDB, Query


#def createTables():
#    connection = psycopg2.connect(database='blaskatronic', user='blaskbot')
#    cursor = connection.cursor()
#    cursor.execute("CREATE TABLE Clips (ID SMALLINT PRIMARY KEY, URL VARCHAR(70), Author VARCHAR(25));")
#    cursor.execute("CREATE TABLE Viewers (ID SMALLINT PRIMARY KEY, Name VARCHAR(25), Points SMALLINT, Rank VARCHAR(25), Multiplier FLOAT, Lurker BIT, TotalPoints SMALLINT, DrinkExpiry TIME, Drinks SMALLINT);")
#    connection.close()
#
#
#def testTables():
#    connection = psycopg2.connect(database='blaskatronic', user='blaskbot')
#    cursor = connection.cursor()
#    cursor.execute("SELECT * FROM Viewers;")
#    cursor.fetchall()
#    cursor.execute("SELECT * FROM Clips;")
#    cursor.fetchall()
#    connection.close()


if __name__ == "__main__":
    viewersDB = TinyDB('./blaskatronicViewers.db')
    clipsDB = TinyDB('./blaskatronicClips.db')

    viewerDict = viewersDB.search(Query().name.exists())
    clipDict = clipsDB.search(Query().url.exists())

    connection = psycopg2.connect(database='blaskatronic', user='blaskbot')
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE Clips (ID SMALLINT PRIMARY KEY, URL VARCHAR(70), Author VARCHAR(25));")
    cursor.execute("CREATE TABLE Viewers (ID SMALLINT PRIMARY KEY, Name VARCHAR(25), Points SMALLINT, Rank VARCHAR(25), Multiplier FLOAT, Lurker BIT, TotalPoints SMALLINT, DrinkExpiry TIME, Drinks SMALLINT);")

    for index, clip in enumerate(clipDict):
        cursor.execute("INSERT INTO Clips (ID, " + ', '.join(clip.keys()) + ") VALUES (%s, %s, %s);", tuple([index] + list(clip.values())))

    for index, viewer in enumerate(viewerDict):
        viewer['lurker'] = 'B' + str(int(eval(viewer['lurker'].capitalize())))
        cursor.execute("INSERT INTO Viewers (ID, " + ', '.join(viewer.keys()) + ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);", tuple([index] + list(viewer.values())))

    cursor.execute("SELECT * FROM Viewers;")
    print(cursor.fetchall())
    cursor.execute("SELECT * FROM Clips;")
    print(cursor.fetchall())

    connection.commit()

    connection.close()
