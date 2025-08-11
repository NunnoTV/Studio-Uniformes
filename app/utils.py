import requests

def download_image_from_url(url):
    """
    Baixa uma imagem de uma URL e retorna seus dados em bytes.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        image_data = response.content
        return image_data
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro ao baixar imagem: {str(e)}")
    

def load_image_from_local_path(filepath):
    """
    Carrega uma imagem de um caminho local e retorna seus dados em bytes.
    """
    try:
        with open(filepath, 'rb') as f:
            image_data = f.read()
        return image_data
    except Exception as e:
        raise Exception(f"Erro ao carregar imagem local: {str(e)}")

def load_image_from_upload(file):
    """
    Carrega uma imagem de um arquivo enviado via upload e retorna seus dados em bytes.
    """
    try:
        image_data = file.read()
        return image_data
    except Exception as e:
        raise Exception(f"Erro ao carregar imagem do upload: {str(e)}")


def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS