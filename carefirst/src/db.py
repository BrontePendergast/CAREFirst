# Mongo
import pymongo
from pymongo import MongoClient

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["carefirstdb"]
client.drop_database('feedback_table')
feedback = db["feedback_table"]

def insertFeedback(conversation_id, message_id, user_feedback):

  feedback_entry = { "conversation_id": conversation_id, "messages": [
    { "message_id": message_id, "feedback" : user_feedback}
    ]}
      
  x = feedback.insert_one(feedback_entry)

  # print list of the _id values of the inserted documents:
  for x in feedback.find():
      print(x)

