import os
from PIL import ImageFont

# Diretório base (pasta app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Constantes de tamanhos e crops
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

# Caminhos de arquivos (ajuste conforme sua estrutura)
# Considera que a pasta "arquivos" está na raiz do projeto
FONT_PATH = os.path.join(BASE_DIR, "..", "arquivos", "fontes", "BRASIL NIKE 2018.TTF")
IMG_RESIZED_DIR = os.path.join(BASE_DIR, "..", "arquivos", "imagens_geradas")
COMPRESSED_FILE = os.path.join(BASE_DIR, "..", "arquivos", "uniforme_diagramado.zip")

# Carrega as fontes
FONTE_NUMERO = ImageFont.truetype(FONT_PATH, 3962)
FONTE_NOME = ImageFont.truetype(FONT_PATH, 794)
FONTE_INFO = ImageFont.truetype(FONT_PATH, 100)
FONTE_NUMERO_SHORT = ImageFont.truetype(FONT_PATH, 1132)