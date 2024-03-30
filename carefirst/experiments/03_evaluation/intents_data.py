import json
import os
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from random import sample

from langchain_community.document_transformers import DoctranQATransformer

openai_api_key = os.getenv("POETRY_OPENAI_API_KEY")
openai_api_model = 'gpt-3.5-turbo'


###########################
# intents metadata
###########################


rc_docs = pd.read_pickle(r'../../data/guidelines/redcross_guidelines.pickle')
# only first aid contents - TODO move this filtering to dataload script as single source of truth
rc_docs = rc_docs[13:205]
# transform to set of questions and answers
qa_transformer = DoctranQATransformer(openai_api_key=openai_api_key, openai_api_model=openai_api_model)
transformed_document = qa_transformer.transform_documents(rc_docs)

# store text output as pickle
with open('../../data/intent/redcross_qna.pickle', 'wb') as f:
    pickle.dump(transformed_document, f)


###########################
# transform for testing
###########################
    

# we need {question, answer, associated page}
# we will then use this for:
# 1. response similarity - with the prescribed answer compared to the tool's answer and the Out-Of-The-Box GPT answer (e.g. demonstrate low hallucination)
# 2. retrieval accuracy - rate at which the correct page is identified.
# we should do this for slightly reworded questions, spelling mistakes, uncertain language to demonstrate how this impacts performance. 

with open('../../data/intent/redcross_qna.pickle', 'rb') as f:
    transformed_document = pickle.load(f)

def TestingTransformation(doc):
  
    doc_list = []

    # one page has multiple questions
    for qna in doc.metadata["questions_and_answers"]:
       
        metadata = {"source": doc.metadata["source"],
                    "page": doc.metadata["page"]}

        metadata["question"] = qna["question"]
        metadata["answer"] = qna["answer"]

        # split them into individual records
        doc_list.append(metadata)

    return doc_list

# final list for testing
transformed_qna = []

# run function across each page
for doc in transformed_document:

    qna_list = TestingTransformation(doc)

    transformed_qna = transformed_qna + qna_list


###########################
# clean testing set
###########################
     
# when a page has no information, such as a divider/contents page, gpt hallucinates and still asks questions
# remove such pages using the metadata associated with the page.
     
chapters = pd.read_pickle(r'../../data/guidelines/redcross_chapter_titles.pickle')
chapter_pages = [chapter["page"] for chapter in chapters]

with open('../../data/intent/redcross_testing.pickle', 'rb') as f:
    transformed_qna = pickle.load(f)

# remove title pages from qna
final_qna = []

for doc in transformed_qna:
  # only keep metadata for non chapter title pages
    if doc["page"] not in chapter_pages:
        final_qna .append(doc)

# ready for diversification
qna_df = pd.DataFrame(final_qna)
qna_df.to_csv('../../data/intent/redcross_testing_pre_translate.csv')


###############################
# diversify using google sheets 
###############################
     
# this step is done in google sheets
# https://docs.google.com/spreadsheets/d/1vA2UDQGRdvgauHejv8-WjVEz2-BJ1AtBQaLrnZzSjFw/edit?usp=sharing
     
###############################
# testing split
###############################
     
# read in newly expanded testing data
qna_expanded = pd.read_csv('../../data/intent/redcross_testing_post_translate.csv')
qna_expanded = qna_expanded.drop(['Unnamed: 0', 'language conversion'], axis = 1)

qna_dict = qna_expanded.to_dict('records')

validation, test = train_test_split(qna_dict, test_size=0.33, random_state=2024)

print(f'Size of validation: {len(validation)} questions')
print(f'Size of test: {len(test)} questions')

###############################
# samples for quick dev
###############################

# 10% sample
sample_validation = sample(validation, k = int(len(validation)*0.1))

print(f'Size of sample validation: {len(sample_validation)} questions')

###############################
# save all files
###############################

# hold out for testing
with open('../../data/intent/redcross_testing.pickle', 'wb') as f:
     pickle.dump(test, f)

# validation/tuning sample
with open('../../data/intent/redcross_validation.pickle', 'wb') as f:
     pickle.dump(validation, f)

# validation/tuning smaller sample for quick iteration
with open('../../data/intent/redcross_validation_10_percent.pickle', 'wb') as f:
     pickle.dump(sample_validation, f)