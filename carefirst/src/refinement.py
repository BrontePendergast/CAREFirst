# packages required
from langchain.output_parsers.pydantic import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.prompts.prompt import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import format_document


#######################################
# Identifying node in graph
#######################################


# knowledge graph node identification prompt
class Node(BaseModel):
    node: str = Field(description="The high level topic node that the user's question is referring to", default = 'None')
    relationship: str = Field(description="The specific topic if mentioned by the user", default = 'None')


node_parser = PydanticOutputParser(pydantic_object=Node)


NODE_PROMPT = PromptTemplate(
    template="""
    The user has provided the following message: \n {question}. 
    Given the following knowledge graph of nodes and their related topics, which node in the graph does this response relate to and which relationship is of interest? 
    Respond with the value of the 'node'. 
    If the user's response references a specific 'relationship' to a topic that is included in the knowledge graph, reference this as the associated relationship. 

    Remember that the 'relationship' will be 'None' if it is unclear from the user message which scenario the user is interested in. 
    Remember that the 'relationship' will be 'Other' when the users specific scenario isn't included.
    Remember that the node should already exist as a node in the graph. The relationship should already exist in connection to that node.
    Remember that the user may use synonyms or less confident wording and you should infer the appropriate node and relationship.
    For example, synonyms from this user's message include: {keywords}
    
    Think step by step.

    Provide your response in JSON format with the identified node and relationship

    Knowledge graph:
    {graph}
    """,
    input_variables=["question", "keywords", "graph"],
)


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