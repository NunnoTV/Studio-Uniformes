import requests

url = "/app/uploads/hc.jpg"

body = {
        "local_path": url,
        "tamanhos": {
            "GG": 15,
            "G": 40,
            "M": 45,
            "P": 30,
            "PP": 20
        }
    }

response = requests.post("http://localhost:80/process", json=body, headers={"Content-Type": "application/json"})




if response.status_code == 200:
    download_id = response.json()['detalhes']['download_id']
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
else:
    print(f"Erro: {response.status_code}")
    print(f"Response: {response.text}")
