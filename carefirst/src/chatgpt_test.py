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

# Add your OpenAI API key
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 
openai.api_key = os.getenv("OPENAI_API_KEY")

from llm_js import ChatChain

result = ChatChain('What kind of cream should I use for a burn', '77')
#print(result)
#print(type(result))
for key in result:
    print(key)
    print(result[key])
    print(type(result[key]))

