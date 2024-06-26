import os
import pandas as pd
import pickle
import re
from tenacity import retry, stop_after_delay, stop_after_attempt
from typing import List
from enum import Enum

from langchain.prompts import PromptTemplate
from langchain.output_parsers.pydantic import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.chat_models import ChatOpenAI

openai_api_key = os.getenv("POETRY_OPENAI_API_KEY")
openai_api_model = 'gpt-3.5-turbo-0125'

# load in db and embeddings
from dataload import load_and_store_text


###########################
# guideline metadata
###########################


documents = pd.read_pickle(r'../data/guidelines/redcross_guidelines.pickle')

class TagsEnum(str, Enum):
    prevention = "Prevention", 
    care = "Care",
    call = "Call",
    signs = "Signs and symptoms",
    causes = "Causes"

class ScenarioTitles(BaseModel, use_enum_values=True):
    Medical_Scenarios: list[str] = Field(description="a list of all medical titles discussed in the text")
    Tags: list[TagsEnum] = Field(description="a list of all themes being discussed in the text")

parser = PydanticOutputParser(pydantic_object=ScenarioTitles)

prompt = PromptTemplate(
    template="""Extract all titles that represent distinct medical scenarios from the following text and all tags of the themes.
    Text: 
    {content}
    \n{format_instructions}""",
    input_variables=["content"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

model = ChatOpenAI(temperature=0.1)

@retry(stop=(stop_after_delay(100)|stop_after_attempt(5)))
def chain(info):
    chain = prompt | model | parser | dict
    return chain.invoke(info)

# add in a flag for title pages
for doc in documents:
    print(doc.page_content)
    # add in extracted properties
    properties = chain({"content": doc.page_content})
    print(properties)
    doc.metadata["Scenario_titles"] = properties['Medical_Scenarios']
    doc.metadata["Tags"] = list(set(properties['Tags']))
    print(doc.metadata["Tags"])
    # get number of words
    page_content = doc.page_content
    num_words = len(page_content.split())
    # short pages represent chapter title pages
    if num_words < 10:
        doc.metadata["Title_page"] = True
    else:
        doc.metadata["Title_page"] = False

# separate out title pages
title_pages = [{"chapter_title": re.sub(r'[0-9]+', '', doc.page_content), 
                "page": doc.metadata["page"],
                "idx": idx} for idx, doc in enumerate(documents) if doc.metadata["Title_page"] == True]

# create the lead chapter page in df
title_df = pd.DataFrame(title_pages)
title_df["lead_page"] = title_df["page"].shift(periods = -1, fill_value = 205)
title_df["lead_idx"] = title_df["idx"].shift(periods = -1, fill_value = 205)


###########################
# chapter knowledge graph
###########################
    

class GraphNode(BaseModel):
    node: str = Field(description="A grouping name for the medical scenarios")
    relationships: list[str] = Field(description="the medical scenarios that fall within this group")

# Define your desired data structure.
class KnowledgeGraph(BaseModel):
    graph: list[GraphNode] = Field(description="a list of the groups and associated relationships")

# Set up a parser + inject instructions into the prompt template.
parser = PydanticOutputParser(pydantic_object=KnowledgeGraph)

prompt = PromptTemplate(
    template="""
      Group the scenarios below together into high level groups (nodes) of related topics (relationships) from the chapter on {chapter}.
      For example, all types of bites should be in the one group. All types of stings should be in another group.
      If the scenario is already labelled as the high level group, do not include it as a related topic.
      Do not include irrelevant groupings, such scenarios can stay on individual nodes.
      \n{format_instructions}
      Scenarios:
      {scenarios}\n""",
    input_variables=["chapter", "scenarios"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

model = ChatOpenAI(temperature=0.1)

@retry(stop=(stop_after_delay(100)|stop_after_attempt(5)))
def chain(info):
    chain = prompt | model | parser | dict
    return chain.invoke(info)

scenarios = {}
graphs = []

for row in range(len(title_df)):
    chapter = title_df['chapter_title'][row]
    # create a key for the chapter
    scenarios[chapter] = {}
    # prepare the nested scenarios
    scenarios[chapter]['Scenarios'] = []
    # for each page 
    for idx in range(title_df['idx'][row], title_df['lead_idx'][row]):
        # add the scenario to the complete chapter list
        try:
            page_scenarios = documents[idx].metadata['Scenario_titles']
            scenarios[chapter]['Scenarios'] += page_scenarios
        except:
            print("ran out of indices")
    scenarios[chapter]['Scenarios'] = list(set(scenarios[chapter]['Scenarios']))
    print(scenarios[chapter]['Scenarios'])
    # get a knowledge graph of these scenarios
    knowledge_graph = chain({"chapter": chapter, "scenarios": scenarios[chapter]['Scenarios']})
    # add Other as fallback
    fallback = []
    for scenario in knowledge_graph['graph']:
        scenario_dict = dict(scenario)
        scenario_dict['relationships'].append('Other')
        fallback.append(scenario_dict)
    # update knowledge_graph
    knowledge_graph = fallback
    print(knowledge_graph)
    scenarios[chapter]['Knowledge Graph'] = knowledge_graph
    graphs.append(knowledge_graph)

title_df['scenarios'] = graphs

# remove title pages from metadata and add on key for chapter title and scenarios
final_extracted_documents = []

for doc in documents:
    new_df = title_df
    # identify which row corresponds to the chapter this page is in
    new_df["page_i"] = doc.metadata["page"]
    filtered_df = new_df[new_df["page_i"].between(new_df["page"], new_df["lead_page"])].reset_index(drop = True)
    # add key for chapter title
    doc.metadata["Chapter_title"] = filtered_df["chapter_title"][0]
    # add key for scenario knowledge graph
    doc.metadata["scenarios"] = filtered_df["scenarios"][0]
    # only keep metadata for non chapter title pages
    if doc.metadata["Title_page"] == False:
        final_extracted_documents.append(doc)


# store transformed data
with open('../data/guidelines/redcross_w_metadata_v4.pickle', 'wb') as f:
    pickle.dump(final_extracted_documents, f)

