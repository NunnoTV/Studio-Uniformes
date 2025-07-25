import json
from flask import Blueprint, request, jsonify, send_file, current_app
from .utils import download_image_from_url, load_image_from_local_path, load_image_from_upload
from .processing import process_image, create_zip_file
from .config import Config
import os
from datetime import datetime
import shutil # For cleaning up temporary directories

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def home():
    """Endpoint de informações da API"""
    return jsonify({
        "message": "API de Redimensionamento de Imagens",
        "version": "1.3",
        "molde_size": f"{Config.SIZE_MOLDE[0]}x{Config.SIZE_MOLDE[1]}",
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
            "posicao": "10px da esquerda, 50px do topo",
            "cor": "adaptada ao modo de cor da imagem"
        }
    })

@main_bp.route('/tamanhos', methods=['GET'])
def get_tamanhos():
    """Retorna os tamanhos disponíveis"""
    return jsonify({
        "tamanhos_disponíveis": list(Config.TAMANHOS.keys()),
        "detalhes": Config.TAMANHOS,
        "molde_size": Config.SIZE_MOLDE
    })

@main_bp.route('/crops', methods=['GET'])
def get_crops():
    """Retorna informações sobre os crops"""
    return jsonify({
        "crops_disponíveis": list(Config.CROPS.keys()),
        "crops_redimensionáveis": Config.CROPS_PARA_REDIMENSIONAR,
        "coordenadas": Config.CROPS,
        "molde_size": Config.SIZE_MOLDE
    })

@main_bp.route('/process', methods=['POST'])
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
                image = download_image_from_url(image_url)
                image_source = f"URL: {image_url}"
                
            elif 'local_path' in data:
                # Entrada via caminho local
                local_path = data['local_path'].strip()
                if not local_path:
                    return jsonify({"erro": "Caminho local não pode estar vazio"}), 400
                
                print(f"📁 Carregando imagem local: {local_path}")
                image = load_image_from_local_path(local_path)
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
            image = load_image_from_upload(file)
            image_source = f"Upload: {file.filename}"
            
        else:
            return jsonify({"erro": "Content-Type deve ser application/json ou multipart/form-data"}), 400
        
        # Verificar se a imagem foi carregada corretamente
        if image is None:
            return jsonify({"erro": "Falha ao carregar a imagem"}), 400
        
        # Validar tamanhos solicitados
        for tamanho, quantidade in tamanhos_data.items():
            if tamanho not in Config.TAMANHOS:
                return jsonify({"erro": f"Tamanho '{tamanho}' não é válido"}), 400
            if not isinstance(quantidade, int) or quantidade <= 0:
                return jsonify({"erro": f"Quantidade para '{tamanho}' deve ser um número inteiro positivo"}), 400
        
        temp_dir = None # Initialize to None for finally block
        try:
            
            # Processar imagem
            current_app.logger.info("🔄 Processando imagem...")
            temp_dir, processed_files = process_image(image, tamanhos_data)
            
            # Criar ZIP com os arquivos processados
            current_app.logger.info("📦 Criando arquivo ZIP...")
            zip_path = create_zip_file(temp_dir, processed_files)

            # Retornar informações do processamento
            total_files = len(processed_files)
            
            return jsonify({
                "sucesso": True,
                "mensagem": "Imagem processada com sucesso",
                "detalhes": {
                    "fonte_imagem": image_source,
                    "modo_cor_original": image.mode,
                    "molde_aplicado": f"{Config.SIZE_MOLDE[0]}x{Config.SIZE_MOLDE[1]}",
                    "tamanhos_processados": tamanhos_data,
                    "total_arquivos_gerados": total_files,
                    "crops_aplicados": list(Config.CROPS.keys()),
                    "formato_arquivo": "crop_name_tamanho_quantidade_unidades.jpg/png (baseado no modo de cor)",
                    "texto_adicionado": f"Tamanho '{list(tamanhos_data.keys())}' com fonte de 126px",
                    "preservacao_cor": "Modo de cor original preservado em todo o processo",
                    "download_id": os.path.basename(zip_path)
                },
                "download_url": f"/download/{os.path.basename(zip_path)}"
            })
            
        except Exception as e:
            current_app.logger.error(f"Erro no processamento da imagem: {str(e)}", exc_info=True)
            return jsonify({"erro": f"Erro no processamento: {str(e)}"}), 500
        finally:
            # Limpar diretório temporário após o processamento, se existir
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    current_app.logger.info(f"Diretório temporário limpo: {temp_dir}")
                except Exception as e:
                    current_app.logger.error(f"Erro ao limpar diretório temporário {temp_dir}: {str(e)}")
            
    except Exception as e:
        current_app.logger.error(f"Erro interno no endpoint: {str(e)}", exc_info=True)
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

@main_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Endpoint para download do arquivo ZIP processado"""
    try:
        file_path = os.path.join(current_app.config['OUTPUT_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            current_app.logger.warning(f"Tentativa de download de arquivo não encontrado: {filename}")
            return jsonify({"erro": "Arquivo não encontrado"}), 404
        
        current_app.logger.info(f"Servindo download de arquivo: {filename}")
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"imagens_processadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )
        
    except Exception as e:
        current_app.logger.error(f"Erro no download do arquivo {filename}: {str(e)}", exc_info=True)
        return jsonify({"erro": f"Erro no download: {str(e)}"}), 500