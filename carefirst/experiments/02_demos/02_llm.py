# packages required
import sys
import os
import random

# run from carefirst directory
os.chdir(os.getcwd() + '/../../')
# append a new directory to sys.path
sys.path.append(sys.path[0] + '/../../src/')
sys.path.append(sys.path[0] + '/../../')

# load in chatbot
from llm import *

# create a new test ID for this demo, to remain constant while demo is running
test_id = "Test" + str(random.randint(0,1000))

##################### demo

def ChatDemo(question):

    result = ChatChain(question = question, 
                       conversation_id = test_id,
                       demo = True,
                       guardrails = True, 
                       followup = True)

    all_options = []
    for doc in result['docs']:
        all_options.extend(doc.metadata['scenarios']) 

    scenarios = ExtractNode({'node':result['node'],
                             'scenarios': str(all_options)})

    page_num = 'page ' + str(result['docs'][0].metadata['page'] + 1)
    document = result["docs"][0].metadata["source"].replace('../data/guidelines/', '')
    source = page_num + ' of ' + document
    
    output = (result["answer"], 
              result["history"]["chat_history"], 
              result["question"], 
              result["node"],
              scenarios, 
              "\n".join([doc.page_content for doc in result["docs"]]),
              source)
    
    return output


import gradio as gr

try:
    demo.close()
    print("Previous demo closed")
except:
    print("No demo running")

with gr.Blocks() as demo:

    with gr.Row():
        gr.Image('experiments/02_demos/images/carefirst_banner.png')
    with gr.Row():
        with gr.Column():
                inputs = gr.Textbox(label="Question", lines=1)
                btn = gr.Button("Ask")
        with gr.Column():
                answer = gr.Textbox(label="Answer", lines=1)
        
    with gr.Accordion("Retrieval Augmented Generation"):
        with gr.Row():
            with gr.Column():
                gr.Image('experiments/02_demos/images/rag.png') 
            with gr.Column(): 
                reword = gr.Textbox(label="Reworded Question", lines=1)
                history = gr.Textbox(label="Conversation History", lines=1)
            with gr.Column():
                with gr.Row():
                    page_content = gr.Textbox(label="Document Content", lines=1)
                    reference = gr.Textbox(label="Reference", lines=1)
        
    with gr.Accordion("Refinement"):
        with gr.Row():
            with gr.Column():
                gr.Image('experiments/02_demos/images/refinement.png') 
            with gr.Column():
                node = gr.Textbox(label="Identified node and relationship", lines=1)
            with gr.Column():
                scenarios = gr.Textbox(label="Possible scenarios", lines=1)    

    with gr.Accordion("Guardrails"):
        with gr.Row():
            with gr.Column(scale = 0.33):
                gr.Image('experiments/02_demos/images/guardrails.png')  

    btn.click(fn=ChatDemo, 
              inputs=[inputs], 
              outputs=[answer, history, reword, node, scenarios, page_content, reference])
    

demo.launch()

