from PIL import Image, ImageDraw, ImageFont
import os
import zipfile
import tempfile
import uuid
from .config import Config

# Adicionado para pré-redimensionamento
MAX_IMAGE_SIZE = (4000, 4000)  # Define um tamanho máximo para a imagem de entrada

def pre_resize_image(image, max_size=MAX_IMAGE_SIZE):
    """
    Redimensiona a imagem se ela exceder as dimensões máximas, mantendo a proporção.
    """
    if image.width > max_size[0] or image.height > max_size[1]:
        print(f"⚠️  Imagem original ({image.width}x{image.height}) excede o limite de {max_size[0]}x{max_size[1]}.")
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        print(f"➡️  Imagem pré-redimensionada para {image.width}x{image.height} para economizar memória.")
    return image

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
        target_width, target_height = Config.SIZE_MOLDE
        
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
        final_image = Image.new(original_mode, Config.SIZE_MOLDE, fill_color)
        
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
    
    # Para imagens CMYK, salvar como JPEG com qualidade otimizada
    elif mode == 'CMYK':
        return 'JPEG', {'quality': 45, 'optimize': True, "dpi": (300, 300)}
    
    # Para outros modos (RGB, L, etc.), salvar como JPEG
    else:
        return 'JPEG', {'quality': 45, 'optimize': True, "dpi": (300, 300)}

def process_image(image, tamanhos_solicitados):
    """Processa a imagem principal gerando todos os crops e redimensionamentos"""
    try:
        # PASSO 0: Pré-redimensionar a imagem para evitar consumo excessivo de memória
        image = pre_resize_image(image)

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
            if tamanho not in Config.TAMANHOS:
                continue

            print(f"📏 Processando tamanho {tamanho} ({quantidade} unidades)")

            # Processar cada crop
            for crop_name, crop_coords in Config.CROPS.items():
                print(f"✂️  Aplicando crop: {crop_name}")

                # Fazer o crop na imagem do molde
                cropped_image = crop_image(molde_image, crop_coords)

                # Determinar o nome do crop para o dicionário de tamanhos
                if 'MANGA' in crop_name:
                    tamanho_key = 'MANGAS'
                else:
                    tamanho_key = crop_name

                # Redimensionar o crop para o tamanho específico
                if tamanho_key in Config.TAMANHOS[tamanho]:
                    target_size = Config.TAMANHOS[tamanho][tamanho_key]
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
    zip_path = os.path.join(Config.OUTPUT_FOLDER, f"processed_images_{uuid.uuid4().hex[:8]}.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_list:
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname)
    
    return zip_path
