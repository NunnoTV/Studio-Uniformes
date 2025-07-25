import requests as requests
from urllib.parse import urlparse
from PIL import Image
import io
import os
import psutil

processo = psutil.Process(os.getpid())

def download_image_from_url(url):
    """
    Baixa uma imagem de uma URL e retorna um objeto PIL Image
    """
    try:
        # Verificar se a URL é válida
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("URL inválida")
        
        # Headers para simular um navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fazer download da imagem
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # Verificar se o conteúdo é uma imagem
        content_type = response.headers.get('content-type', '').lower()
        if not content_type.startswith('image/'):
            raise ValueError(f"URL não aponta para uma imagem válida. Content-Type: {content_type}")
        
        # Verificar tamanho do arquivo (máximo 500MB)
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > 500 * 1024 * 1024: # Use Config.MAX_CONTENT_LENGTH if importing Config here
            raise ValueError("Imagem muito grande (máximo 500MB)")
        
        # Carregar imagem na memória
        image_data = io.BytesIO()
        for chunk in response.iter_content(chunk_size=8192):
            image_data.write(chunk)
        
        image_data.seek(0)
        
        # Abrir com PIL
        image = Image.open(image_data)
        
        
        return image
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro ao baixar imagem: {str(e)}")
    except Exception as e:
        raise Exception(f"Erro ao processar imagem da URL: {str(e)}")
    

def load_image_from_local_path(filepath):
    """
    Carrega uma imagem de um caminho local e retorna um objeto PIL Image
    """
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(filepath):
            raise ValueError(f"Arquivo não encontrado: {filepath}")
        
        # Verificar se é um arquivo
        if not os.path.isfile(filepath):
            raise ValueError(f"Caminho não é um arquivo válido: {filepath}")
        
        # Verificar tamanho do arquivo (máximo 500MB)
        file_size = os.path.getsize(filepath)
        if file_size > 500 * 1024 * 1024:
            raise ValueError("Imagem muito grande (máximo 500MB)")
        
        # Verificar extensão do arquivo
        filename = os.path.basename(filepath)
        if not allowed_file(filename):
            raise ValueError(f"Tipo de arquivo não suportado. Use: png, jpg, jpeg, gif, bmp, tiff")
        
        # Abrir imagem com PIL
        image = Image.open(filepath)
        
        return image
        
    except Exception as e:
        raise Exception(f"Erro ao carregar imagem local: {str(e)}")

def load_image_from_upload(file):
    """
    Carrega uma imagem de um arquivo enviado via upload e retorna um objeto PIL Image
    """
    try:
        # Verificar se o arquivo tem nome válido
        if not file.filename:
            raise ValueError("Nome do arquivo não fornecido")
        
        # Verificar extensão do arquivo
        if not allowed_file(file.filename):
            raise ValueError(f"Tipo de arquivo não suportado. Use: png, jpg, jpeg, gif, bmp, tiff")
        
        # Ler conteúdo do arquivo
        file_content = file.read()
        
        # Verificar tamanho (máximo 500MB)
        if len(file_content) > 500 * 1024 * 1024:
            raise ValueError("Arquivo muito grande (máximo 500MB)")
        
        # Criar stream de bytes
        image_stream = io.BytesIO(file_content)
        
        # Abrir imagem com PIL
        image = Image.open(image_stream)
        
        return image
        
    except Exception as e:
        raise Exception(f"Erro ao carregar imagem do upload: {str(e)}")


def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS