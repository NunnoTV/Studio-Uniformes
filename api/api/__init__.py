from flask import Flask
from api.routes.main import main_bp

def create_app():
    app = Flask(__name__)
    
    # Aqui você pode carregar configurações (ex.: app.config.from_object('app.config.DevelopmentConfig'))
    
    # Registra os blueprints
    app.register_blueprint(main_bp)
    
    return app


