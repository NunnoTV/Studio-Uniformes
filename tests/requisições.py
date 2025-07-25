import requests

url = "https://i.ibb.co/qMQq7qnG/molde.png"

body = {
        "url": url,
        "tamanhos": {
            "EXG": 21,
            "GG": 67
        }
    }

response = requests.post("https://studio-uniformes.vercel.app/process", json=body, headers={"Content-Type": "application/json"})

#download_id = response.json()['detalhes']['download_id']

print(f"Status Code: {response.status_code}")
#print(f"O download_id é: {download_id}")
print(f"Response: {response.json()}")