# packages required
import sys
import os
import random
from transformers import pipeline
import numpy as np
import io
import base64
from transformers import VitsModel, VitsTokenizer, AutoTokenizer
import torch
import scipy
from num2words import num2words
import re

# run from carefirst directory
os.chdir(os.getcwd() + '/../../')
# append a new directory to sys.path
sys.path.append(sys.path[0] + '/../../src/')
sys.path.append(sys.path[0] + '/../../')

# load in chatbot
from llm import *

# create a new test ID for this demo, to remain constant while demo is running
test_id = "Test" + str(random.randint(0,1000))

########################
# Audio
########################

transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")

# https://www.gradio.app/guides/real-time-speech-recognition
def transcribe(audio):
    sr, y = audio
    y = y.astype(np.float32)
    y /= np.max(np.abs(y))

    return transcriber({"sampling_rate": sr, "raw": y})["text"]

model = VitsModel.from_pretrained("facebook/mms-tts-eng")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-eng") #VitsTokenizer

# https://huggingface.co/docs/transformers/model_doc/vits
def text_to_speech(text):
    print(text)
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        output = model(**inputs)

    waveform = output.waveform[0]

    temp_file_path = "techno.wav"
    try:
        os.remove(temp_file_path)
        print("previous file deleted")
    except:
        print("file does not exist")

    scipy.io.wavfile.write(temp_file_path, rate=model.config.sampling_rate, data=waveform.numpy()) 

    return temp_file_path

# solution to autoplay found here https://github.com/gradio-app/gradio/issues/1349
def audio_file_to_html(audio_file: str) -> str:
    """
    Convert audio file to HTML audio player.

    Args:
        audio_file: Path to audio file

    Returns:
        audio_player: HTML audio player that auto-plays
    """
    # Read in audio file to audio_bytes

    audio_bytes = io.BytesIO()
    with open(audio_file, "rb") as f:
        audio_bytes.write(f.read())

    # Generate audio player HTML object for autoplay
    audio_bytes.seek(0)
    audio = base64.b64encode(audio_bytes.read()).decode("utf-8")
    audio_player = (
        f'<audio src="data:audio/mpeg;base64,{audio}" controls autoplay></audio>'
    )
    return audio_player

# https://michael-fuchs-python.netlify.app/2021/06/19/nlp-text-pre-processing-vii-special-cases/
def num_to_words(text):
    '''
    Convert Numbers to Words
    
    Args:
        text (str): String to which the function is to be applied, string
    
    Returns:
        Clean string with converted Numbers to Words
    ''' 
    after_spliting = text.split()

    for index in range(len(after_spliting)):

        if re.search(r'.*(9\-1\-1)', after_spliting[index]):
            after_spliting[index] = "nine one one"
        elif after_spliting[index] == '911':
            after_spliting[index] = "nine one one"
        elif after_spliting[index] == 'EMS':
            after_spliting[index] = "Emergency Medical Services"
        elif after_spliting[index].isdigit():
            after_spliting[index] = num2words(after_spliting[index])

    numbers_to_words = ' '.join(after_spliting)

    return numbers_to_words

######################## 
# Demo
########################

def ChatDemo(text_question = None, audio_question = None):

    if text_question is not None and text_question != '':
        print("text question is being used")
    elif audio_question is not None:
        text_question = transcribe(audio_question)
        print("audio question is being used")


    result = ChatChain(question = text_question, 
                       conversation_id = test_id,
                       demo = True,
                       guardrails = True, 
                       followup = True)

    # process digits
    answer_for_speech = num_to_words(result["answer"])
    # text to speech
    speech_path = text_to_speech(answer_for_speech)

    all_options = []
    for doc in result['docs']:
        all_options.extend(doc.metadata['scenarios']) 

    scenarios = ExtractNode({'node':result['node'],
                             'scenarios': str(all_options)})

    page_num = 'page ' + str(result['docs'][0].metadata['page'] + 1)
    document = result["docs"][0].metadata["source"].replace('../data/guidelines/', '')
    source = page_num + ' of ' + document
    
    output = (text_question, # transcribed question
              result["answer"], 
              audio_file_to_html(speech_path),
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
                audio = gr.Audio(sources=["microphone"])
                btn = gr.Button("Ask")
        with gr.Column():
            with gr.Row():
                transcribed = gr.Textbox(label="Transcribed question", lines=1)
            with gr.Row():
                answer = gr.Textbox(label="Answer", lines=1)
            with gr.Row():
                speech = gr.HTML()

    btn.click(fn=ChatDemo, 
              inputs=[inputs, audio], 
              outputs=[transcribed, answer, speech])
    

demo.launch()

