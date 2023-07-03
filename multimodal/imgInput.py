import base64
import json
import os
import aiohttp
from dotenv import load_dotenv
import asyncio
import replicate
import openai
from func.agentPrompter import fill_template
from termcolor import colored

# 微软的我也想试试，图片标题和 OCR 都有 https://learn.microsoft.com/en-us/azure/cognitive-services/computer-vision/concept-describe-images-40?tabs=image
# 注册时电话通不过，需上班时间问销售

openai.api_key = "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"

class ImageUnderstandingModel:
    def __init__(self):
        load_dotenv(".env")
        self.google_cloud_api_key = os.getenv("GOOGLE_CLOUD_API_KEY")
        # self.replicate_key = os.getenv("REPLICATE_KEY")
        # os.environ["REPLICATE_API_TOKEN"] = self.replicate_key
    
    def ask_image_question(self, prompt, filepath):
        output = replicate.run(
        "andreasjansson/blip-2:4b32258c42e9efd4288bb9910bc532a69727f9acd26aa08e175713a0a857a608",
        input={"image": open(filepath, "rb"), "question": prompt},
    )
        return output

    def get_image_caption(self, filepath):
        output = replicate.run(
            "andreasjansson/blip-2:4b32258c42e9efd4288bb9910bc532a69727f9acd26aa08e175713a0a857a608",
            input={"image": open(filepath, "rb"), "caption": True},
        )
        return output

    async def do_image_ocr(self, filepath):
        # Read the image file and encode it in base64 format
        if not self.google_cloud_api_key:
            return "No Key"
        with open(filepath, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        # Prepare the JSON payload
        payload = {
            "requests": [
                {
                    "image": {"content": encoded_image},
                    "features": [{"type": "TEXT_DETECTION"}],
                }
            ]
        }

        header = {
            "Content-Type": "application/json; charset=utf-8",
        }

        url = f"https://vision.googleapis.com/v1/images:annotate?key={self.google_cloud_api_key}"

        # Send the async request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers=header, data=json.dumps(payload)
            ) as response:
                result = await response.json()

                if response.status == 200:
                    # Get fullTextAnnotation
                    full_text_annotation = result.get("responses", [])[0].get(
                        "fullTextAnnotation"
                    )

                    if full_text_annotation:
                        extracted_text = full_text_annotation.get("text")

                        # Return the extracted text
                        return extracted_text
                    else:
                        return ""
                else:
                    raise Exception(
                        f"Google Cloud Vision API returned an error. Status code: {response.status}, Error: {result}"
                    )
                
    def get_response(self, msg):
        def run_conversation(messages):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0,
            )
            return response

        messages = [
            {"role": "system", "content": fill_template()},
            {"role": "user", "content": msg}
        ]
        # print(messages)
        response = run_conversation(messages)["choices"][0]
        return json.dumps(response["message"]["content"], ensure_ascii=False)  
                
