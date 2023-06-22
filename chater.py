from langchain import  LLMChain, OpenAI, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory, VectorStoreRetrieverMemory,CombinedMemory
from langchain.embeddings import  OpenAIEmbeddings
from langchain.schema import Document
from langchain.vectorstores import Qdrant
from langchain.callbacks import get_openai_callback
from langchain.text_splitter import  RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.callbacks.base import BaseCallbackHandler

import re

from typing import List, Sequence



import os
import orjson

api_key  = 'xxx'
os.environ["OPENAI_API_KEY"] = api_key

render_tpl= """
You are {roleAI}, you'll chat with {roleHuman} here's some important things that you should know 
The relationship between you({roleAI}) and {roleHuman}: 

{relationship} 

The information of youself({roleAI}):
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
- Sometimes you prefer to use emojis in chat {emoji}.
- The length of your response message should be about the same as the length of {roleHuman}'s message.
- You can learn conversation context from "Chat History" and "Recent Chat History".
- Please condense your response to within 20 {character} and output.
- Chat History is real conversation bewteen {roleAI} and {roleHuman}
- Recent Chat History is the lastst messages {roleHuman} sent to {roleAI}

Chat History:
{{history}}

Recent Chat History:
{{recent}}

{roleHuman}:{{message}}
{roleAI}:
"""


"""
"""

def extract_variables_from_tpl(text:str):
    pattern = r"\{\{(.*?)\}\}"
    matches = re.findall(pattern, text)
    return matches

def read_charator_json(path:str):
    with open(path, 'r') as f:
        charator = orjson.loads(f.read())
    return charator



class ChatBot:
    def __init__(self,chat_to:str,raw_prompt:str,temperature=0.0,) -> None:

        self.raw_prompt = raw_prompt
        self.vdb = self._init_vectiorDB(chat_to)
        self.prompt_tpl = self._init_prompt_tpl() 
        self.chain = self._init_chain(temperature=temperature)
        self.ai_name = ""
        self.human_name = ""


    def _init_prompt_tpl(self) -> PromptTemplate:
        _,json_path = self._get_user_data()
        charator = read_charator_json(json_path)
        _tpl = self.raw_prompt.format(**charator)
        vars = extract_variables_from_tpl(self.raw_prompt)
        self.ai_name = charator["roleAI"]
        self.human_name = charator["roleHuman"]
        return PromptTemplate(template=_tpl,input_variables=vars)
    

    def _init_chain(self,temperature:float):
        vector_retiever = self.vdb.as_retriever(search_kwargs={"k":3})
        vector_memory = VectorStoreRetrieverMemory(retriever=vector_retiever)
        conversation_history_memory = ConversationBufferWindowMemory(
            input_key="message",
            memory_key="recent",
            ai_prefix=self.ai_name,
            human_prefix=self.human_name,
            k=3
        )
     
        
        mem = CombinedMemory(memories=[vector_memory,conversation_history_memory])
        
        chain = LLMChain(
            llm=OpenAI(temperature=temperature),#pyright:ignore
            memory=mem,
            prompt=self.prompt_tpl,
            verbose=True

        )
   
        return chain

    def _init_vectiorDB(self,user_id:str):
        history,_ = self._get_user_data()
        docs = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20).split_documents(
            TextLoader(history).load()
        )
        embed = OpenAIEmbeddings() #pyright: ignore
        return Qdrant.from_documents(documents=docs,embedding=embed,location=":memory:")

    def _get_user_data(self) -> Sequence[str]:
        return "src/ai_try/ChatHistory.txt","src/ai_try/cybergoose.json"

    def _get_relevant_from_vectorDB(self,message:str)-> List[Document]:
        return self.vdb.similarity_search(message,5)

    def chat(self,**kwd):
        return self.chain.predict(**kwd)
        

chater = ChatBot("",raw_prompt=render_tpl)
while True:

    with get_openai_callback() as cb:

        #recent_text= "".join([f"Human: {i}\n" for i in recent_list])
        print("你说：")
        ipt = input()
        res = chater.chat(message=ipt)
        print(res)
        

