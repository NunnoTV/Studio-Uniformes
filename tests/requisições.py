import requests

url = "C:/Users/brunn/OneDrive/Documentos/Studio Uniformes/molde.jpg"

body = {
        "local_path": url,
        "tamanhos": {
            "EXG": 21,
            "GG": 67,
            "G": 175,
            "M": 154,
            "P": 83 
        }
    }

response = requests.post("http://localhost:5000/process", json=body, headers={"Content-Type": "application/json"})

#download_id = response.json()['detalhes']['download_id']

print(f"Status Code: {response.status_code}")
#print(f"O download_id é: {download_id}")
print(f"Response: {response.json()}")