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
        gr.Markdown(
"""
## User Experience      
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
        
    with gr.Accordion("Model Design"):
        with gr.Row():
            gr.Image('experiments/02_demos/images/model_steps_v3.png') 

    with gr.Accordion("Engineered Flow "):
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

