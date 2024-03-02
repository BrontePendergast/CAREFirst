# packages required
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# load in db and embeddings
# default is "sentence-transformers/all-mpnet-base-v2"
embeddings = HuggingFaceEmbeddings()
# assumes you're running from carefirst directory and this db by default
db = FAISS.load_local("./data/guidelines/redcross_guidelinesfaiss_index", embeddings)

def retrieval(query, db):
    
    # run similarity search
    answer = db.similarity_search(query)

    # extract required information
    page_content = answer[0].page_content
    page_num = 'page ' + str(answer[0].metadata['page'] + 1)
    document = answer[0].metadata['source'].replace('../data/guidelines/', '')

    source = page_num + ' of ' + document
    
    return page_content, source



