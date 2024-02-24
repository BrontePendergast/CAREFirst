# Mongo
import pymongo
from pymongo import MongoClient
from datetime import datetime

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["carefirstdb"]
history = db["history"]
for x in history.find():
  print(x)

#db["history"].drop()

# client.'feedback_table'.drop()
print(db.list_collection_names())




# history.find_one_and_update(
#   {'conversation_id': '55'},
#   {'$set': {'message_id': 20}}, upsert=True)

# Retrieve History for a conversation_id
# conversation_history = history.find_one({'conversation_id': '55'})["history"]
# print(conversation_history)

# Store Conversation History

# client.drop_database('history')


# def insertFeedback(conversation_id, history, timestamp):

#   feedback_entry = { "conversation_id": conversation_id
#                     , "history": history
#                     , "timestamp": timestamp}
      
#   x = feedback.insert_one(feedback_entry)


#   # print list of the _id values of the inserted documents:
# insertFeedback('999', 'my history', datetime.now())


#result = feedback.find_one_by({'conversation_id': '55'})

# client.drop_database('feedback_table')
# feedback = db["feedback_table"]

# def insertFeedback(conversation_id, message_id, user_feedback, question):

#   feedback_entry = { "conversation_id": conversation_id, "messages": [
#     { "message_id": message_id, "feedback" : user_feedback, "question": question}
#     ]}
      
#   x = feedback.insert_one(feedback_entry)

#   # print list of the _id values of the inserted documents:
#   for x in feedback.find():
#       print(x)

