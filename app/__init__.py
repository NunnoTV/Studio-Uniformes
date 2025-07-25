from flask import Flask
import os
from .config import Config
import jsonify

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Criar diretórios se não existirem
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

    from .routes import main_bp
    app.register_blueprint(main_bp)

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"erro": "Arquivo muito grande. Tamanho máximo: 500MB"}), 413

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Endpoint não encontrado"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"erro": "Erro interno do servidor"}), 500

    return app