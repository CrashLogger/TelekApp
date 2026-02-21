import requests
from dotenv import load_dotenv
import os

api_url = "https://app.galerna.eus/discordbotapi"

file_path = "debug-tools/angery-admin.png"

load_dotenv()
username = os.getenv("REAL_API_LOGIN")
hash = os.getenv("REAL_API_HASH")

with open(file_path, "rb") as f:
    data = {"username": username, "password_hash": hash}
    files = {"file": (file_path.split('/')[-1], f)}
    response = requests.post(api_url, data=data, files=files)

# Response
print("Status Code:", response.status_code)
print("Response:", response.json())
