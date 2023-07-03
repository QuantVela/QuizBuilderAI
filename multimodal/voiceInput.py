import openai
import json
from func.voicer import VoiceTool
from func.agentPrompter import fill_template
import time
from termcolor import colored
import re

openai.api_key = "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"

def speech_to_text():
    audio_file= open("../audio/mia.wav", "rb") #To do: 客户端需换成用户输入的语音
    transcript = openai.Audio.transcribe("whisper-1", audio_file, prompt="使用简体中文")
    result = json.dumps(transcript.text, ensure_ascii=False)
    result = result[1:-1] if result[0] == result[-1] == "\"" else result
    return result

def run_conversation(messages):  
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5,
    )
    return response

def get_response(msg):
    messages = [
        { "role": "system", "content": fill_template()},
        { "role": "user", "content": msg}]
    response = run_conversation(messages)["choices"][0]
    return json.dumps(response["message"]["content"], ensure_ascii=False)

def remove_all_emojis(text: str) -> str:
    emoji_pattern = re.compile('[\U00010000-\U0010ffff]', flags=re.UNICODE)
    result = re.sub(emoji_pattern, "", text)
    return result

voice_msg = speech_to_text()
res = get_response(voice_msg)
text = remove_all_emojis(res)
print(text)
voice_tool = VoiceTool()
voice_tool.run(text)