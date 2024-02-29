import openai
import os

import pymongo
from pymongo import MongoClient
from pydantic_mongo import AbstractRepository, ObjectIdField
from langchain_community.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

import db_mongo

# OpenAI API key
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 
openai.api_key = os.getenv("OPENAI_API_KEY")

# Connect to MongoDBAtlas Database
connection_string = db_mongo.getURI()
database_name = "carefirstdb"

# Chat Message History
chat_message_history = MongoDBChatMessageHistory(
    session_id="test_session",
    connection_string=connection_string,
    database_name=database_name,
    collection_name="chat_histories",
)

chat_message_history.add_user_message("Hello 2")
chat_message_history.add_ai_message("Hi 2 ")

chat_message_history.add_user_message("Hello again 2")
chat_message_history.add_ai_message("Hi again 2")

# View Chat History
#print(chat_message_history)

# # Chain
# prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", "You are a helpful assistant."),
#         MessagesPlaceholder(variable_name="history"),
#         ("human", "{question}"),
#     ]
# )

# chain = prompt | ChatOpenAI()

# chain_with_history = RunnableWithMessageHistory(
#     chain,
#     lambda session_id: MongoDBChatMessageHistory(
#         session_id="test_session",
#         connection_string=connection_string,
#         database_name="carefirstdb",
#         collection_name="chat_histories",
#     ),
#     input_messages_key="question",
#     history_messages_key="history",
# )

# config = {"configurable": {"session_id": "conversation_id"}}

# chain_with_history.invoke({"question": "Hi! I'm bob"}, config=config)

# print(chain_with_history.get_session_history("test_session2"))


# View MongoDB Record
db_mongo.viewCollection(db_name="carefirstdb", collection_name="chat_histories")

# Delete MongoDB Collection
db_mongo.deleteCollection(db_name="carefirstdb", collection_name="chat_histories")