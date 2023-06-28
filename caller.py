import openai
import json
from func.voicer import VoiceTool
from func.agentPrompter import fill_template
import time
from termcolor import colored

openai.api_key = "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"
messages = []

def text_to_speech(text):
    """Convert response text to speech when the user sends a voice message or requests a voice response"""
    voice_tool = VoiceTool()
    voice_msg = voice_tool.run(text)
    return voice_msg

def run_conversation(msg):
    messages = [
        { "role": "system", "content": fill_template()},
        { "role": "user", "content": msg}]
    functions=[
        {
            "name": "text_to_speech",
            "description": "Convert response text to speech when the user sends a voice message or requests a voice response",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Response text that needs to be converted into speech",
                    },
                },
                "required": ["text"],
            },
        }
    ]   
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        temperature=0,
        function_call="auto",
    )
    return response

while True:
    msg = input(colored(f"message: ", "blue"))
    start_time = time.time()
    response = run_conversation(msg)
    print(response)

    if response.choices[0]["finish_reason"] == "stop":
        print(json.dumps(response.choices[0]["message"]["content"], ensure_ascii=False))
        break

    if response.choices[0]["finish_reason"] == "function_call":
        fn_name = response.choices[0].message["function_call"].name
        arguments = list(json.loads(response.choices[0].message["function_call"].arguments).values())
        print("arguments:", arguments)
        try:
            function = locals().get(fn_name)
            result = function(arguments)
        except Exception as e:
            print(f"Error when calling function {fn_name} with arguments {arguments}: {e}")

        messages.append(
            {
                "role": "assistant",
                "content": None,
                "function_call": {
                    "name": fn_name,
                    "arguments": arguments,
                },
            }
        )

        messages.append(
            {
                "role": "function", 
                "name": fn_name, 
                "content": result}
        )
        response = run_conversation(messages)
        print(response)
        print(json.dumps(response.choices[0]["message"]["content"], ensure_ascii=False))
        print(messages)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: {elapsed_time} seconds")

    # response_msg = response['choices'][0]['message']
    # print(response_msg)
    # print(json.dumps(response_msg.content, ensure_ascii=False))
    # if response_msg.get("function_call"):
    #     available_functions = {
    #         "text_to_speech": text_to_speech,
    #     }
    #     function_name = response_msg["function_call"]["name"]
    #     function_to_call = available_functions[function_name]
    #     function_args = json.loads(response_msg["function_call"]["arguments"])
    #     function_response = function_to_call(
    #         text=function_args["text"] if "text" in function_args else None,
    #     ) #这里调用的函数，结果赋值给function_response
    #     messages.append(response_msg)
    #     messages.append(
    #         {
    #             "role": "function",
    #             "name": function_name,
    #             "content": function_response,
    #         }
    #     )

    #     second_response = openai.ChatCompletion.create(
    #         model="gpt-3.5-turbo-0613",
    #         messages=messages,
    #         temperature=0
    #     ) #询问模型：我刚才执行了一个函数，结果是 X，基于这个新的信息，你现在会说什么？
    #     end_time = time.time()
    #     elapsed_time = end_time - start_time
    #     print(f"Elapsed time: {elapsed_time} seconds")
    #     print(messages)
    #     return second_response

