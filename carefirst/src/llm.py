import openai
import os
from operator import itemgetter
from typing import List
import ast
import pandas as pd
from datetime import datetime

# orchestration
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_community.llms import HuggingFaceHub
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import format_document
from langchain_core.messages import AIMessage, HumanMessage, get_buffer_string, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers.pydantic import PydanticOutputParser
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_community.chat_message_histories import MongoDBChatMessageHistory

# guardrails
from nemoguardrails import RailsConfig
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails
from tenacity import retry, stop_after_attempt


#######################################
# Prompts
#######################################


#https://python.langchain.com/docs/expression_language/cookbook/retrieval
# reframe as one complete question
_template = """
Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)


# prompt to provide answer
template = """
Answer the question based only on the following context. 
The context may include synonyms to what is provided in the question:
{context}

Question: {question}
"""
ANSWER_PROMPT = ChatPromptTemplate.from_template(template)


# retrieval prompt
DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

def _combine_documents(docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)


# knowledge graph node identification prompt
class Node(BaseModel):
    node: str = Field(description="The high level topic node that the user's question is referring to", default = 'None')
    relationship: str = Field(description="The specific topic if mentioned by the user", default = 'None')

# function to extract the node:
def ExtractNode(info):
    scenarios = ast.literal_eval(info['scenarios'])
    # run through list
    for scenario in scenarios:
        if info['node']['node'] == scenario['node']:
            identified = scenario
    # return the one identified by the model
    return identified

SCENARIO_PROMPT = PromptTemplate.from_template(template="{scenarios}")

def _extract_documents(docs, document_prompt=SCENARIO_PROMPT, document_separator="\n\n"):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)

node_parser = PydanticOutputParser(pydantic_object=Node)

node_prompt = PromptTemplate(
    template="""
    The user has provided the following response: \n {question}. 
    Given the following knowledge graph of nodes and their related topics, which node in the graph does this response relate to? 
    Respond with the value of the 'node'. 
    The 'relationship' will be 'None' if there is no way to choose between existing relationships in the Knowledge graph. 
    If the user's response references a specific 'relationship' to a topic that is included in the knowledge graph, include this in your response. 
    Remember the topic should already exist in the graph.
    Think step by step.

    Provide your response in JSON format with the identified node and relationship

    Knowledge graph:
    {graph}
    """,
    input_variables=["question", "graph"],
)


# follow up prompt
class FollowUp(BaseModel):
    output: str = Field(description="a question to send back to the user")

# Set up a parser + inject instructions into the prompt template.
follow_parser = PydanticOutputParser(pydantic_object=FollowUp)

follow_system_prompt = SystemMessagePromptTemplate.from_template(
    template="""
    The user has a question and you have narrowed down that the answer is related to several scenarios. 
    Ask the user a follow up question to identify which specific scenario they are referring to.
    """)

follow_human_prompt = HumanMessagePromptTemplate.from_template(template = "User question: \n {question} \n Scenarios: \n{graph}", input_variables=["question", "graph"])

follow_prompt = ChatPromptTemplate.from_messages([follow_system_prompt, follow_human_prompt])


#######################################
# Retriever
#######################################


QDRANT_URL = os.getenv("POETRY_QDRANT_URL")
QDRANT_KEY = os.getenv("POETRY_QDRANT_KEY")

docs = pd.read_pickle("./data/guidelines/redcross_w_metadata.pickle")
# default is "sentence-transformers/all-mpnet-base-v2"
embeddings = HuggingFaceEmbeddings()
# by default accesses existing collection
db = Qdrant.from_documents(
    docs,
    embeddings,
    url=QDRANT_URL,
    prefer_grpc=True,
    api_key=QDRANT_KEY,
    collection_name="redcross",
)
retriever = db.as_retriever(search_kwargs={"k": 1})


#######################################
# LLMs
#######################################


def SelectLLM(model_name="gpt-3.5-turbo-1106", huggingface=False):

    if huggingface:
        # See https://huggingface.co/models?pipeline_tag=text-generation&sort=downloads for some other options
        repo_id = model_name #"mistralai/Mistral-7B-v0.1"  

        llm = HuggingFaceHub(
            repo_id=repo_id, model_kwargs={"temperature": 0.5}#, "max_length": 200}
            )
    
    else:
        llm = ChatOpenAI(model_name=model_name)
    
    return llm


llm = SelectLLM()


#######################################
# Guardrails
#######################################


# simple prompt to have minimal impact on latency
prompt = ChatPromptTemplate.from_template("Answer No to this: {question}")
output_parser = StrOutputParser()

config = RailsConfig.from_path("data/config")
guardrails = RunnableRails(config, input_key="question", output_key="answer")


#######################################
# Conversation history
#######################################


MONGODB_PASSWORD = os.getenv("POETRY_MONGODB_PASSWORD")
MONGODB_USERNAME = os.getenv("POETRY_MONGODB_USERNAME")
DATABASE_NAME = "carefirstdb"
CONNECTION_STRING = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@carefirst-dev.77movpn.mongodb.net/?retryWrites=true&w=majority"


#######################################
# Chatbot modules
#######################################


def ChatChain(question, conversation_id = 'Test123', demo = False):

    # load message history
    message_history = MongoDBChatMessageHistory(
        session_id=conversation_id,
        connection_string=CONNECTION_STRING,
        database_name=DATABASE_NAME,
        collection_name="chat_histories",
        )

    # buffer the memory from history
    memory = ConversationBufferMemory(
        return_messages=True, output_key="answer", input_key="question", chat_memory=message_history)
    
    # First we add a step to load memory
    # This adds a "memory" key to the input object
    loaded_memory = RunnablePassthrough.assign(
        chat_history=RunnableLambda(memory.load_memory_variables) | itemgetter("history"),
    )

    # Now we calculate the standalone question
    standalone_question = {
        "standalone_question": {
            "question": lambda x: x["question"],
            "chat_history": lambda x: get_buffer_string(x["chat_history"]),
        }
        | CONDENSE_QUESTION_PROMPT
        | llm
        | StrOutputParser(),
    }

    # Now we retrieve the documents
    retrieved_documents = {
        "docs": itemgetter("standalone_question") | retriever ,
        "question": lambda x: x["standalone_question"],
    }

    # knowledge graph of retrieved information
    get_knowledge_graph = ({
        "question": itemgetter("question"), 
        "graph": lambda x: _extract_documents(x["docs"])
        }
        | node_prompt 
               | llm
               | node_parser 
               | dict
    )

    graph = ({"question": itemgetter("question"),
              "node": get_knowledge_graph,
              "docs": itemgetter("docs")} 
    )   

    # when a follow up question is required 
    follow_up = (follow_prompt
                 | llm
    )

    # Function to check if follow up is required or direct answer
    def RequireQuestion(info):

        if info['node']['relationship'] == 'None':
            answer_chain = {"question": lambda x: info["question"], 
                            "graph": {"scenarios": lambda x : info["scenarios"], 
                                      "node": lambda x: info['node']} | RunnableLambda(ExtractNode)} | follow_up
        else:
            answer_chain = {"question": lambda x: info["question"], 
                            "context": lambda x: info["context"]} | ANSWER_PROMPT | llm

        return answer_chain


    final_chain = ({"question": itemgetter("question"), 
                   "node": itemgetter("node"),
                   "scenarios": lambda x: _extract_documents(x["docs"]),
                   "context": lambda x: _combine_documents(x["docs"])} 
                   | RunnableLambda(RequireQuestion)
    )

    # And finally, we do the part that returns the answers
    answer = {
        "history": loaded_memory,
        "question": itemgetter("question"),
        "node": itemgetter("node"),
        "answer": final_chain | StrOutputParser(),
        "docs": itemgetter("docs"),
    }

    simple_chain = prompt | llm 
    chain_with_guardrails = guardrails | simple_chain 

    guardrail_result = chain_with_guardrails.invoke({"question": question})

    if guardrail_result['answer'] in ["Your medical situation is critical. Please call EMS/9-1-1", "I'm sorry, I can't respond to that."]:

        message_history.add_user_message(question)
        message_history.add_ai_message(guardrail_result['answer'])

        return guardrail_result['answer']
    
    # And now we put it all together!
    chain = loaded_memory | standalone_question | retrieved_documents | graph | answer
    
    # run chain
    result = chain.invoke({"question": question})

    # store answer in memory
    message_history.add_user_message(question)
    message_history.add_ai_message(result["answer"])

    # Demo expects all output fields
    if demo:
        return result
    
    page_num = 'page ' + str(result['docs'][0].metadata['page'] + 1)
    document = result["docs"][0].metadata["source"].replace('../data/guidelines/', '')
    source = page_num + ' of ' + document

    # expected response from the app
    response = {
        "conversation_id": conversation_id,
        "answer": result["answer"],
        "query": question,
        "source": source,
        "timestamp": datetime.now()
    }

    return response
