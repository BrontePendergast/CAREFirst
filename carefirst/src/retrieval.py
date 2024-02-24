# packages required
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# load in db and embeddings
# default is "sentence-transformers/all-mpnet-base-v2"
embeddings = HuggingFaceEmbeddings()
db = FAISS.load_local("./data/guidelines/redcross_guidelinesfaiss_index", embeddings)

def retrieval(query):
    
    # run similarity search
    answer = db.similarity_search(query)

    # extract required information
    page_content = answer[0].page_content
    page_num = 'page ' + str(answer[0].metadata['page'] + 1)
    document = answer[0].metadata['source'].replace('../data/guidelines/', '')

    source = page_num + ' of ' + document
    
    return page_content, source


##################### demo

# import gradio as gr

# try:
#     demo.close()
#     print("Previous demo closed")
# except:
#     print("No demo running")

# demo = gr.Interface(
#     title = "CAREFirst - Retrieval demo",
#     description = """
#     Steps taken:
#     1. Red Cross pdf was converted to text 
#     2. Text was converted to embeddings with sentence-transformers all-mpnet-base-v2
#     3. Information is retrieved based on similarity to the query with Facebook AI Similarity Search (Faiss) Vector Database
#     """,
#     fn=retrieval,
#     inputs=[gr.Textbox(label="Question", lines=1)],
#     outputs=[gr.Textbox(label="Guidelines", lines=10), gr.Textbox(label="Reference", lines=1)],
#     examples = ["What to do if Cuts?",
#                 "how do you treat abrasions?",
#                 "What to do if you get a sting?",
#                 "How to remove Splinters",
#                 "How do you treat a sprain?",
#                 "Which medicine to take if I get a mild fever?"]
# )

# demo.launch()