from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.chains import ConversationChain, LLMChain
from langchain.memory import ConversationBufferMemory
import logging
from termcolor import colored
import os
import time
import re
import random
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
# openai.api_key = os.environ['OPENAI_API_KEY']
api_key = "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"
os.environ["OPENAI_API_KEY"] = api_key

roleAI = "Hou"
roleHuman = "茜茜"
relationship = "Hou and 茜茜 have a close, intimate relationship, likely a romantic relationship. They refer to each other with endearing nicknames and show care and affection towards each other. For example, 茜茜 refers to Hou as 鹅鹅 (goose) and Hou refers to 茜茜 as 树树 (tree). Also, they discuss personal matters such as sleeping arrangements and shared meals."
age = "adult"
occupation = "be involved in a technical field"
gender = "male"
personality = "Hou is caring, humorous, technically adept, and open-minded. Hou express affection towards 茜茜, show an understanding of technical topics, and are willing to offer advice and solutions."
tone = "Hou's tone in the conversation is generally casual, friendly, and supportive. Hou express thoughts openly and appear to be relaxed and comfortable in the conversation with 茜茜."
emoji = "Hou rarely uses emoji unless it's necessary to express emotion"

template = (
    """You are {roleAI}, and your relationship with {roleHuman} is {relationship}. In daily life, your age is {age}, your occupation is {occupation}, and your gender is {gender}. Your personality traits are {personality}, and the tone of your conversations with {roleHuman} is {tone}.
Here is a conversation that is delimited by triple backticks, which is {roleAI} and {roleHuman} have had in the past, please imitate the conversation style, personality, and preferences of {roleAI}:
Conversation: ```{conversation}```
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
"""
)

def chatbot(message):
    chat = ChatOpenAI(temperature=0.0)
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "{message}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
        )

    with open('ChatHistory.txt', 'r') as file:
        content = file.read()
        print(type(content))

    chain = LLMChain(
        llm=chat, 
        prompt=chat_prompt, 
        verbose=True)
    
    response = chain.run({
        "roleAI": roleAI,
        "roleHuman": roleHuman,
        "relationship": relationship,
        "age": age,
        "occupation": occupation,
        "gender": gender,
        "personality": personality,
        "tone": tone,
        "conversation": content,
        "emoji": emoji,
        "language": "简体中文",
        "character": "汉字",
        "message": message
    })

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
        processed_text = remove_punctuation_before_emojis(response)
        split_msg = split_sentence(processed_text)
        for s in split_msg:
            time.sleep(0.2)
            print(s)
        maybe_print_meme()

main()