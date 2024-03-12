# import openai
import json
import pandas as pd
# from sentence_transformers import SentenceTransformer, util
# from rouge import Rouge
# from openai import OpenAI
import os
import sys


# client = OpenAI(api_key=os.getenv('POETRY_OPENAI_API_KEY'))

# Initialize SBERT model
# sbert_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Initialize ROUGE scorer
# rouge = Rouge()



# run from carefirst directory
os.chdir(os.getcwd() + '/../../')
# append a new directory to sys.path
sys.path.append(sys.path[0] + '/../../src/')
sys.path.append(sys.path[0] + '/../../')

from llm import *
print('successfully imported')

question=('what are cuts?')
result = ChatChain(question)
print(result['answer'])

# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")        
# llm = ChatOpenAI(model_name=model_name, openai_api_key=openai.api_key) # JS add openai key

# model = 'gpt-3.5-turbo-0125'

# def gpt3_response(prompt):
#     response = client.Completion.create(
#         engine=model,
#         prompt=prompt,
#         max_tokens=50
#     )
#     return response.choices[0].text.strip()

# # TODO add in intents data - must be mapped to correct page numbers as well
# # examples = ["What to do if Cuts?",
# #                 "how do you treat abrasions?",
# #                 "What to do if you get a sting?",
# #                 "How to remove Splinters",
# #                 "How do you treat a sprain?",
# #                 "Which medicine to take if I get a mild fever?"]
# import json
# import pandas as pd
 
# #TODO replace with redcross_testing
# # Opening JSON file
# f = open('../../data/intent/intents.json')
# intents = json.load(f)
# intents = intents['intents']


# intent_count = len(intents)
# scores = {'cos_sim_gpt3': [],
#           'cos_sim_chatbot': [],
#           'cos_sim_answers': [],
#           'rouge_gpt3': [],
#           'rouge_chatbot': [],
#           'page_num': []}

# sum_rouge = 0
# sum_sbert = 0
# sum_page_num = 0

# for intent in intents:
#     for prompt in intent['patterns']:
#         # Get response from GPT-3.5
#         gpt3_answer = gpt3_response(prompt)
#         # TODO import 02_llm.py ChatDemo
#         chatbot_answer, _, _, _, _, _, source = ChatDemo(prompt)

#         embeddings = sbert_model.encode([prompt, gpt3_answer, chatbot_answer])
#         scores['cos_sim_gpt3'].append(util.cos_sim(embeddings[0], embeddings[1]))
#         scores['cos_sim_chatbot'].append(util.cos_sim(embeddings[0], embeddings[2]))
#         scores['cos_sim_answers'].append(util.cos_sim(embeddings[1], embeddings[2]))

#         scores['rouge_gpt3'].append(rouge.get_scores(gpt3_answer, intent['responses'][0]))
#         scores['rouge_chatbot'].append(rouge.get_scores(chatbot_answer, intent['responses'][0]))

#         # TODO implement page number retreival

#         print("GPT-3.5 Response:", gpt3_answer)