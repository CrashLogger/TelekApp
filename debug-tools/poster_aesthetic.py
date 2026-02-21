import requests
from dotenv import load_dotenv
import os


api_url = "http://127.0.0.1:5000/discordbotapi"



trigger = input("Insert trigger: ")
autoresponse = input("Insert autoresponse: ")


load_dotenv()
username = os.getenv("REAL_API_LOGIN")
password_hash = os.getenv("REAL_API_HASH")

# jotasón
data = {
    "username": username,
    "password_hash": password_hash,
    "trigger": trigger,
    "autoresponse": autoresponse
}

# POSTeame esta
response = requests.post(api_url, json=data)

# Respondeme esta
print("Status Code:", response.status_code)
try:
    print("Response:", response.json())
except Exception:
    print("Response content:", response.text)