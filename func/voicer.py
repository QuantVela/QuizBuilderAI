"""Tool for voice message."""
import requests
import os
from dotenv import load_dotenv
import time
from pymongo import MongoClient
from typing import Optional, Type, List, Dict
from langchain.chat_models import ChatOpenAI

class VoiceTool():
    def __init__(self):
        load_dotenv()
        self.XI_API_KEY = os.getenv('XI_API_KEY')
        self.headers = {"Accept": "application/json","xi-api-key": self.XI_API_KEY}  
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['mydatabase']     

    def run(self, query: str) -> str:
        # response = chatbot(query)
        return self.text_to_speech(query) 
    
    def add_voice(self, voice_data: Dict[str, str], voice_files: List[tuple]) -> str:
        """
        Add a new voice to database.

        Parameters:
        voice_data = {
            'name': 'Hou Voice',
            'labels': '{"accent": "British", "gender": "Male", "language": "English", "age": "Adult"}'
        }
        voice_files = [
            ('files', ('hou_en.wav', open("./audio/hou_en.wav", 'rb'), 'audio/wav'))
        ]

        Returns:
        str: voice_id

        To do:
        - voice_data 部分根据数据库已有资料去填充，部分在页面填写
        - voice_files 客户端校验 Provide more than 1 minute of high quality voice audio, audio files, up to 10MB, a total of less than 25 samples
        
        """
        add_voice_url = "https://api.elevenlabs.io/v1/voices/add"
        try:
            response = requests.post(add_voice_url, headers=self.headers, data=voice_data, files=voice_files)
        except Exception as e:
            return f"Failed to add voice: {e}"
        
        voice_id = response.json()["voice_id"]
        
        self.db['voice_collection'].insert_one({'voice_id': voice_id})
        result = self.db['voice_collection'].find_one({'voice_id': voice_id})
        if result:
            print("Voice has been successfully stored. Voice ID:", result['voice_id'])
        else:
            print("Voice storage failed.")
            return None
        return voice_id

    def text_to_speech(self, text: str) -> str:
        """
        Convert text to speech when the user sends a voice message or requests a voice response
        """
        try:
            response = requests.get(
                "https://api.elevenlabs.io/v1/voices/settings/default",
                headers={ "Accept": "application/json" }
            ).json()
        except Exception as e:
            return f"Failed to get voice: {e}"
        stability, similarity_boost = response["stability"], response["similarity_boost"]

        voice_id_entry = self.db['voice_collection'].find_one()
        if not voice_id_entry:
            print("No voice ID found.")
            return
        voice_id = voice_id_entry['voice_id']
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"

        self.headers["Content-Type"] = "application/json"
        tts_data = {
          "text": text,
          "model_id": "eleven_monolingual_v1", #To do: 数据库接入语言 monolingual for English, eleven_multilingual_v1 for English, German, Polish, Spanish, Italian, French, Portuguese, and Hindi.
          "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost
          }
        }

        try:
            response = requests.post(tts_url, json=tts_data, headers=self.headers, stream=True)
        except Exception as e:
            return f"Failed to convert text to speech: {e}"
        
        output_path_prefix = "./audio/output_"
        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
        output_path = output_path_prefix + timestamp + ".wav"

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"Audio message: {output_path}")

        return output_path #To do: return audio url

    def get_history(self) -> str:
        """Returns metadata about all your generated audio."""
        history_url = "https://api.elevenlabs.io/v1/history"
        response = requests.get(history_url, headers=self.headers)
        return response.text
