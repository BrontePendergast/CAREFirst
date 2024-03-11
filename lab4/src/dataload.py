from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import pickle


def load_and_store_embeddings(dir = '../data/guidelines/', path = 'redcross_guidelines.pdf'):
    # load and split document by page
    loader = PyPDFLoader(dir + path)
    pages = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    docs = text_splitter.split_documents(pages)

    # store text output as pickle
    with open(dir + path[:-4] + '.pickle', 'wb') as f:
        pickle.dump(pages, f)

    # default is "sentence-transformers/all-mpnet-base-v2"
    embeddings = HuggingFaceEmbeddings()

    db = FAISS.from_documents(docs, embeddings)
    db.save_local(dir + path[:-4] + "faiss_index")

    return f"PDF has converted to text and then to embeddings and stored here {dir + path[:-4]+ 'faiss_index'}"


pdfs = ['redcross_guidelines.pdf', 
        'ifrc_guidelines.pdf', 
        'who_guidelines.pdf']


# convert all pdfs
for pdf in pdfs:
    load_and_store_embeddings(path = pdf)
