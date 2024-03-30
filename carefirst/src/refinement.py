# packages required
from langchain.output_parsers.pydantic import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.prompts.prompt import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import format_document

from enum import Enum

#######################################
# Identifying node in graph
#######################################

class ScenarioEnum(str, Enum):
    known = "One", 
    other = "Other",
    many = "Many"

# knowledge graph node identification prompt
class Node(BaseModel):
    node: str = Field(description="The high level topic node that the user's question is referring to", default = 'None')
    thought: str = Field(description="One sentence thought behind choosing whether the relationship is One, Many or Other")
    identified: ScenarioEnum = Field(description="Description of whether the related scenario known, other or none", default = 'None')

node_parser = PydanticOutputParser(pydantic_object=Node)

node_system_prompt = SystemMessagePromptTemplate.from_template(
    template="""
    The user will provide a message and your role is to link this message to the knowledge graph.

    Knowledge graph:
    {graph}

    ======================
    
    Given the knowledge graph of nodes and their related topics, which node in the graph does this message relate to? 

    In the Thought key of your response, answer the following in one sentence:
    Consider the relationships linked to this node in the knowledge graph. Could the user's message be about 'One' or 'Many' of these relationships? 
    If there are 'Many', is there 'One' that is the most likely or could they all be equally likely because there is no additional context?
    Could the user's message be about a 'Other' relationship not mentioned here? 
    Does a synonyms from this user's message help determine the relationship? synonyms: {keywords}

    In the Identified key, provide the answer of 'One', 'Many', 'Other'

    format response in JSON:
    {format_instructions}
    """,
    input_variables=["graph", "keywords", "format_instructions"])
    # Does a synonyms from this user's message help determine the relationship? synonyms: {keywords}

node_human_prompt = HumanMessagePromptTemplate.from_template(
    template = "Human Message: \n {question}", 
    input_variables=["question"]
    )


NODE_PROMPT = ChatPromptTemplate.from_messages([node_system_prompt,
                                                node_human_prompt])

    # 

# extract scenarios
SCENARIO_PROMPT = PromptTemplate.from_template(template="{scenarios}")


def ExtractScenarios(docs, 
                     document_prompt=SCENARIO_PROMPT, 
                     document_separator="+"):
    
    doc_strings = [format_document(doc, document_prompt) for doc in docs]

    return document_separator.join(doc_strings)


# function to extract the node:
def ExtractNode(info):

    scenarios = eval(info['scenarios'])
    # run through list
    for scenario in scenarios:
        if info['node']['node'] == scenario['node']:
            # return the one identified by the model
            return scenario
    # exception otherwise, default back to answering question
    return 'Failed'


#######################################
# Follow up question if required
#######################################


# follow up prompt
class FollowUp(BaseModel):
    output: str = Field(description="a question to send back to the user")


# Set up a parser + inject instructions into the prompt template.
follow_parser = PydanticOutputParser(pydantic_object=FollowUp)


FOLLOW_UP_SYSTEM_PROMPT = SystemMessagePromptTemplate.from_template(
    template="""
    The user has a question and you have narrowed down that the answer is related to several scenarios. 
    Your role is to ask the user a follow up question to identify which specific scenario they are referring to.
    """
    )


FOLLOW_UP_HUMAN_PROMPT = HumanMessagePromptTemplate.from_template(
    template = "User question: \n {question} \n Scenarios: \n{graph}\n Assistant:", 
    input_variables=["question", "graph"]
    )


FOLLOW_UP_PROMPT = ChatPromptTemplate.from_messages([FOLLOW_UP_SYSTEM_PROMPT, 
                                                  FOLLOW_UP_HUMAN_PROMPT])