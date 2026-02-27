import json
import os
import requests
from dotenv import load_dotenv

# Thx @ggonzalez088 for the data extraction from the other bot

api_url = os.environ.get('TRIGGER_API_URL')
filename = "debug-tools/respuestas.json"

load_dotenv()

jwt_token = os.environ.get('JWT_TOKEN')


def form_json_request(trigger:str, response:str):
    header_jwt = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    data={
        "trigger":trigger,
        "autoresponse":response
    }

    print(header_jwt, data)
    response = requests.post(api_url, headers=header_jwt, json=data)

with open(filename, 'r') as file:
    data = json.load(file)['responses']
    print(type(data))
    for combo in data:
        trigger = combo["trigger"]
        responses = combo["response"]
        for response in responses:
            print(f"{trigger} - > {response}")
            form_json_request(trigger, response)
