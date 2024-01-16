import requests

url = "http://localhost:8000/api/generate-diff"
params = {
    "repoUrl": "https://github.com/debricked/tiny-repo",
    "prompt": "Write a README.md"
}

with requests.post(url, json=params, stream=True) as r:
    for chunk in r.iter_content(1024):  # or, for line in r.iter_lines():
        print(chunk.decode())