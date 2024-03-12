# import openai
import json
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from rouge import Rouge
from openai import OpenAI
import os
import sys


client = OpenAI(api_key=os.getenv('POETRY_OPENAI_API_KEY'))

#Initialize SBERT model
sbert_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

#Initialize ROUGE scorer
rouge = Rouge()



# run from carefirst directory
os.chdir(os.getcwd() + '/../../')
# append a new directory to sys.path
sys.path.append(sys.path[0] + '/../../src/')
sys.path.append(sys.path[0] + '/../../')

from src.llm import *

print('successfully imported')

question=('what are cuts?')
result = ChatChain(question)
print(result['answer'])

openai.api_key = os.getenv("POETRY_OPENAI_API_KEY")        


model = 'gpt-3.5-turbo-0125'
def gpt3_response(prompt, model):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=50
    )
    return response.choices[0].message.content

# TODO add in intents data - must be mapped to correct page numbers as well
# examples = ["What to do if Cuts?",
#                 "how do you treat abrasions?",
#                 "What to do if you get a sting?",
#                 "How to remove Splinters",
#                 "How do you treat a sprain?",
#                 "Which medicine to take if I get a mild fever?"]
import json
import pandas as pd
 
#TODO replace with redcross_testing
# Opening JSON file
# f = open('../../data/intent/intents.json')
# intents = json.load(f)
# intents = intents['intents']

intents = pd.read_pickle(r'./data/intent/redcross_testing.pickle')


intent_count = len(intents)
# scores = {'cos_sim_gpt3': [],
#           'cos_sim_chatbot': [],
#           'cos_sim_answers': [],
#           'rouge_gpt3': [],
#           'rouge_chatbot': [],
#           'page_num': []}

scores = []

# sum_rouge = 0
# sum_sbert = 0
# sum_page_num = 0

import re
import random

scores = []
for intent in intents:
    #
    prompt = intent['question']
    # similar to the model adding 1 to account for 0 index start
    page = intent['page'] + 1
    answer = intent['answer']
    # Get response from GPT-3.5
    gpt3_answer = gpt3_response(prompt, model)
    # TODO import 02_llm.py ChatDemo
    test_id = "Test" + str(random.randint(0,1000))
    chatbot_response = ChatChain(prompt, conversation_id=test_id)
    chatbot_page = int(''.join(re.findall(r'\d+', chatbot_response["source"])))
    chatbot_answer = chatbot_response['answer']
    #
    embeddings = sbert_model.encode([answer, gpt3_answer, chatbot_answer])
    #
    # changed the output to a dictionary because it'll be easier to evaluate
    results = {
     'question': prompt,
     'expected_answer': answer,
     'gpt3_answer': gpt3_answer,
     'chatbot_answer': chatbot_answer,
     'page': page,
     'chatbot_page': chatbot_page,
     'cos_sim_gpt3' : util.cos_sim(embeddings[0], embeddings[1])[0].numpy()[0],
     'cos_sim_chatbot': util.cos_sim(embeddings[0], embeddings[2])[0].numpy()[0],
     'cos_sim_answers': util.cos_sim(embeddings[1], embeddings[2])[0].numpy()[0],
     'rouge_1_f1_gpt3': float(rouge.get_scores(gpt3_answer, intent['answer'])[0]['rouge-1']['f']),
     'rouge_1_f1_chatbot': float(rouge.get_scores(chatbot_answer, intent['answer'])[0]['rouge-1']['f']),
     'rouge_2_f1_gpt3': float(rouge.get_scores(gpt3_answer, intent['answer'])[0]['rouge-2']['f']),
     'rouge_2_f1_chatbot': float(rouge.get_scores(chatbot_answer, intent['answer'])[0]['rouge-2']['f']),                    
     'rouge_l_f1_gpt3': float(rouge.get_scores(gpt3_answer, intent['answer'])[0]['rouge-l']['f']),
     'rouge_l_f1_chatbot': float(rouge.get_scores(chatbot_answer, intent['answer'])[0]['rouge-l']['f'])
    }
    # append to a list
    scores.append(results)

scores_df = pd.DataFrame(scores)
scores_df['page_match'] = scores_df.apply(lambda x: 1 if x['page'] == x['chatbot_page'] else 0, axis = 1)
scores_df.to_csv('./data/intent/model_evaluation_v1.csv')

# average similarity with cosine and rouge
print(scores_df[[
           'page_match',
           'cos_sim_gpt3', 
           'cos_sim_chatbot', 
           'cos_sim_answers', 
           'rouge_1_f1_gpt3', 
           'rouge_1_f1_chatbot',
           'rouge_2_f1_gpt3', 
           'rouge_2_f1_chatbot',
           'rouge_l_f1_gpt3', 
           'rouge_l_f1_chatbot',
           ]].mean())

from sklearn.metrics import confusion_matrix

# classification result of the source pages used
confusion_matrix(scores_df['page'], scores_df['chatbot_page'])

scores_df[['page','chatbot_page']]