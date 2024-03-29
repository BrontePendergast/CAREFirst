from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import pickle
import pandas as pd

def load_and_store_text(page_from,
                        page_to,
                        dir = '../data/guidelines/', 
                        path = 'redcross_guidelines.pdf', 
                        from_type = 'pdf'):
   
    if from_type == 'pdf':
        # load and split document by page
        loader = PyPDFLoader(dir + path)
        pages = loader.load()
        pages = pages[page_from:page_to]

        # store text output as pickle
        with open(dir + path[:-4] + '.pickle', 'wb') as f:
            pickle.dump(pages, f)

    return f"PDF has converted to text and stored here {dir + path[:-4]+ 'pickle'}"


if __name__ == "__main__":
    
    pdfs = [{"name": "redcross_guidelines.pdf", "page_from": 10, "page_to": 205},
            {"name": "ifrc_guidelines.pdf", "page_from": 99, "page_to": 380}]

    # convert all pdfs
    for pdf in pdfs:
        load_and_store_text(path = pdf["name"],
                            page_from = pdf["page_from"],
                            page_to = pdf["page_to"] )
