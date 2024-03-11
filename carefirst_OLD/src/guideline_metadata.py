import json
import os
import pandas as pd
import pickle
import re

from langchain.schema import Document
from langchain_community.document_transformers import DoctranPropertyExtractor

openai_api_key = os.getenv("POETRY_OPENAI_API_KEY")
openai_api_model = 'gpt-3.5-turbo-0125'


###########################
# guideline metadata
###########################


rc_docs = pd.read_pickle(r'../data/guidelines/redcross_guidelines.pickle')

# TODO move this filtering to dataload script as single source of truth
documents = rc_docs[13:205]

info_properties = [
    {
        "name": "Title",
        "description": "Title of the content. This is required based on the text.",
        "type": "string",
        "required": True
    },
    {
        "name":"Common Causes", 
        "description":"A list of the common causes of this ailment only if writen in the context.",
        "type":"array",
        "items":{
            "name": "cause",
            "description": "One common cause described",
            "type": "string"
        },
        "required": False
    },
    {
        "name":"Prevention", 
        "description":"A list of the preventions only if writen in the context.",
        "type":"array",
        "items":{
            "name": "step",
            "description": "One prevention step.",
            "type": "string"
        },
        "required": False
    },
    {
        "name":"What To Look For", 
        "description":"What signs and symptoms to look for only if writen in the context.",
        "type":"array",
        "items":{
            "name": "sign",
            "description": "One sign or symptom",
            "type": "string"
        },
        "required": False
    },
    {
        "name":"What To Do", 
        "description":"A list of steps for What should you do for this ailment based on a specific scenario, only if writen in the context.",
        "type":"array",
        "items":{
            "type": "object",
            "properties": {
                "Scenario": {
                    "description": "What scenario is this 'what to do' section covering.",
                    "type": "string"
                    },
                "Call":{
                    "description": "What does the subsection say for when to call 911 or seek other help. Do not write anything if this is not mentioned.",
                    "type": "string"
                    },
                "Care":{
                    "description": "What care instructions are provided in this what to do section.",
                    "type": "string"
                    }
                }
            },
        "required": False
    },
    {
        "name":"Other Information", 
        "description":"Other information provided in the context that doesn't fit the other properties.",
        "type":"array",
        "items":{
            "name": "information",
            "description": "Only information found in the context.",
            "type": "string"
        },
        "required": False
    },
]

property_extractor_info = DoctranPropertyExtractor(properties=info_properties,
                                                   openai_api_key=openai_api_key,
                                                   openai_api_model=openai_api_model)


extracted_documents = property_extractor_info.transform_documents(
    documents, properties=info_properties
)

# add in a flag for title pages
for doc in extracted_documents:

    page_content = doc.page_content
    num_words = len(page_content.split())

    if num_words < 10:
        doc.metadata["Title_page"] = True
    else:
        doc.metadata["Title_page"] = False

# separate out title pages
title_pages = [{"chapter_title": re.sub(r'[0-9]+', '', doc.page_content), "page": doc.metadata["page"]} for doc in extracted_documents if doc.metadata["Title_page"] == True]

with open('../data/guidelines/redcross_chapter_titles.pickle', 'wb') as f:
    pickle.dump(title_pages, f)

# create the lead chapter page in df
title_df = pd.DataFrame(title_pages)
title_df["lead_page"] = title_df["page"].shift(periods = -1, fill_value = 205)

# remove title pages from metadata and add on key for chapter title
final_extracted_documents = []

for doc in extracted_documents:
    
    new_df = title_df
    # identify which row corresponds to the chapter this page is in
    new_df["page_i"] = doc.metadata["page"]
    filtered_df = new_df[new_df["page_i"].between(new_df["page"], new_df["lead_page"])].reset_index(drop = True)
    # add key for chapter title
    doc.metadata["extracted_properties"]["Chapter_title"] = filtered_df["chapter_title"][0]
    # only keep metadata for non chapter title pages
    if doc.metadata["Title_page"] == False:
        final_extracted_documents.append(doc)


with open('../data/guidelines/redcross_guideline_metadata.pickle', 'wb') as f:
    pickle.dump(final_extracted_documents, f)


