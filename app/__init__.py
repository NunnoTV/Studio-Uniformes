from flask import Flask
import os
from .config import Config
from flask import jsonify
from .tasks import celery

def create_app(celery_app=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Criar diretÃ³rios se nÃ£o existirem
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

    from .routes import main_bp
    app.register_blueprint(main_bp)

    if celery_app:
        celery_app.config_from_object(app.config, namespace='CELERY')
        celery_app.conf.update(app.config)

        class ContextTask(celery_app.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery_app.Task = ContextTask

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"erro": "Arquivo muito grande. Tamanho mÃ¡ximo: 500MB"}), 413

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Endpoint nÃ£o encontrado"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"erro": "Erro interno do servidor"}), 500

    return app