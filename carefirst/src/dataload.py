from langchain_community.document_loaders import PyPDFLoader
import pickle

def load_and_store_data(dir = '../data/guidelines/', path = 'redcross_guidelines.pdf'):
    # load and split document by page
    loader = PyPDFLoader(dir + path)
    pages = loader.load_and_split()

    # store output as pickle
    with open(dir + path[:-4] + '.pickle', 'wb') as f:
        pickle.dump(pages, f)

    return f"PDF has converted to text and stored here {dir + path[:-4]+ '.pickle'}"

pdfs = ['redcross_guidelines.pdf', 
        'ifrc_guidelines.pdf', 
        'who_guidelines.pdf']

# convert all pdfs
for pdf in pdfs:
    load_and_store_data(path = pdf)

# code to open again
with open('../data/guidelines/ifrc_guidelines.pickle', 'rb') as f:
   redcross = pickle.load(f)