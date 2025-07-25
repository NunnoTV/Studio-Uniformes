from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import os
import zipfile
import tempfile
import json
import requests
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
from urllib.parse import urlparse
import io
import psutil

processo = psutil.Process(os.getpid())



app = Flask(__name__)

# Configurações
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Criar diretórios se não existirem
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Tamanho do molde - medida padrão para redimensionar antes dos crops
SIZE_MOLDE = (20942, 9449)



# Dicionário de tamanhos
TAMANHOS = {
    "EXG": (8031, 10709),
    "XG": (7795, 10394),
    "GG": (7559, 10079),
    "G": (7323, 9764),
    "M": (7087, 9449),
    "P": (6850, 9134),
    "PP": (6614, 8818),
    "EXG FEMININA": (7795, 10394),
    "XG FEMININA": (7559, 10079),
    "GG FEMININA": (7323, 9764),
    "G FEMININA": (7087, 9449),
    "M FEMININA": (6850, 9134),
    "P FEMININA": (6614, 8818),
    "PP FEMININA": (6378, 8504),
    "16 ANOS": (6614, 8819),
    "14 ANOS": (6378, 8504),
    "12 ANOS": (6142, 8189),
    "10 ANOS": (5906, 7874),
    "8 ANOS": (5669, 7559),
    "6 ANOS": (5197, 6929),
    "4 ANOS": (4961, 6614),
    "2 ANOS": (4724, 6299)
}

# Coordenadas dos crops
CROPS = {
    'MANGA_ESQUERDA': (0, 0, 6141.73, 3189.07 ),
    'MANGA_DIREITA': (0, 3493.76, 6141.73, 6682.83),
    'FRENTE': (6455.25, 0, 13541.87, 9448.91),
    'COSTAS': (13855.39, 0, 20942, 9448.91)
}

# Crops que devem ser redimensionados
CROPS_PARA_REDIMENSIONAR = ['FRENTE', 'COSTAS']

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
        if content_length and int(content_length) > 500 * 1024 * 1024:
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

def get_fill_color_for_mode(mode):
    """
    Retorna a cor de preenchimento apropriada para cada modo de cor
    """
    if mode in ['RGB', 'RGBA']:
        return (255, 255, 255)  # Branco para RGB/RGBA
    elif mode in ['CMYK']:
        return (0, 0, 0, 0)  # Branco em CMYK
    elif mode in ['L', 'LA']:
        return 255  # Branco para escala de cinza
    elif mode == '1':
        return 1  # Branco para imagens binárias
    else:
        return 255  # Padrão para outros modos

def resize_to_molde(image):
    """
    Redimensiona a imagem para o tamanho do molde (SIZE_MOLDE)
    mantendo a proporção e preenchendo com fundo branco se necessário
    PRESERVA O MODO DE COR ORIGINAL
    """
    try:
        # Obter dimensões atuais e modo de cor
        original_width, original_height = image.size
        original_mode = image.mode
        target_width, target_height = SIZE_MOLDE
        
        print(f"🔧 Redimensionando de {original_width}x{original_height} para {target_width}x{target_height}")
        print(f"🎨 Modo de cor original: {original_mode}")
        
        # Calcular proporções
        ratio_width = target_width / original_width
        ratio_height = target_height / original_height
        
        # Usar a menor proporção para manter a imagem toda visível
        ratio = min(ratio_width, ratio_height)
        
        # Calcular novo tamanho mantendo proporção
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        
        # Redimensionar imagem
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Criar nova imagem com fundo branco NO MESMO MODO DE COR ORIGINAL
        fill_color = get_fill_color_for_mode(original_mode)
        final_image = Image.new(original_mode, SIZE_MOLDE, fill_color)
        
        # Calcular posição para centralizar a imagem redimensionada
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        
        # Colar a imagem redimensionada no centro
        final_image.paste(resized_image, (x_offset, y_offset))
        
        print(f"✅ Imagem redimensionada e centralizada com sucesso (modo {original_mode} preservado)")
        return final_image
        
    except Exception as e:
        raise Exception(f"Erro ao redimensionar para molde: {str(e)}")

def crop_image(image, crop_coords):
    """Realiza o crop da imagem usando as coordenadas fornecidas"""
    # Converter coordenadas float para int
    left, top, right, bottom = map(int, crop_coords)
    
    # Verificar se as coordenadas estão dentro dos limites da imagem
    img_width, img_height = image.size
    left = max(0, min(left, img_width))
    top = max(0, min(top, img_height))
    right = max(left, min(right, img_width))
    bottom = max(top, min(bottom, img_height))
    
    return image.crop((left, top, right, bottom))

def resize_image(image, target_size):
    """Redimensiona a imagem mantendo a proporção"""
    return image.resize(target_size, Image.Resampling.LANCZOS)

def get_text_color_for_mode(mode):
    """
    Retorna cores de texto apropriadas para cada modo de cor
    """
    if mode in ['RGB', 'RGBA']:
        return {'text': (255, 255, 255), 'outline': (0, 0, 0)}  # Texto branco, contorno preto
    elif mode == 'CMYK':
        return {'text': (0, 0, 0, 0), 'outline': (0, 0, 0, 100)}  # Texto branco, contorno preto em CMYK
    elif mode in ['L', 'LA']:
        return {'text': 255, 'outline': 0}  # Texto branco, contorno preto para escala de cinza
    elif mode == '1':
        return {'text': 1, 'outline': 0}  # Texto branco, contorno preto para imagens binárias
    else:
        return {'text': 255, 'outline': 0}  # Padrão

def draw_text_on_image(image, text, font_height=126, y_position=50):
    """
    Desenha texto centralizado na imagem
    PRESERVA O MODO DE COR ORIGINAL
    
    Args:
        image: Imagem PIL onde o texto será desenhado
        text: Texto a ser desenhado
        font_height: Altura da fonte em pixels (padrão: 126px)
        y_position: Posição Y do texto em pixels da parte superior (padrão: 50px)
    
    Returns:
        Imagem PIL com o texto desenhado
    """
    try:
        # Criar uma cópia da imagem para não modificar a original
        img_with_text = image.copy()
        draw = ImageDraw.Draw(img_with_text)
        
        # Obter dimensões da imagem e modo de cor
        img_width, img_height = img_with_text.size
        original_mode = img_with_text.mode
        
        # Obter cores apropriadas para o modo de cor
        colors = get_text_color_for_mode(original_mode)
        
        # Tentar usar uma fonte TrueType, caso contrário usar fonte padrão
        try:
            # Tentar carregar uma fonte do sistema (ajuste o caminho conforme necessário)
            font_paths = [
                # Windows
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
                # Linux
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                # macOS
                "/System/Library/Fonts/Arial.ttf",
                "/System/Library/Fonts/Helvetica.ttc"
            ]
            
            font = None
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, font_height)
                    break
            
            # Se não encontrou nenhuma fonte, usar fonte padrão
            if font is None:
                font = ImageFont.load_default()
                print("⚠️  Usando fonte padrão - pode não ter exatamente 126px de altura")
                
        except Exception as e:
            print(f"⚠️  Erro ao carregar fonte personalizada: {e}")
            font = ImageFont.load_default()
        
        # Obter dimensões do texto
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        
        x_position = 10  # 10px de margem
        
        # Verificar se a posição Y não ultrapassa os limites da imagem
        if y_position + text_height > img_height:
            y_position = img_height - text_height - 10  # 10px de margem
        
        # Desenhar contorno preto para melhor legibilidade
        outline_width = max(1, font_height // 40)  # Espessura proporcional ao tamanho da fonte
        
        for adj_x in range(-outline_width, outline_width + 1):
            for adj_y in range(-outline_width, outline_width + 1):
                if adj_x != 0 or adj_y != 0:
                    draw.text((x_position + adj_x, y_position + adj_y), text, font=font, fill=colors['outline'])
        
        # Desenhar texto principal
        draw.text((x_position, y_position), text, font=font, fill=colors['text'])
        
        print(f"✏️  Texto '{text}' adicionado na posição ({x_position}, {y_position}) no modo {original_mode}")
        return img_with_text
        
    except Exception as e:
        print(f"⚠️  Erro ao adicionar texto à imagem: {e}")
        return image  # Retorna imagem original se houver erro

def get_save_format_and_params(image):
    """
    Determina o formato e parâmetros de salvamento baseado no modo de cor da imagem
    """
    mode = image.mode
    
    # Para imagens RGBA ou com transparência, salvar como PNG
    if mode in ['RGBA', 'LA'] or 'transparency' in image.info:
        return 'PNG', {}
    
    # Para imagens CMYK, salvar como JPEG com qualidade alta
    elif mode == 'CMYK':
        return 'JPEG', {'quality': 50, 'optimize': True, "dpi": (300, 300)}
    
    # Para outros modos (RGB, L, etc.), salvar como JPEG
    else:
        return 'JPEG', {'quality': 50, 'optimize': True, "dpi": (300, 300)}

def process_image(image, tamanhos_solicitados):
    """Processa a imagem principal gerando todos os crops e redimensionamentos"""
    try:
        # Criar diretório temporário para os resultados
        temp_dir = tempfile.mkdtemp()
        processed_files = []
        
        # Obter modo de cor original
        original_mode = image.mode
        print(f"🎨 Modo de cor original da imagem: {original_mode}")
        
        # PASSO 1: Redimensionar imagem para o tamanho do molde
        print("🎯 Redimensionando imagem para tamanho do molde...")
        molde_image = resize_to_molde(image)
        
        # Processar cada tamanho solicitado
        for tamanho, quantidade in tamanhos_solicitados.items():
            if tamanho not in TAMANHOS:
                continue
            
            target_size = TAMANHOS[tamanho]
            print(f"📏 Processando tamanho {tamanho} ({quantidade} unidades)")
            
            # Processar cada crop
            for crop_name, crop_coords in CROPS.items():
                print(f"✂️  Aplicando crop: {crop_name}")
                
                # Fazer o crop na imagem do molde
                cropped_image = crop_image(molde_image, crop_coords)
                
                # Se for FRENTE ou COSTAS, redimensionar
                if crop_name in CROPS_PARA_REDIMENSIONAR:
                    final_image = resize_image(cropped_image, target_size)
                    print(f"🔄 Redimensionando {crop_name} para {target_size}")
                else:
                    final_image = cropped_image
                
                # Adicionar texto com o tamanho na imagem
                final_image = draw_text_on_image(final_image, tamanho)
                
                # Determinar formato e parâmetros de salvamento baseado no modo de cor
                save_format, save_params = get_save_format_and_params(final_image)
                extension = save_format.lower()
                
                # Salvar arquivo único com formato: crop_name_tamanho_quantidade_unidades.extensao
                filename = f"{crop_name}_{tamanho}_{quantidade}_unidades.{extension}"
                filepath = os.path.join(temp_dir, filename)
                
                final_image.save(filepath, save_format, **save_params)
                processed_files.append(filepath)
                print(f"💾 Salvo: {filename} (formato: {save_format}, modo: {final_image.mode})")
        
        print(f"✅ Processamento concluído: {len(processed_files)} arquivos gerados")
        return temp_dir, processed_files
        
    except Exception as e:
        raise Exception(f"Erro ao processar imagem: {str(e)}")

def create_zip_file(files_dir, files_list):
    """Cria um arquivo ZIP com todos os arquivos processados"""
    zip_path = os.path.join(app.config['OUTPUT_FOLDER'], f"processed_images_{uuid.uuid4().hex[:8]}.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_list:
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname)
    
    return zip_path

@app.route('/', methods=['GET'])
def home():
    """Endpoint de informações da API"""
    return jsonify({
        "message": "API de Redimensionamento de Imagens",
        "version": "1.3",
        "molde_size": f"{SIZE_MOLDE[0]}x{SIZE_MOLDE[1]}",
        "color_mode_preservation": "Preserva o modo de cor original da imagem (RGB, CMYK, L, etc.)",
        "endpoints": {
            "POST /process": "Processa imagem via URL, arquivo local ou upload com crops e redimensionamento",
            "GET /tamanhos": "Lista tamanhos disponíveis",
            "GET /crops": "Lista crops disponíveis",
            "GET /download/<filename>": "Download do arquivo ZIP processado"
        },
        "formas_de_entrada": {
            "url": {
                "descricao": "Imagem via URL",
                "content_type": "application/json",
                "exemplo": {
                    "url": "https://exemplo.com/imagem.jpg",
                    "tamanhos": {
                        "G": 5,
                        "M": 10,
                        "P FEMININA": 8
                    }
                }
            },
            "arquivo_local": {
                "descricao": "Imagem de arquivo local",
                "content_type": "application/json",
                "exemplo": {
                    "local_path": "/caminho/para/imagem.jpg",
                    "tamanhos": {
                        "G": 5,
                        "M": 10
                    }
                }
            },
            "upload": {
                "descricao": "Upload de arquivo",
                "content_type": "multipart/form-data",
                "campos": {
                    "file": "Arquivo de imagem",
                    "tamanhos": "JSON string com tamanhos e quantidades"
                }
            }
        },
        "formato_arquivo": "crop_name_tamanho_quantidade_unidades.jpg/png (baseado no modo de cor)",
        "texto_adicionado": {
            "altura_fonte": "126px",
            "posicao": "10px da margem esquerda, 50px do topo",
            "cor": "adaptada ao modo de cor da imagem (texto branco com contorno preto)"
        },
        "tipos_arquivo_suportados": ["png", "jpg", "jpeg", "gif", "bmp", "tiff"],
        "tamanho_maximo": "500MB"
    })

@app.route('/tamanhos', methods=['GET'])
def get_tamanhos():
    """Retorna os tamanhos disponíveis"""
    return jsonify({
        "tamanhos_disponíveis": list(TAMANHOS.keys()),
        "detalhes": TAMANHOS,
        "molde_size": SIZE_MOLDE
    })

@app.route('/crops', methods=['GET'])
def get_crops():
    """Retorna informações sobre os crops"""
    return jsonify({
        "crops_disponíveis": list(CROPS.keys()),
        "crops_redimensionáveis": CROPS_PARA_REDIMENSIONAR,
        "coordenadas": CROPS,
        "molde_size": SIZE_MOLDE
    })

@app.route('/process', methods=['POST'])
def process_image_endpoint():
    """
    Endpoint principal para processar imagens
    
    Aceita três formas de entrada:
    
    1. JSON com URL:
    {
        "url": "https://exemplo.com/imagem.jpg",
        "tamanhos": {
            "G": 5,
            "M": 10,
            "P FEMININA": 8
        }
    }
    
    2. JSON com caminho local:
    {
        "local_path": "/caminho/para/imagem.jpg",
        "tamanhos": {
            "G": 5,
            "M": 10
        }
    }
    
    3. Multipart/form-data com upload:
    - file: arquivo de imagem
    - tamanhos: JSON string com tamanhos e quantidades
    """
    # Medição de memória e CPU no início
    memoria_antes = processo.memory_info().rss / (1024 * 1024)  # em MB
    cpu_antes = processo.cpu_percent()
    import time
    tempo_inicio = time.time()
    
    print(f"📊 Iniciando processamento:")
    print(f"   💾 Memória (antes): {memoria_antes:.2f} MB")
    print(f"   🖥️  CPU (antes): {cpu_antes:.2f}%")
    
    try:
        image = None
        image_source = ""
        tamanhos_data = None
        
        # Determinar tipo de entrada e processar
        if request.is_json:
            # Entrada via JSON
            data = request.get_json()
            
            # Verificar se há dados de tamanhos
            if 'tamanhos' not in data:
                return jsonify({"erro": "Dados de tamanhos não fornecidos"}), 400
            
            tamanhos_data = data['tamanhos']
            if not isinstance(tamanhos_data, dict):
                return jsonify({"erro": "Tamanhos deve ser um objeto"}), 400
            
            # Processar baseado no tipo de entrada
            if 'url' in data:
                # Entrada via URL
                image_url = data['url'].strip()
                if not image_url:
                    return jsonify({"erro": "URL da imagem não pode estar vazia"}), 400
                
                print(f"📥 Baixando imagem de: {image_url}")
                memoria_download_antes = processo.memory_info().rss / (1024 * 1024)
                image = download_image_from_url(image_url)
                memoria_download_depois = processo.memory_info().rss / (1024 * 1024)
                print(f"   💾 Memória após download: {memoria_download_depois:.2f} MB (+{memoria_download_depois - memoria_download_antes:.2f} MB)")
                image_source = f"URL: {image_url}"
                
            elif 'local_path' in data:
                # Entrada via caminho local
                local_path = data['local_path'].strip()
                if not local_path:
                    return jsonify({"erro": "Caminho local não pode estar vazio"}), 400
                
                print(f"📁 Carregando imagem local: {local_path}")
                memoria_download_antes = processo.memory_info().rss / (1024 * 1024)
                image = load_image_from_local_path(local_path)
                memoria_download_depois = processo.memory_info().rss / (1024 * 1024)
                print(f"   💾 Memória após carregamento: {memoria_download_depois:.2f} MB (+{memoria_download_depois - memoria_download_antes:.2f} MB)")
                image_source = f"Arquivo local: {local_path}"
                
            else:
                return jsonify({"erro": "Forneça 'url' ou 'local_path' no JSON"}), 400
                
        elif request.content_type and request.content_type.startswith('multipart/form-data'):
            # Entrada via upload de arquivo
            if 'file' not in request.files:
                return jsonify({"erro": "Arquivo não fornecido"}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({"erro": "Nenhum arquivo selecionado"}), 400
            
            # Verificar se dados de tamanhos foram fornecidos
            if 'tamanhos' not in request.form:
                return jsonify({"erro": "Dados de tamanhos não fornecidos no formulário"}), 400
            
            try:
                tamanhos_data = json.loads(request.form['tamanhos'])
                if not isinstance(tamanhos_data, dict):
                    return jsonify({"erro": "Tamanhos deve ser um objeto JSON válido"}), 400
            except json.JSONDecodeError:
                return jsonify({"erro": "Dados de tamanhos devem estar em formato JSON válido"}), 400
            
            print(f"📤 Carregando arquivo enviado: {file.filename}")
            memoria_download_antes = processo.memory_info().rss / (1024 * 1024)
            image = load_image_from_upload(file)
            memoria_download_depois = processo.memory_info().rss / (1024 * 1024)
            print(f"   💾 Memória após upload: {memoria_download_depois:.2f} MB (+{memoria_download_depois - memoria_download_antes:.2f} MB)")
            image_source = f"Upload: {file.filename}"
            
        else:
            return jsonify({"erro": "Content-Type deve ser application/json ou multipart/form-data"}), 400
        
        # Validar tamanhos solicitados
        for tamanho, quantidade in tamanhos_data.items():
            if tamanho not in TAMANHOS:
                return jsonify({"erro": f"Tamanho '{tamanho}' não é válido"}), 400
            if not isinstance(quantidade, int) or quantidade <= 0:
                return jsonify({"erro": f"Quantidade para '{tamanho}' deve ser um número inteiro positivo"}), 400
        
        try:
            
            # Processar imagem
            print("🔄 Processando imagem...")
            memoria_processo_antes = processo.memory_info().rss / (1024 * 1024)
            temp_dir, processed_files = process_image(image, tamanhos_data)
            memoria_processo_depois = processo.memory_info().rss / (1024 * 1024)
            print(f"   💾 Memória após processamento: {memoria_processo_depois:.2f} MB (+{memoria_processo_depois - memoria_processo_antes:.2f} MB)")
            
            # Criar ZIP com os arquivos processados
            print("📦 Criando arquivo ZIP...")
            memoria_zip_antes = processo.memory_info().rss / (1024 * 1024)
            zip_path = create_zip_file(temp_dir, processed_files)
            memoria_zip_depois = processo.memory_info().rss / (1024 * 1024)
            print(f"   💾 Memória após criação do ZIP: {memoria_zip_depois:.2f} MB (+{memoria_zip_depois - memoria_zip_antes:.2f} MB)")

            
            # Limpar arquivos temporários
            for temp_file in processed_files:
                try:
                    os.remove(temp_file)
                except:
                    pass
            os.rmdir(temp_dir)
            
            # Medições finais
            memoria_depois = processo.memory_info().rss / (1024 * 1024)
            cpu_depois = processo.cpu_percent()
            tempo_fim = time.time()
            tempo_total = tempo_fim - tempo_inicio
            
            # Cálculos de uso
            memoria_usada = memoria_depois - memoria_antes
            memoria_pico = max(memoria_download_depois, memoria_processo_depois, memoria_zip_depois)
            memoria_pico_delta = memoria_pico - memoria_antes
            
            print(f"📊 Processamento finalizado:")
            print(f"   💾 Memória final: {memoria_depois:.2f} MB")
            print(f"   📈 Memória pico: {memoria_pico:.2f} MB")
            print(f"   🔺 Delta total: {memoria_usada:.2f} MB")
            print(f"   🔺 Delta pico: {memoria_pico_delta:.2f} MB")
            print(f"   🖥️  CPU final: {cpu_depois:.2f}%")
            print(f"   ⏱️  Tempo total: {tempo_total:.2f}s")
            
            # Retornar informações do processamento
            total_files = len(processed_files)
            
            return jsonify({
                "sucesso": True,
                "mensagem": "Imagem processada com sucesso",
                "detalhes": {
                    "fonte_imagem": image_source,
                    "modo_cor_original": image.mode,
                    "molde_aplicado": f"{SIZE_MOLDE[0]}x{SIZE_MOLDE[1]}",
                    "tamanhos_processados": tamanhos_data,
                    "total_arquivos_gerados": total_files,
                    "crops_aplicados": list(CROPS.keys()),
                    "formato_arquivo": "crop_name_tamanho_quantidade_unidades.jpg/png (baseado no modo de cor)",
                    "texto_adicionado": f"Tamanho '{list(tamanhos_data.keys())}' com fonte de 126px",
                    "preservacao_cor": "Modo de cor original preservado em todo o processo",
                    "download_id": os.path.basename(zip_path)
                },
                "performance": {
                    "tempo_processamento": f"{tempo_total:.2f}s",
                    "memoria_inicial": f"{memoria_antes:.2f} MB",
                    "memoria_final": f"{memoria_depois:.2f} MB",
                    "memoria_pico": f"{memoria_pico:.2f} MB",
                    "memoria_consumida_total": f"{memoria_usada:.2f} MB",
                    "memoria_consumida_pico": f"{memoria_pico_delta:.2f} MB",
                    "detalhamento_memoria": {
                        "download": f"+{memoria_download_depois - memoria_download_antes:.2f} MB",
                        "processamento": f"+{memoria_processo_depois - memoria_processo_antes:.2f} MB",
                        "criacao_zip": f"+{memoria_zip_depois - memoria_zip_antes:.2f} MB"
                    },
                    "cpu_inicial": f"{cpu_antes:.2f}%",
                    "cpu_final": f"{cpu_depois:.2f}%"
                },
                "download_url": f"/download/{os.path.basename(zip_path)}"
            })
            
        except Exception as e:
            return jsonify({"erro": f"Erro no processamento: {str(e)}"}), 500
            
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Endpoint para download do arquivo ZIP processado"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            return jsonify({"erro": "Arquivo não encontrado"}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"imagens_processadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )
        
    except Exception as e:
        return jsonify({"erro": f"Erro no download: {str(e)}"}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({"erro": "Arquivo muito grande. Tamanho máximo: 500MB"}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({"erro": "Endpoint não encontrado"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"erro": "Erro interno do servidor"}), 500

if __name__ == '__main__':
    print("🚀 Iniciando API de Redimensionamento de Imagens")
    print(f"📐 Tamanho do molde: {SIZE_MOLDE[0]}x{SIZE_MOLDE[1]}")
    print("🎨 PRESERVAÇÃO DE COR: Modo de cor original será mantido (RGB, CMYK, L, etc.)")
    print("📋 Tamanhos disponíveis:", list(TAMANHOS.keys()))
    print("✂️  Crops disponíveis:", list(CROPS.keys()))
    print("🔄 Crops que serão redimensionados:", CROPS_PARA_REDIMENSIONAR)
    print("💾 Formato de arquivo: crop_name_tamanho_quantidade_unidades.jpg/png (baseado no modo de cor)")
    print("✏️  Texto: Tamanho desenhado em cada imagem (126px de altura, centralizado, 50px do topo)")
    print("🌐 API rodando em: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)