# packages required
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.prompts.prompt import PromptTemplate
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.prompts.prompt import PromptTemplate
from langchain.schema import format_document
import os
import pandas as pd
import qdrant_client
from datetime import datetime


#######################################
# Set up
#######################################


EXISTS = True
COLLECTION_NAME = "redcross_v3"
QDRANT_URL = os.getenv("POETRY_QDRANT_URL")
QDRANT_KEY = os.getenv("POETRY_QDRANT_KEY")

docs = pd.read_pickle("./data/guidelines/redcross_w_metadata_v3.pickle")
# default is "sentence-transformers/all-mpnet-base-v2"
embeddings = HuggingFaceEmbeddings()
# by default accesses existing collection

if EXISTS:
    client = qdrant_client.QdrantClient(
        QDRANT_URL,
        api_key=QDRANT_KEY
    )

    db = Qdrant(
        client=client, collection_name=COLLECTION_NAME, 
        embeddings=embeddings,
    )
else:
    db = Qdrant.from_documents(
        docs,
        embeddings,
        url=QDRANT_URL,
        prefer_grpc=True,
        api_key=QDRANT_KEY,
        collection_name=COLLECTION_NAME,
        force_recreate=True
    )


#######################################
# The retriever
#######################################

# initialize the bm25 retriever 
bm25_retriever = BM25Retriever.from_documents(
    docs, 
    )
bm25_retriever.k = 1

def Retriever(query, k=2, tag=None):
    question = query["question"]["standalone_question"]
    tag = query['keywords']['tag']
    keywords = " ".join(query['keywords']['keywords'])
    print(tag)
    print(keywords)
    
    if tag != "None":

        qdrant_retriever = db.as_retriever(search_kwargs={"k": k,
                                                   "filter":{"Tags":tag}})

    else:
        qdrant_retriever = db.as_retriever(search_kwargs={"k": k,})

    retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, qdrant_retriever], weights=[0.5, 0.5]
    )
    start_time = datetime.now()
    retrieved_docs = retriever.invoke(question + '\n' + keywords)
    end_time = datetime.now()
    print('Retrieval Duration: {}'.format(end_time - start_time))
    return retrieved_docs


# document processing
DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

def CombineDocuments(docs, 
                     document_prompt=DEFAULT_DOCUMENT_PROMPT, 
                     document_separator="\n\n================================\n\n"):
    
    doc_strings = [format_document(doc, document_prompt) for doc in docs]

    return document_separator.join(doc_strings)

