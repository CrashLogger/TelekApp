import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Correct URL with scheme
api_url = "http://127.0.0.1:5000/autoresponse/upload"  # Adjust endpoint as needed

# Load credentials
username = os.getenv("REAL_API_LOGIN")
hash_value = os.getenv("REAL_API_HASH")

file_path = "debug-tools/angery-admin.png"

# Use 'data' for form fields and 'files' for the file
with open(file_path, "rb") as f:
    data = {"username": username, "password_hash": hash_value}
    files = {"file": (os.path.basename(file_path), f)}
    
    response = requests.post(api_url, data=data, files=files)

# Response
print("Status Code:", response.status_code)
try:
    print("Response:", response.json())
except Exception:
    print("Response content:", response.text)