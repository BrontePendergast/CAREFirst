from operator import itemgetter
from datetime import datetime

# orchestration
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_community.llms import HuggingFaceHub
from langchain_openai import ChatOpenAI
from langchain_core.messages import get_buffer_string
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory
# from langchain_community.chat_message_histories import MongoDBChatMessageHistory
from langchain_mongodb import MongoDBChatMessageHistory


# carefirst functions
from src. retrieval import Retriever, CombineDocuments
from src. refinement import ExtractScenarios, ExtractNode, node_parser, NODE_PROMPT, FOLLOW_UP_PROMPT
from src.summarization import ANSWER_PROMPT, CONDENSE_QUESTION_PROMPT, message_parser, keyword_parser, KEYWORD_PROMPT
from src.guardrails import guardrail_prompt, guardrails_run

# Env Variables
from dotenv import load_dotenv, dotenv_values 
import os
load_dotenv() 

#######################################
# LLMs
#######################################


MODEL = "gpt-3.5-turbo-1106"
MODEL_ANSWER = "mistralai/Mistral-7B-Instruct-v0.2"

def SelectLLM(model_name="gpt-3.5-turbo-1106", huggingface=False):

    if huggingface:
        # See https://huggingface.co/models?pipeline_tag=text-generation&sort=downloads for some other options
        repo_id = model_name #"mistralai/Mistral-7B-v0.1"  

        llm = HuggingFaceHub(
            repo_id=repo_id, model_kwargs={"temperature": 0.1, 
                                           "max_new_tokens": 1000, 
                                           "return_full_text": False,
                                           "num_beams": 4}
            )
    
    else:
        llm = ChatOpenAI(model_name=model_name, temperature = 0.1)
    
    return llm

# # huggingface models
# llm_answer = SelectLLM(model_name = MODEL_ANSWER,
#                        huggingface = True)

# gpt
llm_answer = SelectLLM(model_name = MODEL,
                       huggingface = False)

llm = SelectLLM(model_name = MODEL,
                huggingface = False)


#######################################
# Conversation history
#######################################


MONGODB_PASSWORD = os.getenv("POETRY_MONGODB_PASSWORD")
MONGODB_USERNAME = os.getenv("POETRY_MONGODB_USERNAME")
DATABASE_NAME = "carefirstdb"
COLLECTION_NAME = "chat_history"
CONNECTION_STRING = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@carefirst-dev.77movpn.mongodb.net/?retryWrites=true&w=majority"

# memory - reduce to the 3 most recent messages
memory = ConversationBufferWindowMemory(
        return_messages=True, output_key="answer", input_key="question", k = 3
    )

#######################################
# Chatbot chains
#######################################


# first we'll calculate the standalone question
standalone_question = (
    {
        "question": lambda x: x["question"],
        "chat_history": lambda x: get_buffer_string(x["chat_history"]) or "No chat history",
        "format_instructions": lambda x: message_parser.get_format_instructions()
    }
    | CONDENSE_QUESTION_PROMPT
    | llm
    | message_parser
    | dict
)


# first we'll calculate the standalone question
keywords = (
    {
        "question": lambda x: x["question"],
        "chat_history": lambda x: get_buffer_string(x["chat_history"]) or "No chat history",
        "format_instructions": lambda x: keyword_parser.get_format_instructions()
    }
    | KEYWORD_PROMPT
    | llm
    | keyword_parser
    | dict
)


# next, we'll check the knowledge graph of retrieved information
get_knowledge_graph = (
    {
        "question": itemgetter("question"), 
        "keywords": itemgetter("keywords"),
        "graph": lambda x: ExtractScenarios(x["docs"]),
        "format_instructions": lambda x: node_parser.get_format_instructions()
    }
    | NODE_PROMPT
    | llm
    | node_parser 
    | dict
)


# get the required keys for the next step
graph = (
    {
        "question": itemgetter("question"),
        "node": get_knowledge_graph,
        "docs": itemgetter("docs")
    } 
)  


# Function to check if follow up is required or direct answer
def RequireQuestion(info):
    # by default answer the question, unless a follow up can be determined
    answer_chain = (
        {
            "question": lambda x: info["question"], 
            "context": lambda x: info["context"]
        } 
        | ANSWER_PROMPT 
        | llm_answer
    )
        
    # follow ups aren't on by default to allow for testing and evaluation
    if info["follow_up"]: 

        if info['node']['identified'] == 'Many':
            try:
                graph = ExtractNode({"scenarios": info["scenarios"], 
                                     "node": info["node"]})
                if graph == 'Failed':
                    raise Exception("follow up failed")
                
                answer_chain = (
                    {
                        "question": lambda x: info["question"], 
                        "graph": lambda x: graph
                    }
                    | FOLLOW_UP_PROMPT 
                    | llm_answer
                )
            except: print(f"follow up failed with node: {info['node']}")

    return answer_chain


# function to check guardrail response before proceeding with answer
def AnswerDecision(info):

    print(f"quardrail answer: {info['guardrail_answer']}")

    if info["guardrail_answer"] in ["Your medical situation may be critical. Please call EMS/9-1-1", 
                                    "I'm sorry, I can't respond to that.",
                                    "Hello! Thanks for using Carefirst AI, how can I assist you?",
                                    "You're welcome! Thanks for using Carefirst AI.",
                                    "If you have any more questions or need further information, feel free to ask."]:
        return info["guardrail_answer"]
    else:
            
        x = info["actual_answer"]

        final_chain = (
            {
                "question": lambda y : x["question"],
                "node": lambda y: x["node"],
                "scenarios": lambda y: ExtractScenarios(x["docs"]),
                "context": lambda y : CombineDocuments(x["docs"]),
                "follow_up": lambda y: info["follow_up"]
            } 
            | RunnableLambda(RequireQuestion)
        )

    return final_chain | StrOutputParser()


#######################################
# Chatbot application
#######################################


def ChatChain(question, conversation_id = 'Test456', demo = False, guardrails = False, followup = False):
    
    # First we add a step to load memory
    # This adds a "memory" key to the input object
    loaded_memory = RunnablePassthrough.assign(
        chat_history=RunnableLambda(memory.load_memory_variables) | itemgetter("history"),
    )

    # Add Mongo History to chain
    ## Create history object from langchain_community.chat_message_histories
    mongo_history = MongoDBChatMessageHistory(
      connection_string=CONNECTION_STRING, 
      database_name=DATABASE_NAME,
      collection_name=COLLECTION_NAME,
      session_id=conversation_id
    )
    ## Create chat_history [{"Human": " "}, {"AI": " "}]
    ## https://python.langchain.com/docs/integrations/memory/mongodb_chat_message_history
    chat_history = mongo_history.messages
    print(chat_history)

    # guardrails aren't on by default to allow for testing and evaluation
    if guardrails:
        guardrails_run = guardrails_run
    else:
        def guardrails_run(info):
            return "Guardrails are not implemented"

    # And now we put it all together!
    chain = (
          loaded_memory 
        | { # run question and keyword prompt in parallel
            "question": standalone_question,
            "keywords": keywords
          }
        | { # document retrieval
            "question": lambda x: x["question"]["standalone_question"],
            "docs": RunnableLambda(Retriever),
            "keywords": lambda x: x["keywords"]["keywords"],
            "original_question": lambda x: question
          }
        | { # run in parallel
            "guardrail_answer": RunnableLambda(guardrails_run),
            "actual_answer": graph,
            "follow_up": lambda x: followup
          }
        | { # Determine whether to give guardrail answer, follow up question or answer from document
            "history": loaded_memory | {"chat_history": lambda x: get_buffer_string(x["chat_history"]) or "No chat history"},
            "question": lambda x: x["actual_answer"]["question"],
            "node": lambda x: x["actual_answer"]["node"],
            "answer": RunnableLambda(AnswerDecision),
            "docs": lambda x: x["actual_answer"]["docs"],
          }            
        )
    
    # run chain
    result = chain.invoke({"question": question})

    # store answer in memory
    memory.save_context({"question": question},
                        {"answer": result["answer"]})
    

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
        "timestamp": datetime.now(),
        "model": MODEL
    }

    return response
