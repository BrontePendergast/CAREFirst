# Mongo
import pymongo
from pymongo import MongoClient
from datetime import datetime

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from dotenv import load_dotenv, dotenv_values 
load_dotenv() 

def getMongoURL():
  MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
  uri = "mongodb+srv://rmarin:" + MONGODB_PASSWORD + "@carefirst-dev.77movpn.mongodb.net/?retryWrites=true&w=majority"
  
  # Create a new client and connect to the server
  client = MongoClient(uri, server_api=ServerApi('1'))

  # Send a ping to confirm a successful connection
  try:
      client.admin.command('ping')
      print("Pinged your deployment. You successfully connected to MongoDB!")
  except Exception as e:
      print(e)
  
  return uri



# client = pymongo.MongoClient("mongodb://localhost:27017/")

# database_name="carefirstdb"
# collection_name="chat_histories"

# db = client[database_name]
# history = db[collection_name]
# # db = client["carefirstdb"]
# # history = db["history"]


# for x in history.find():
#   print(x)

# #db["history"].drop()

# # client.'feedback_table'.drop()
# print(db.list_collection_names())

