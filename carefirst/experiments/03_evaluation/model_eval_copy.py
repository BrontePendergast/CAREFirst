##############################
# Set up
##############################

import pandas as pd
from sentence_transformers import SentenceTransformer, util
from rouge import Rouge
from openai import OpenAI
import os
import sys
from tenacity import retry, stop_after_delay, stop_after_attempt
import pandas as pd
import re

client = OpenAI(api_key=os.getenv('POETRY_OPENAI_API_KEY'))
# openai.api_key = os.getenv("POETRY_OPENAI_API_KEY")   

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

##############################
# Model functions
##############################

# example
question=('what are cuts?')
result = ChatChain(question)
print(result['answer'])


model = 'gpt-3.5-turbo-0125'
@retry(stop=(stop_after_delay(20)|stop_after_attempt(5)))
def gpt3_response(prompt, model):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=50
    )
    return response.choices[0].message.content

# gpt3_answer = gpt3_response(prompt, model)

@retry(stop=(stop_after_delay(20)|stop_after_attempt(5)))
def chatbot_response_fun(prompt):
    chatbot_response = ChatChain(prompt)
    return chatbot_response


##############################
# evaluation function
##############################


def evaluate_one_model(chatbot, 
                       chatbot_name, 
                       test_data_path = './data/intent/redcross_testing.pickle', 
                       output_data_path = './data/intent/model_evaluation_v1.csv'):
    #
    intents = pd.read_pickle(test_data_path)
    intent_count = len(intents)
    print(f"Total number of eval questions: {intent_count}")
    # initialize results
    scores = []
    #
    for intent in intents:
        # reset memory
        memory = ConversationBufferWindowMemory(
            return_messages=True, output_key="answer", input_key="question"
        )
        #
        prompt = intent['question']
        # similar to the model adding 1 to account for 0 index start
        page = intent['page'] + 1
        answer = intent['answer']
        # get response from carefirst
        chatbot_response = chatbot(prompt)
        chatbot_page = int(''.join(re.findall(r'\d+', chatbot_response["source"])))
        chatbot_answer = chatbot_response['answer']
        #
        embeddings = sbert_model.encode([answer, chatbot_answer])
        #
        # changed the output to a dictionary because it'll be easier to evaluate
        results = {
        'question': prompt,
        'expected_answer': answer,
        'chatbot_answer': chatbot_answer,
        'page': page,
        'chatbot_page': chatbot_page,
        f'cos_sim_{chatbot_name}': util.cos_sim(embeddings[0], embeddings[1])[0].numpy()[0],
        f'rouge_1_f1_{chatbot_name}': float(rouge.get_scores(chatbot_answer, intent['answer'])[0]['rouge-1']['f']),
        f'rouge_2_f1_{chatbot_name}': float(rouge.get_scores(chatbot_answer, intent['answer'])[0]['rouge-2']['f']),                    
        f'rouge_l_f1_{chatbot_name}': float(rouge.get_scores(chatbot_answer, intent['answer'])[0]['rouge-l']['f'])
        }       
        # append to a list
        scores.append(results)
        print(results)
        scores_df = pd.DataFrame(scores)
        scores_df['page_match'] = scores_df.apply(lambda x: 1 if x['page'] == x['chatbot_page'] else 0, axis = 1)
        scores_df.to_csv(output_data_path)
    #
    return scores_df


##############################
# run evaluation for Mistal 7b
##############################

# validation on smaller sample
scores_df = evaluate_one_model(chatbot = chatbot_response_fun, 
                       chatbot_name = 'gemma', 
                       test_data_path = './data/intent/redcross_validation_10_percent.pickle', 
                       output_data_path = './data/intent/model_evaluation_gemma_7b_it.csv')



