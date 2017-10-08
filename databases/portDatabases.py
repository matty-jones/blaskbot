import psycopg2
from tinydb import TinyDB, Query

#def createTables():
#    connection = psycopg2.connect(database='blaskytest', user='blaskbot')
#    cursor = connection.cursor()
#    cursor.execute("CREATE TABLE Clips (ID SMALLINT PRIMARY KEY, URL VARCHAR(70), Author VARCHAR(25));")
#    cursor.execute("CREATE TABLE Viewers (ID SMALLINT PRIMARY KEY, Name VARCHAR(25), Points SMALLINT, Rank VARCHAR(25), Multiplier FLOAT, Lurker BIT, TotalPoints SMALLINT, DrinkExpiry TIME, Drinks SMALLINT);")
#    connection.close()
#
#
#def testTables():
#    connection = psycopg2.connect(database='blaskytest', user='blaskbot')
#    cursor = connection.cursor()
#    cursor.execute("SELECT * FROM Viewers;")
#    cursor.fetchall()
#    cursor.execute("SELECT * FROM Clips;")
#    cursor.fetchall()
#    connection.close()


if __name__ == "__main__":
    channel = 'blaskatronic'
    viewersDB = TinyDB('./' + channel + 'Viewers.db')
    clipsDB = TinyDB('./' + channel + 'Clips.db')
    discordDB = TinyDB('./discordNames.db')

    viewerDict = viewersDB.search(Query().name.exists())
    clipDict = clipsDB.search(Query().url.exists())
    discordDict = discordDB.search(Query().twitchName.exists())

    try:
        connection = psycopg2.connect(database=channel + 'db', user='blaskbot')
    except psycopg2.OperationalError:
        tempConnect = psycopg2.connect(database='postgres', user='postgres')
        tempConnect.autocommit = True
        print('CREATE DATABASE {};'.format(channel + 'db'))
        tempConnect.cursor().execute('CREATE DATABASE {};'.format(channel + 'db'))
        tempConnect.close()
        connection = psycopg2.connect(database=channel + 'db', user='blaskbot')

    cursor = connection.cursor()
    cursor.execute("CREATE TABLE Clips (ID SERIAL PRIMARY KEY, URL VARCHAR(70), Author VARCHAR(25));")
    cursor.execute("CREATE TABLE Viewers (ID SERIAL PRIMARY KEY, Name VARCHAR(25), Points SMALLINT, Rank VARCHAR(25), Multiplier FLOAT, Lurker BIT, TotalPoints SMALLINT, DrinkExpiry TIME, Drinks SMALLINT);")

    for index, clip in enumerate(clipDict):
        cursor.execute("INSERT INTO Clips (" + ', '.join(clip.keys()) + ") VALUES (%s, %s);", tuple(clip.values()))

    for index, viewer in enumerate(viewerDict):
        viewer['lurker'] = 'B' + str(int(eval(viewer['lurker'].capitalize())))
        cursor.execute("INSERT INTO Viewers (" + ', '.join(viewer.keys()) + ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", tuple(viewer.values()))

    ### Sorting the Discord name mappings out
    # First, create the discord column
    cursor.execute("ALTER TABLE Viewers ADD Discord VARCHAR(25);")
    # Then, update the discord column to be == the name column
    cursor.execute("UPDATE Viewers SET Discord = Name;")

    # Now, iterate through the TinyDB and re-update the ones we know there are discord names for
    for _, user in enumerate(discordDict):
        cursor.execute("UPDATE Viewers SET Discord = %s WHERE Name = %s;", (user['discordName'], user['twitchName']))


    cursor.execute("SELECT * FROM Viewers;")
    print(cursor.fetchall())
    cursor.execute("SELECT * FROM Clips;")
    print(cursor.fetchall())

    connection.commit()

    connection.close()
