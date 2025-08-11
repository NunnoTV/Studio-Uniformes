import json
from flask import Blueprint, request, jsonify, url_for, current_app
from .utils import download_image_from_url, load_image_from_local_path, load_image_from_upload
from .tasks import process_image_task
from .config import Config
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def home():
    return jsonify({"message": "API de Redimensionamento de Imagens com Celery"})

@main_bp.route('/process', methods=['POST'])
def process_image_endpoint():
    image_data = None
    tamanhos_data = None

    if request.is_json:
        data = request.get_json()
        if 'tamanhos' not in data:
            return jsonify({"erro": "Dados de tamanhos nÃ£o fornecidos"}), 400
        tamanhos_data = data['tamanhos']
        if 'url' in data:
            image_data = download_image_from_url(data['url'])
        elif 'local_path' in data:
            image_data = load_image_from_local_path(data['local_path'])
    elif request.content_type.startswith('multipart/form-data'):
        if 'file' not in request.files:
            return jsonify({"erro": "Arquivo nÃ£o fornecido"}), 400
        file = request.files['file']
        if 'tamanhos' not in request.form:
            return jsonify({"erro": "Dados de tamanhos nÃ£o fornecidos"}), 400
        tamanhos_data = json.loads(request.form['tamanhos'])
        image_data = load_image_from_upload(file)

    if not image_data or not tamanhos_data:
        return jsonify({"erro": "Entrada invÃ¡lida"}), 400

    task = process_image_task.delay(image_data, tamanhos_data)

    return jsonify({"task_id": task.id, "status_url": url_for('main.get_status', task_id=task.id, _external=True)}), 202

@main_bp.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    task = process_image_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pendente...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'result': task.info.get('result', None) if isinstance(task.info, dict) else task.info
        }
        if 'result' in response and response['result']:
             response['download_url'] = url_for('main.download_file', filename=os.path.basename(response['result']), _external=True)
    else:
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

@main_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(current_app.config['OUTPUT_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({"erro": "Arquivo nÃ£o encontrado"}), 404
    from flask import send_from_directory
    return send_from_directory(current_app.config['OUTPUT_FOLDER'], filename, as_attachment=True)
