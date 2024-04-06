# packages required
from langchain.output_parsers.pydantic import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder


#######################################
# Question summarization
#######################################


# reframe the question
class message(BaseModel):
    standalone_question: str = Field(description="The standalone message")


message_parser = PydanticOutputParser(pydantic_object=message)


question_system_prompt = SystemMessagePromptTemplate.from_template(
    template="""
    Given the chat history and the latest human message, rephrase the latest human message to be a standalone message incorporating any context from the chat history.
    The message should continue to be written from the human's perspective and your response should not answer their message. 
    Prioritise the information in the latest human message and make no changes to it if the chat history does not provide additional context.

    Example 1: No chat history

    Chat history: No chat history
    Latest Human Message: I have a cut
    standalone_question: I have a cut

    Example 2: Relevant chat history

    Chat history: 
        Human: I have a cut
        AI: Is it a shallow or deep cut
    Latest Human Message: It's shallow
    standalone_question: I have a shallow cut

    Example 3: Changing topic

    Chat history:
        Human: I have a cut
        AI: Treat it by cleaning it with water and applying a dry bandage
    Latest Human Message: How do I remove a splinter
    standalone_question: How do I remove a splinter

    Respond with the standalone message in JSON format
    {format_instructions}
    """)


question_human_prompt = HumanMessagePromptTemplate.from_template(
    template = "Please rewrite the human message: \n Chat history: \n{chat_history}\n ================== \n Latest Human Message: \n {question}", 
    input_variables=["question", "chat_history"]
    )


CONDENSE_QUESTION_PROMPT = ChatPromptTemplate.from_messages([question_system_prompt, 
                                                             question_human_prompt])


#######################################
# keyword summarization
#######################################


# reframe the question
class keyword(BaseModel):
    tag: str = Field(description="The tagged question type", default = 'None')
    keywords: list[str] = Field(description="Key words and synonyms referencing the ailment", default = 'None')


keyword_parser = PydanticOutputParser(pydantic_object=keyword)


keyword_system_prompt = SystemMessagePromptTemplate.from_template(
    template="""
    Given the chat history and the current message, identify the keywords from the message.
    Prioritise the information in the current message and make no changes to it if the chat history is not relevant.

    This message will match one of the following tags of the type of message:
    - "Prevention" 
    - "Care" (what to do)
    - "Call"
    - "Signs and symptoms"
    - "Causes"
    - "None"

    The standalone message will have a keyword for the medical practise, ailment or injury. Identify this and provide commonly used synonyms to that word.
    If there are no synonyms, do not provide any additional words. Do not include keywords that change the details of the word to be more specifc to one ailment.
    
    Respond with the associated tag and keywords in JSON format
    {format_instructions}
    """)


keyword_human_prompt = HumanMessagePromptTemplate.from_template(
    template = "Chat history: \n{chat_history}\n Human Message: \n {question}\n please provide the tag and keywords", 
    input_variables=["question", "chat_history"]
    )


KEYWORD_PROMPT = ChatPromptTemplate.from_messages([keyword_system_prompt,
                                                   keyword_human_prompt,
                                                   MessagesPlaceholder(variable_name="conversation", optional=True)])

#######################################
# Answer summarization
#######################################


# prompt to provide answer
answer_system_prompt = SystemMessagePromptTemplate.from_template(
template = """
Answer the question based only on the following context. 
The context may include synonyms to what is provided in the question:
{context}

The user asked: {question}

Assistant:

""",
input_variables = ["context", "question"]
)

ANSWER_PROMPT = ChatPromptTemplate.from_messages([answer_system_prompt])