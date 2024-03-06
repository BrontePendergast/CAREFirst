import openai
import os
from operator import itemgetter

# JS add dotenv
from dotenv import load_dotenv, dotenv_values 


# orchestration
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

# JS ADD
from langchain_community.llms import HuggingFaceHub
from datetime import datetime

#from langchain_openai import ChatOpenAI

from langchain_community.chat_models import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import format_document
from langchain_core.messages import AIMessage, HumanMessage, get_buffer_string
from langchain_core.runnables import RunnableParallel
from langchain.memory import ConversationBufferMemory

# scripts
#from retrieval import *  
from src.retrieval import *     # Jess add src.

# guardrails
from nemoguardrails import RailsConfig
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails


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
template = """Answer the question based only on the following context. The context may include synonyms to what is provided in the question:
{context}

Question: {question}
"""
ANSWER_PROMPT = ChatPromptTemplate.from_template(template)


# retrieval prompt
DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

def _combine_documents(
    docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"
):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)


#######################################
# Retriever
#######################################


retriever = db.as_retriever(search_kwargs={"k": 1})


#######################################
# LLMs
#######################################


def SelectLLM(model_name="gpt-3.5-turbo", huggingface=False):

    if huggingface:
        # See https://huggingface.co/models?pipeline_tag=text-generation&sort=downloads for some other options
        repo_id = model_name #"mistralai/Mistral-7B-v0.1"  

        llm = HuggingFaceHub(
            repo_id=repo_id, model_kwargs={"temperature": 0.5}#, "max_length": 200}
            )
    
    else:   
        load_dotenv()  # JS Add
        openai.api_key = os.getenv("OPENAI_API_KEY")        # JS Add
        llm = ChatOpenAI(model_name=model_name, openai_api_key=openai.api_key) # JS add openai key
    
    return llm


llm = SelectLLM()

#######################################
# Guardrails
#######################################

# simple prompt to have minimal impact on latency
prompt = ChatPromptTemplate.from_template("Answer No to this: {question}")
output_parser = StrOutputParser()

#config = RailsConfig.from_path("data/config")
#guardrails = RunnableRails(config, input_key="question", output_key="answer")


#######################################
# chatbot
#######################################


memory = ConversationBufferMemory(
        return_messages=True, output_key="answer", input_key="question"
    )

def ChatChain(question, conversation_id):

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


    # Now we construct the inputs for the final prompt
    final_inputs = {
        "context": lambda x: _combine_documents(x["docs"]),
        "question": itemgetter("question"),
    }

    # And finally, we do the part that returns the answers
    answer = {
        "history": loaded_memory,
        "question": itemgetter("question"),
        "answer": final_inputs | ANSWER_PROMPT | llm,
        "docs": itemgetter("docs"),
    }

    # simple_chain = prompt | llm 
    # chain_with_guardrails = guardrails | simple_chain 

    # guardrail_result = chain_with_guardrails.invoke({"question": question})

    # if guardrail_result['answer'] in ["Your medical situation is critical. Please call EMS/9-1-1", "I'm sorry, I can't respond to that."]:

    #     memory.save_context({"question": question}, 
    #                         {"answer": guardrail_result['answer']})
        
    #     result = {
    #     "history": None,
    #     "question": None,
    #     "answer": guardrail_result['answer'],
    #     "docs": None,
    #     }
    
    #     return result["answer"], result["history"], result["question"], result["docs"]
    
    # And now we put it all together!
    final_chain = loaded_memory | standalone_question | retrieved_documents | answer

    # run chain
    result = final_chain.invoke({"question": question})

    # # store answer in memory
    memory.save_context({"question": question}, 
                        {"answer": result["answer"].content})

    #output = result["answer"].content, result["history"]["chat_history"], result["question"], result["docs"]
    
    # JS Add Below
    timestamp = datetime.now()
    output = conversation_id, result["answer"].content, result["question"], result["docs"][0].metadata, timestamp

    #return output

    # # # JS Add Below to convert to dictionary

    keys =  ["conversation_id", "answer", "query", "source", "timestamp_responseout"]
    values = [output[0], output[1], output[2], output[3], output[4]]

    output_dict = dict(zip(keys, values))

    return output_dict
     
