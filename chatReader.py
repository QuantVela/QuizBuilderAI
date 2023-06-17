from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os

api_key  = "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"
os.environ["OPENAI_API_KEY"] = api_key

chat = ChatOpenAI(temperature=0.0)

with open('ChatHistory.txt', 'r') as file:
    content = file.read()
# print(content)

template_string = """Please analyze the following conversation that is delimited by triple backticks and infer or guess based on the content:
What is the relationship between {roleAI} and {roleHuman}?
What is the age, occupation, and gender of {roleAI}?
What are the personality traits of {roleAI}?
What is the tone of {roleAI} in the conversation?
Does {roleAI} like to use emojis to express their reactions?
Extract 10 rounds of typical dialogue, including messages from {roleHuman} and responses from {roleAI}.
conversation: ```{conversation}```
"""
roleAI = "Hou"
roleHuman = "茜茜"
prompt_template = ChatPromptTemplate.from_template(template_string)
messages = prompt_template.format_messages(
                    roleAI=roleAI,
                    roleHuman=roleHuman,
                    conversation=content)
response = chat(messages)
print(response.content)

# to do: output in json, including {relationship},{age},{occupation},{gender},{personality},{tone},{emoji},{dialogue}

