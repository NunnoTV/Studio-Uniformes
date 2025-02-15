from flask import Blueprint, request, jsonify, send_file
from api.services import image_service
from api.constants import COMPRESSED_FILE

main_bp = Blueprint("main", __name__)

@main_bp.route("/", methods=["POST"])
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

@main_bp.route("/download", methods=["GET"])
def download():
    # Retorna o arquivo compactado para download
    return send_file(COMPRESSED_FILE, as_attachment=True)