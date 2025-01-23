
#from langchain_community.llms import OpenAI
#from langchain.llms import OpenAI

from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import OpenAI

from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

import pandas as pd

# Load data into a pandas DataFrame
df = pd.read_csv("titanic.csv")

# Create a pandas agent
agent = create_pandas_dataframe_agent(OpenAI(temperature=0), df, verbose=False)

# Interact with the DataFrame using natural language queries
question = "How many rows are there?"
print('Q:', question)
result = agent.invoke(question)
print('R:', result['output'])  # Output: "There are 891 rows in the dataframe."
question = "what is the correlation of survival rate regarding the traveling class?"
print('Q:', question)
result = agent.invoke(question)
print('R:', result['output'])  # Output: "There are 891 rows in the dataframe."
question = "What is the youngest and oldest age in the data?"
print('Q:', question)
result = agent.invoke(question)
print('R:', result['output'])  # Output: "There are 891 rows in the dataframe."
question = "Were older or yonger people more likely to survive?"
print('Q:', question)
result = agent.invoke(question)
print('R:', result['output'])  # Output: "There are 891 rows in the dataframe."
question = "Plot the survivor count for each sex"
print('Q:', question)
result = agent.invoke(question)
print('R:', result['output'])  # Output: "There are 891 rows in the dataframe."
question = "Plot the survivor count for each sexi, and use different colored bars."
print('Q:', question)
result = agent.invoke(question)
print('R:', result['output'])  # Output: "There are 891 rows in the dataframe."
