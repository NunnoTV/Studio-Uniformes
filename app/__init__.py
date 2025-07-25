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

    # Error Handlers
    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"erro": "Arquivo muito grande. Tamanho máximo: 500MB"}), 413

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Endpoint não encontrado"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"erro": "Erro interno do servidor"}), 500

    print("🚀 API de Redimensionamento de Imagens inicializada.")
    print(f"📐 Tamanho do molde: {Config.SIZE_MOLDE[0]}x{Config.SIZE_MOLDE[1]}")
    print("🎨 PRESERVAÇÃO DE COR: Modo de cor original será mantido (RGB, CMYK, L, etc.)")
    print("📋 Tamanhos disponíveis:", list(Config.TAMANHOS.keys()))
    print("✂️  Crops disponíveis:", list(Config.CROPS.keys()))
    print("🔄 Crops que serão redimensionados:", Config.CROPS_PARA_REDIMENSIONAR)
    print("💾 Formato de arquivo: crop_name_tamanho_quantidade_unidades.jpg/png (baseado no modo de cor)")


    return app