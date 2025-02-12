import os, shutil
import requests
from PIL import Image, ImageFont, ImageDraw
from flask import Flask, request, send_file, jsonify
from io import BytesIO
from zipfile import ZipFile

app = Flask(__name__)





# Constantes
TAMANHOS = {
    "tamanho": (7913, 10703),
    "EXG": (7913, 10703),
    "XG": (7913, 10703),
    "GG": (7913, 10703),
    "G": (7322, 9904),
    "M": (7086, 9583),
    "P": (7086, 9583),
    "PP": (7086, 9583),
    "EXG FEMININA": (7913, 10703),
    "XG FEMININA": (7913, 10703),
    "GG FEMININA": (7913, 10703),
    "G FEMININA": (7322, 9904),
    "M FEMININA": (7086, 9583),
    "P FEMININA": (7086, 9583),
    "PP FEMININA": (7086, 9583),
}

CROP_MANGA_ESQUERDA = (0, 0, 6141.73, 3188.98)
CROP_MANGA_DIREITA = (0, 3493.66, 6141.73, 6682.63)
CROP_FRENTE = (6631.23, 0, 13717.85, 9448.82)
CROP_COSTAS = (14031.5, 0, 21072.41, 9448.82)
CROP_SHORT_ESQUERDO = (11032.57, 9636.66, 21072.41, 17313.2)
CROP_SHORT_DIREITO = (0, 9636.66, 10042, 17313.2)

SIZE_CAMISA_SHORT = (21118, 17313)

CAMINHO_FONTE = "arquivos/BRASIL NIKE 2018.TTF"
FONTE_NUMERO = ImageFont.truetype(CAMINHO_FONTE, 3962)
FONTE_NOME = ImageFont.truetype(CAMINHO_FONTE, 794)
FONTE_INFO = ImageFont.truetype(CAMINHO_FONTE, 100)
FONTE_NUMERO_SHORT = ImageFont.truetype(CAMINHO_FONTE, 1132)

IMG_RESIZED_DIR = "generated_images"



# Funções auxiliares
def criar_diretorio_se_nao_existir(diretorio):
    if os.path.exists(diretorio):
        shutil.rmtree(diretorio)
        os.makedirs(diretorio)
    else:
        os.makedirs(diretorio)

        
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
        for x in range(-1, 2):
            for y in range(-1, 2):
                draw.text(((img.width / 2) + x, 100 + y), tamanho, anchor="mt", font=FONTE_INFO, fill=15)
        draw.text(((img.width / 2), 100), tamanho, anchor="mt", font=FONTE_INFO)

    if tamanho in TAMANHOS:
        img = img.resize(TAMANHOS[tamanho])
    elif tamanho:
        print(f"Tamanho {tamanho} não encontrado para {nome_arquivo}")

    img.save(f"{IMG_RESIZED_DIR}/{nome_arquivo}.jpg")

def costas(nome, numero, tamanho, molde_resized):
    gerar_imagem(molde_resized, CROP_COSTAS, (0, nome, 0), FONTE_NOME, f"COSTAS - ({nome})({numero})", tamanho, numero)

def frentes(valor, tamanho, molde_resized):
    gerar_imagem(molde_resized, CROP_FRENTE, None, FONTE_INFO, f"FRENTE {tamanho} - {valor} UND", tamanho)

def mangas(valor, tamanho, molde_resized):
    gerar_imagem(molde_resized, CROP_MANGA_DIREITA, None, None, f"Manga Direita - {tamanho} - {valor} UND")
    gerar_imagem(molde_resized, CROP_MANGA_ESQUERDA, None, None, f"Manga Esquerda - {tamanho} - {valor} UND")

def shorts_esquerdo(numero, tamanho, molde_resized):
    img = molde_resized.crop(CROP_SHORT_ESQUERDO)
    draw = ImageDraw.Draw(img)
    draw.text((3622, 5020), numero, anchor="mt", font=FONTE_NUMERO_SHORT, fill=15)
    if tamanho and tamanho in TAMANHOS:
        img.save(f"{IMG_RESIZED_DIR}/Short Esquerdo - numero {numero}.jpg")
    elif tamanho:
        print(f"Tamanho {tamanho} não encontrado para short numero {numero}")

def short_direito(valor, tamanho, molde_resized):
    gerar_imagem(molde_resized, CROP_SHORT_DIREITO, None, None, f"Short Direito - {tamanho} - {valor} UND")

def listar(string, molde_resized):
    contagem_tamanhos = {}
    leitor = string.split()
    for linha in leitor:
        nome, numero, tamanho = linha.split(",")
        costas(nome, numero, tamanho, molde_resized)
        shorts_esquerdo(numero, tamanho, molde_resized)
        contagem_tamanhos[tamanho] = contagem_tamanhos.get(tamanho, 0) + 1

    for tamanho, valor in contagem_tamanhos.items():
        frentes(valor, tamanho, molde_resized)
        mangas(valor, tamanho, molde_resized)
        short_direito(valor, tamanho, molde_resized)

filename = "arquivos/compress.zip"

def comprimir():

    with ZipFile(filename, 'w') as zip:
        for root, dirs, files in os.walk(IMG_RESIZED_DIR):
            for file in files:
                filepath = os.path.join(root, file)
                zip.write(filepath)
    return filename

def download(filename):
    return send_file(filename, as_attachment=True)

@app.route("/", methods=["POST"])
def diagramar():
    try:
        dados = request.get_json()
        string = dados.get("lista")
        url_image = dados.get("imagem")
        
        response = requests.get(url_image, stream=True)
        response.raise_for_status()
        
        molde = Image.open(BytesIO(response.content))
        molde_resized = molde.resize(SIZE_CAMISA_SHORT, resample=Image.Resampling.LANCZOS)

        criar_diretorio_se_nao_existir(IMG_RESIZED_DIR)
        listar(string, molde_resized)
        filename = comprimir()
        
        return jsonify("Arquivo diagramado com sucesso")
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/download", methods=["GET"])
def download():
        return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))