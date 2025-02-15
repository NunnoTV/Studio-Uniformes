# app/services/image_service.py
import os
import requests
from zipfile import ZipFile
from io import BytesIO
from PIL import Image, ImageDraw

from constants import (
    TAMANHOS,
    CROP_MANGA_ESQUERDA,
    CROP_MANGA_DIREITA,
    CROP_FRENTE,
    CROP_COSTAS,
    CROP_SHORT_ESQUERDO,
    CROP_SHORT_DIREITO,
    SIZE_CAMISA_SHORT,
    IMG_RESIZED_DIR,
    COMPRESSED_FILE,
    FONTE_NUMERO,
    FONTE_NOME,
    FONTE_INFO,
    FONTE_NUMERO_SHORT,
)
from utils.file_utils import criar_diretorio_se_nao_existir

def gerar_imagem(molde_resized, crop, texto, fonte, nome_arquivo, tamanho=None, numero=None):
    img = molde_resized.crop(crop)
    draw = ImageDraw.Draw(img)

    if texto:
        if isinstance(texto, tuple):
            draw.text((img.width / 2, 1417), texto[1], anchor="mt", font=FONTE_NOME)
            draw.text((img.width / 2, 2447), numero, anchor="mt", font=FONTE_NUMERO)
        else:
            draw.text((img.width / 2, 100), texto, anchor="mt", font=fonte)

    if tamanho:
        # Adiciona o texto com efeito de contorno (sombra)
        for x in range(-1, 2):
            for y in range(-1, 2):
                draw.text(((img.width / 2) + x, 100 + y), tamanho, anchor="mt", font=FONTE_INFO, fill=15)
        draw.text(((img.width / 2), 100), tamanho, anchor="mt", font=FONTE_INFO)

    if tamanho in TAMANHOS:
        img = img.resize(TAMANHOS[tamanho])
    elif tamanho:
        print(f"Tamanho {tamanho} não encontrado para {nome_arquivo}")

    output_path = os.path.join(IMG_RESIZED_DIR, f"{nome_arquivo}.jpg")
    img.save(output_path)

def costas(nome, numero, tamanho, molde_resized):
    gerar_imagem(molde_resized, CROP_COSTAS, (0, nome, 0), FONTE_NOME,
                 f"COSTAS - ({nome})({numero})", tamanho, numero)

def frentes(valor, tamanho, molde_resized):
    gerar_imagem(molde_resized, CROP_FRENTE, None, FONTE_INFO,
                 f"FRENTE {tamanho} - {valor} UND", tamanho)

def mangas(valor, tamanho, molde_resized):
    gerar_imagem(molde_resized, CROP_MANGA_DIREITA, None, None,
                 f"Manga Direita - {tamanho} - {valor} UND")
    gerar_imagem(molde_resized, CROP_MANGA_ESQUERDA, None, None,
                 f"Manga Esquerda - {tamanho} - {valor} UND")

def shorts_esquerdo(numero, tamanho, molde_resized):
    img = molde_resized.crop(CROP_SHORT_ESQUERDO)
    draw = ImageDraw.Draw(img)
    draw.text((3622, 5020), numero, anchor="mt", font=FONTE_NUMERO_SHORT, fill=15)
    if tamanho and tamanho in TAMANHOS:
        output_path = os.path.join(IMG_RESIZED_DIR, f"Short Esquerdo - numero {numero}.jpg")
        img.save(output_path)
    elif tamanho:
        print(f"Tamanho {tamanho} não encontrado para short numero {numero}")

def short_direito(valor, tamanho, molde_resized):
    gerar_imagem(molde_resized, CROP_SHORT_DIREITO, None, None,
                 f"Short Direito - {tamanho} - {valor} UND")

def listar(lista_str, molde_resized):
    contagem_tamanhos = {}
    linhas = lista_str.split()
    for linha in linhas:
        # Cada linha deve ter o formato: nome,numero,tamanho
        nome, numero, tamanho = linha.split(",")
        costas(nome, numero, tamanho, molde_resized)
        shorts_esquerdo(numero, tamanho, molde_resized)
        contagem_tamanhos[tamanho] = contagem_tamanhos.get(tamanho, 0) + 1

    for tamanho, valor in contagem_tamanhos.items():
        frentes(valor, tamanho, molde_resized)
        mangas(valor, tamanho, molde_resized)
        short_direito(valor, tamanho, molde_resized)

def comprimir_imagens():
    with ZipFile(COMPRESSED_FILE, 'w') as zipf:
        for root, dirs, files in os.walk(IMG_RESIZED_DIR):
            for file in files:
                filepath = os.path.join(root, file)
                # Salva somente o nome do arquivo dentro do zip
                zipf.write(filepath, arcname=file)
    return COMPRESSED_FILE

def process_image_request(lista, url_image):
    # Baixa a imagem a partir da URL
    response = requests.get(url_image, stream=True)
    response.raise_for_status()
    
    molde = Image.open(BytesIO(response.content))
    molde_resized = molde.resize(SIZE_CAMISA_SHORT, resample=Image.Resampling.LANCZOS)
    
    # Cria (ou recria) o diretório de saída
    criar_diretorio_se_nao_existir(IMG_RESIZED_DIR)
    
    # Processa a imagem gerando os cortes e textos
    listar(lista, molde_resized)
    # Compacta os arquivos gerados
    zip_file = comprimir_imagens()
    return zip_file
