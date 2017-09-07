from tinydb import TinyDB, Query
import tinydb.operations as dbop

if __name__ == "__main__":
    # Which database would you like to update?
    databaseName = './databases/blaskatronicViewers.db'
    # Put the new properties you'd like to add to the database here as the keys in
    # the dictionary, and then assign some default values to those keys.
    newPropertiesToAdd = {'drinkExpiry': None, 'drinks': 0}


    # The following code will add those properties and their default values to
    # any elements in the database that don't already have they key.
    db = TinyDB(databaseName)
    allElements = db.search(Query().name.exists())
    for propertyToAdd in newPropertiesToAdd.keys():
        for element in allElements:
            if element in db.search(Query().propertyToAdd.exists()):
                continue
            if propertyToAdd == 'totalPoints':
                value = db.search(Query().name == element['name'])[0]['points']
                db.update(dbop.set(propertyToAdd, value), Query().name == element['name'])
            else:
                db.update(dbop.set(propertyToAdd, newPropertiesToAdd[propertyToAdd]), Query().name == element['name'])


    # ---=== DEBUG LINES ===---
    # Create dummy db for testing
    #for viewer in ['test1', 'test2', 'test3']:
    #    db.insert({'name': viewer, 'points': 0, 'rank': 'None', 'multiplier': 1})
    # ---===================---
