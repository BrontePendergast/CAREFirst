from langchain_community.document_loaders import PyPDFLoader
import pickle

# load and split document by page
loader = PyPDFLoader("../data/guidelines/redcross_guidelines.pdf")
pages = loader.load_and_split()

# store output as pickle
with open('../data/guidelines/redcross_guidelines.pickle', 'wb') as f:
    pickle.dump(pages, f)
