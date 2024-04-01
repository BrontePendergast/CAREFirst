# packages required
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# guardrails
from nemoguardrails import RailsConfig, LLMRails
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails

#######################################
# Guardrails
#######################################


# simple prompt to have minimal impact on latency
guardrail_prompt = ChatPromptTemplate.from_template("Should I answer this question? \n Respond only with 'Yes' or 'No'\n Question: {question} ")
output_parser = StrOutputParser()

config = RailsConfig.from_path("data/config")

guardrails = LLMRails(config)

def guardrails_run(info):
     rewritten_question = info["question"]
     original_question = info["original_question"]
     res = guardrails.generate(prompt=f'{original_question}, additionally {rewritten_question}')
     return res