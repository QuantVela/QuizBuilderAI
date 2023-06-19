from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain, OpenAI
from langchain.chains import ConversationChain, LLMChain
from langchain.memory import ConversationBufferMemory, ChatMessageHistory
from langchain.vectorstores import Qdrant
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
import logging
from termcolor import colored
import os
import time
import re
import random
import orjson
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv()) # read local .env file
# openai.api_key = os.environ['OPENAI_API_KEY']
api_key = "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"
os.environ["OPENAI_API_KEY"] = api_key
QDRANT_HOST = "aifriend"
QDRANT_URL = "https://99d3f2ff-e74b-49e0-9bb9-04977ac947d3.us-east-1-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "9i1v-GcgQygerPq9mqh9WxqlJqXuU2YJ7fGU_ubHOzpgku48s7eknw"

template = (
    """You are {roleAI}, and your relationship with {roleHuman} is {relationship}. In daily life, your age is {age}, your occupation is {occupation}, and your gender is {gender}. Your personality traits are {personality}, and the tone of your conversations with {roleHuman} is {tone}.
The following is a conversation which is {roleAI} and {roleHuman} have had in the past, please imitate the conversation style, personality, and preferences of {roleAI}:
Relevant pieces of previous conversation history:
Conversation: {{conversation}}
(You do not need to use these pieces of information if not relevant)

Based on the above information, as {roleAI}, please respond to the message {roleHuman} sends to you and provide emotional companionship.

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

{{history}}
Current conversation:
{roleHuman}: {{message}}
{roleAI}:
"""
)
def read_botset(path:str):
    with open(path, 'r') as f:
        charactor = orjson.loads(f.read())
    return charactor

def chatbot(message):
    chat = ChatOpenAI(temperature=0.0)
    profile = read_botset('botset.json')

    full_prompt_str = template.format(**profile)
    prompt_template = PromptTemplate(
        input_variables=["message", "conversation", "history"],
        template=full_prompt_str
    )

    loader = TextLoader('ChatHistory.txt')
    documents = loader.load()
    print (f'You have {len(documents)} document(s) in your data')
    print (f'There are {len(documents[0].page_content)} characters in your document')

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    docs = text_splitter.split_documents(documents)
    print (f'Now you have {len(docs)} documents')

    embeddings = OpenAIEmbeddings(openai_api_key=api_key)

    qdrant = Qdrant.from_documents(
        docs,
        embeddings,
        url=QDRANT_URL,
        prefer_grpc=True,
        api_key=QDRANT_API_KEY,
        collection_name="chat_history",
    )
    
    chain = LLMChain(
        llm=chat, 
        prompt=prompt_template, 
        verbose=True,
        memory=ConversationBufferWindowMemory(k=4,memory_key="history",input_key="message"),
    )

    relevant_docs = qdrant.similarity_search(query=message, k=4)
    print("Relevant docs:", relevant_docs)
    conversation ='\n'.join(["Conversation "+str(i+1) +": \n"+ doc.page_content for i,doc in enumerate(relevant_docs)])
    print("Conversation:", conversation)
          
    # response = chain.run({"message":message, "conversation":conversation})
    response = chain.predict(
        message=message, 
        conversation=conversation)

    # print(chain.memory.buffer)
    return response

def remove_punctuation_before_emojis(text):
    emoji_pattern = re.compile('[\U00010000-\U0010ffff]', flags=re.UNICODE)    
    emojis = re.findall(emoji_pattern, text)
    sentence = re.sub(emoji_pattern, "", text)   
    # Remove any punctuation at the end of the sentence
    sentence = re.sub(r'[^\w\s]$', '', sentence)
    result = sentence + ''.join(emojis)
    return result

def split_sentence(sentence):
    if sentence.endswith('。'):
        sentence = sentence[:-1]   
    split_sentences = re.split('，|！|。',sentence)   
    return split_sentences

# random meme
def maybe_print_meme():
    num = random.random()
    if num < 0.2:  # 20% probability
        folder = random.choice(['meme/cuteCat', 'meme/cuteDog'])  
        images = os.listdir(folder)
        image = random.choice(images) 
        print(f'{folder}/{image}')  # To do: change to img url

def main():
    print("Start chatting...Press CTRL+C to exit at any time.\n")
    while True:
        message = input(colored(f"message: ", "blue"))
        response = chatbot(message)
        print(response)
        
        # processed_text = remove_punctuation_before_emojis(response)
        # split_msg = split_sentence(processed_text)
        # for s in split_msg:
        #     time.sleep(0.2)
        #     print(s)
        # maybe_print_meme()

main()