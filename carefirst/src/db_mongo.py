import os
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv, dotenv_values 

load_dotenv() 
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")

def getURI():
    
    uri = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@carefirst-dev.77movpn.mongodb.net/?retryWrites=true&w=majority"

    return uri

def getClient():
    
    uri = getURI()
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    return client

def addCollection(db_name, collection_name):

    client = getClient()
    db = client[db_name]
    collection = db[collection_name]

    print(db.list_collection_names())
    return

def deleteCollection(db_name, collection_name):
    client = getClient()
    
    db = client[db_name]
    db[collection_name].drop()

    print(f'collection names: {db.list_collection_names()}')
    return

def viewCollection(db_name, collection_name):

    client = getClient()

    db = client[db_name]
    print(db.list_collection_names())
    collection = db[collection_name]

    for x in collection.find():
        print(x)

    return


# addCollection(db_name="carefirstdb", collection_name="chat_histories")
#deleteCollection(db_name="carefirstdb", collection_name="messages")
viewCollection(db_name="carefirstdb", collection_name="messages")
