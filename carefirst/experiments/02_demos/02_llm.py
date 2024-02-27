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

# load in chatbot
from llm import *


##################### demo

def ChatDemo(question):

    result = ChatChain(question)

    # if guardrails are alerted:
    if isinstance(result, str):      
        return result, None, None, None, None, None, None

    scenarios = ExtractNode({'node':result['node'],
                             'scenarios': str(result['docs'][0].metadata['scenarios'])})

    page_num = 'page ' + str(result['docs'][0].metadata['page'] + 1)
    document = result["docs"][0].metadata["source"].replace('../data/guidelines/', '')
    source = page_num + ' of ' + document
    
    output = (result["answer"], 
              result["history"]["chat_history"], 
              result["question"], 
              result["node"],
              scenarios, 
              result["docs"][0].page_content,
              source)
    
    return output

import gradio as gr

try:
    demo.close()
    print("Previous demo closed")
except:
    print("No demo running")

with gr.Blocks() as demo:

    gr.Markdown(
"""
## CAREFirst - Conversation demo
Steps taken:
1. Red Cross pdf was converted to text 
2. Text was converted to embeddings with sentence-transformers all-mpnet-base-v2
3. Information is retrieved based on similarity to the query with Facebook AI Similarity Search (Faiss) Vector Database
4. GPT-3.5 turbo takes in context and conversation history to answer questions    
5. NeMo guardrails to respond immediately to call 911 given certain input
6. Identify when a follow up question is required based on extracted relationships in the data.           
""")
    with gr.Row():
        with gr.Column():
            inputs = gr.Textbox(label="Question", lines=1)
            btn = gr.Button("Ask")
        with gr.Column():
            answer = gr.Textbox(label="Answer", lines=1)
    with gr.Row():
        examples = gr.Examples(examples = ["What to do if Cuts?",
                                           "how do you treat abrasions?",
                                           "What to do if you get a sting?",
                                           "How to remove Splinters",
                                           "How do you treat a sprain?",
                                           "Which medicine to take if I get a mild fever?"],
                                inputs = [inputs])
    with gr.Row():
        with gr.Column():   
            history = gr.Textbox(label="Conversation History", lines=1)
        with gr.Column(): 
            with gr.Row():
                reword = gr.Textbox(label="Reworded Question", lines=1)
            with gr.Row():
                node = gr.Textbox(label="Identified node and relationship", lines=1)
            with gr.Row():
                scenarios = gr.Textbox(label="Possible scenarios", lines=1)
        with gr.Column():
            with gr.Row():
                page_content = gr.Textbox(label="Document Content", lines=1)
            with gr.Row():
                reference = gr.Textbox(label="Reference", lines=1)
    
    btn.click(fn=ChatDemo, 
              inputs=[inputs], 
              outputs=[answer, history, reword, node, scenarios, page_content, reference])

demo.launch()
