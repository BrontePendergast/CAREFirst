# packages required
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# guardrails
from nemoguardrails import RailsConfig, LLMRails
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails

#######################################
# Guardrails
#######################################

config = RailsConfig.from_path("data/config")

guardrails = LLMRails(config)

def guardrails_func(info):
     rewritten_question = info["question"]
     original_question = info["original_question"]
     res = guardrails.generate(prompt=f'{original_question}, additionally {rewritten_question}')
     return res