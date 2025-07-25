import os

class Config:
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    UPLOAD_FOLDER = 'uploads'
    OUTPUT_FOLDER = 'outputs'

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