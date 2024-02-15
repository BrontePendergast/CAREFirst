import openai
from operator import itemgetter

# orchestration
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_community.llms import HuggingFaceHub
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import format_document
from langchain_core.messages import AIMessage, HumanMessage, get_buffer_string
from langchain_core.runnables import RunnableParallel
from langchain.memory import ConversationBufferMemory

# scripts
from retrieval import *

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
        llm = ChatOpenAI(model_name=model_name)
    
    return llm


llm = SelectLLM()


#######################################
# chatbot
#######################################


memory = ConversationBufferMemory(
        return_messages=True, output_key="answer", input_key="question"
    )

def ChatChain(question):

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

    # And now we put it all together!
    final_chain = loaded_memory | standalone_question | retrieved_documents | answer

    # run chain
    result = final_chain.invoke({"question": question})

    # store answer in memory
    memory.save_context({"question": question}, 
                        {"answer": result["answer"].content})

    return result["answer"].content, result["history"]["chat_history"], result["question"], result["docs"]
