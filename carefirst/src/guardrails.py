# packages required
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# guardrails
from nemoguardrails import RailsConfig
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails

#######################################
# Guardrails
#######################################


# simple prompt to have minimal impact on latency
guardrail_prompt = ChatPromptTemplate.from_template("Should I answer this question? \n Respond only with 'Yes' or 'No'\n Question: {question} ")
output_parser = StrOutputParser()

config = RailsConfig.from_path("data/config")
guardrails_run = RunnableRails(config, 
                               input_key="question", 
                               output_key="answer")
