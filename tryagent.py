from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from tools.voicer import VoiceTool
from langchain import OpenAI
from langchain.tools import tool
from langchain.callbacks import get_openai_callback
import re
import time

api_key = "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"
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613", openai_api_key=api_key)

@tool("TextTool", return_direct=True)
def split_sentence(text: str) -> list[str]:
    """Split sentence when the output is text type"""
    if sentence.endswith('。'):
        sentence = sentence[:-1]   
    split_sentences = re.split('，|！|。',sentence)   
    return split_sentences

voice_tool = VoiceTool()

tools = [
    Tool(
        name="VoiceTool",
        func=voice_tool.run,
        description="Convert text to speech when user ask your response is voice type"
    ),
    Tool(
        name="TextTool",
        func=split_sentence.run,
        description="Split sentence when the output is text type"
    )
]

agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)

start_time = time.time()

with get_openai_callback() as cb:
    agent.run("I want to hear your voice.")
    print(f"\n\nTotal Tokens:{cb.total_tokens}")
end_time = time.time()  # capture the end time
response_time = end_time - start_time  # calculate the response time
print(f"The response time is {response_time} seconds.")