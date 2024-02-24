import openai
import os

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