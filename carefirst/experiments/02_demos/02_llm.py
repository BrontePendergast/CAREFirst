# packages required
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

import sys
import os

# run from carefirst directory
os.chdir(os.getcwd() + '/../../')
# append a new directory to sys.path
sys.path.append(sys.path[0] + '/../../src/')
sys.path.append(sys.path[0] + '/../../')

# load in db and embeddings
from llm import *


##################### demo


import gradio as gr

try:
    demo.close()
    print("Previous demo closed")
except:
    print("No demo running")

demo = gr.Interface(
    title = "CAREFirst - Conversation demo",
    description = """
    Steps taken:
    1. Red Cross pdf was converted to text 
    2. Text was converted to embeddings with sentence-transformers all-mpnet-base-v2
    3. Information is retrieved based on similarity to the query with Facebook AI Similarity Search (Faiss) Vector Database
    4. GPT-3.5 turbo takes in context and conversation history to answer questions
    """,
    fn=ChatChain,
    inputs=[gr.Textbox(label="Question", lines=1)],
    outputs=[gr.Textbox(label="Answer", lines=10), gr.Textbox(label="Reference", lines=1)],
    examples = ["What to do if Cuts?",
                "how do you treat abrasions?",
                "What to do if you get a sting?",
                "How to remove Splinters",
                "How do you treat a sprain?",
                "Which medicine to take if I get a mild fever?"]
)

demo.launch()

