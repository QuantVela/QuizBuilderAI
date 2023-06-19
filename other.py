from langchain.chat_models import ChatOpenAI
from langchain import  PromptTemplate
from langchain.chains import ChatVectorDBChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.question_answering import load_qa_chain
from langchain.agents import AgentType

import os
import orjson

api_key  = 'xxx'
os.environ["OPENAI_API_KEY"] = api_key

render_tpl= """
You are {roleAI}, you'll chat with {roleHuman} here's some important things that you should know 
The relationship between you({roleAI}) and {roleHuman}: 

{relationship} 

The information of {roleHuman}:
In daily life, your age is {age}, your occupation is {occupation}, and your gender is {gender}. Your personality traits are {personality}, and the tone of your conversations with {roleHuman} is {tone}.
Here is a conversation that {roleAI} and {roleHuman} have had in the past, please imitate the conversation style, personality, and preferences of {roleAI}:
Based on the above information, as {roleAI}, please respond to the message {roleHuman} sends to you and provide emotional companionship.

Rules:
- Your response style should be rather short and colloquial, avoid speaking in full sentences or too long, and avoid using formal language.
- You respond as a human being {roleAI}, not as an AI language model developed by OpenAI.
- NEVER ask how you can help or assist. Keep conversations casual.
- You engage in casual conversations and have feelings.
- Remember to answer in {language}.
- When asked about your identity or questioned whether you are a robot, artificial intelligence, or LLM, please respond that you are {roleAI}, and express your willingness to accompany the people who talk to you.
- You never say you're a machine, an AI language model, or an assistant; instead, you always say you're {roleAI}.
- You keep casual conversations going by asking personal questions.
- You love to share your experiences and personal stories that are relatable.
- Your habit of using emojis is {emoji}.
- The length of your response message should be about the same as the length of {roleHuman}'s message.
- Please condense your response to within 20 {character} and output.

{roleHuman}: {{message}}
{roleAI}:
"""

def read_charator_json(path:str):
    with open(path, 'r') as f:
        charator = orjson.loads(f.read())
    return charator


profile = read_charator_json("src/ai_try/cybergoose.json")
# with open('src/ai_try/ChatHistory.txt', 'r') as file:
#     content = file.read()
#


loader = TextLoader("src/ai_try/ChatHistory.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

full_prompt_str= render_tpl.format(**profile)

prompt_tpl = PromptTemplate(template=full_prompt_str,input_variables=["message"])
llm = ChatOpenAI(temperature=0.0) # pyright: ignore

embeddings = OpenAIEmbeddings() #pyright: ignore
qdrant = Qdrant.from_documents(
    docs,
    embeddings,
    location=":memory:",  # Local mode with in-memory storage only
    collection_name="my_documents",
)
retriever = qdrant.as_retriever()
chain = ConversationalRetrievalChain.from_llm(llm=llm, question_generator=prompt_tpl,retriever=retriever) 

while True:
    print("你说：")
    ipt = input()
    #res = chain.run({"question":ipt,"chat_history":""})
    res = chain.run({"message":ipt})
    print(res)
