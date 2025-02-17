from flask import Flask
import os
from flask import request, jsonify, send_file
#from api.constants import COMPRESSED_FILE
from .constants import COMPRESSED_FILE
from services import image_service


print("Diretório de Trabalho:", os.getcwd())


app = Flask(__name__)



@app.route('/')
def home():
    return 'Hello, World!'


@app.route("/diagramar", methods=["POST"])
def diagramar():
    try:
        dados = request.get_json()
        lista = dados.get("lista")
        url_image = dados.get("imagem")
        
        # Processa a imagem e gera o arquivo compactado
        image_service.process_image_request(lista, url_image)
        
        return jsonify({"message": "Arquivo diagramado com sucesso"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["GET"])
def download():
    # Retorna o arquivo compactado para download
    return send_file(COMPRESSED_FILE, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))

