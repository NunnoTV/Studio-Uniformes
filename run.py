from app import create_app
import os
import sys
from waitress import serve

# Adiciona a raiz do projeto ao Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

app = create_app()

if __name__ == '__main__':
    # Este bloco é para uso em desenvolvimento com `python run.py`
    # Em produção, o Gunicorn cuidará da execução do aplicativo.
    print("🚀 Iniciando API de Redimensionamento de Imagens em modo de desenvolvimento.")
    print("Para produção, use Gunicorn e Nginx.")
    serve(app, host='0.0.0.0', port=80)