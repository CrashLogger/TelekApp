import requests

api_url = "http://127.0.0.1:5000/discordbotapi"

file_path = "debug-tools/patata.png"

with open(file_path, "rb") as f:
    data = {"username": "test", "password_hash": "098f6bcd4621d373cade4e832627b4f6"}
    files = {"file": (file_path.split('/')[-1], f)}
    response = requests.post(api_url, data=data, files=files)

# Response
print("Status Code:", response.status_code)
print("Response:", response.json())
