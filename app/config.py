import os

class Config:
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size

    if os.getenv('VERCEL') == '1':
        # Use o diretório /tmp no ambiente Vercel (que é gravável)
        UPLOAD_FOLDER = '/tmp/uploads'
        OUTPUT_FOLDER = '/tmp/outputs'
    else:
        # Use diretórios locais para desenvolvimento
        # O __file__ aponta para app/config.py, então subimos um nível para a raiz do projeto.
        basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
        OUTPUT_FOLDER = os.path.join(basedir, 'outputs')

    # Tamanho do molde - medida padrão para redimensionar antes dos crops
    SIZE_MOLDE = (20942, 9449)

    TAMANHOS = {
        "EXG": {"FRENTE": (8031, 10709),
                "COSTAS": (8031, 10709),
                "MANGAS": (7278, 3779)
                },
        "XG": {"FRENTE": (7795, 10394),
               "COSTAS": (7795, 10394),
               "MANGAS": (7278, 3779)
               },
        "GG": {"FRENTE": (7559, 10079),
               "COSTAS": (7559, 10079),
               "MANGAS": (7278, 3779)
               },
        "G": {"FRENTE": (7323, 9764),
              "COSTAS": (7323, 9764),
              "MANGAS": (6614, 3189)
              },
        "M": {"FRENTE": (7087, 9449),
              "COSTAS": (7087, 9449),
              "MANGAS": (6614, 3189)
              },
        "P": {"FRENTE": (6850, 9134),
              "COSTAS": (6850, 9134),
              "MANGAS": (6614, 3189)
              },
        "PP": {"FRENTE": (6614, 8818),
               "COSTAS": (6614, 8818),
               "MANGAS": (6614, 3189)
               },
        "EXG FEMININA": {"FRENTE": (7795, 10394),
                         "COSTAS": (7795, 10394),
                         "MANGAS": (6614, 3189)
                         },
        "XG FEMININA": {"FRENTE": (7559, 10079),
                        "COSTAS": (7559, 10079),
                        "MANGAS": (6614, 3189)
                        },
        "GG FEMININA": {"FRENTE": (7323, 9764),
                        "COSTAS": (7323, 9764),
                        "MANGAS": (6614, 3189)
                        },
        "G FEMININA": {"FRENTE": (7087, 9449),
                       "COSTAS": (7087, 9449),
                       "MANGAS": (6614, 3189)
                       },
        "M FEMININA": {"FRENTE": (6850, 9134),
                       "COSTAS": (6850, 9134),
                       "MANGAS": (6614, 3189)
                       },
        "P FEMININA": {"FRENTE": (6614, 8818),
                       "COSTAS": (6614, 8818),
                       "MANGAS": (6614, 3189)
                       },
        "PP FEMININA": {"FRENTE": (6378, 8504),
                        "COSTAS": (6378, 8504),
                        "MANGAS": (6614, 3189)
                        },
        "16 ANOS": {"FRENTE": (6614, 8819),
                    "COSTAS": (6614, 8819),
                    "MANGAS": (6614, 3189)
                    },
        "14 ANOS": {"FRENTE": (6378, 8504),
                    "COSTAS": (6378, 8504),
                    "MANGAS": (6614, 3189)
                    },
        "12 ANOS": {"FRENTE": (6142, 8189),
                    "COSTAS": (6142, 8189),
                    "MANGAS": (5314, 2759)
                    },
        "10 ANOS": {"FRENTE": (5906, 7874),
                    "COSTAS": (5906, 7874),
                    "MANGAS": (5314, 2759)
                    },
        "8 ANOS": {"FRENTE": (5669, 7559),
                   "COSTAS": (5669, 7559),
                   "MANGAS": (5314, 2759)
                   },
        "6 ANOS": {"FRENTE": (5197, 6929),
                   "COSTAS": (5197, 6929),
                   "MANGAS": (5314, 2759)
                   },
        "4 ANOS": {"FRENTE": (4961, 6614),
                   "COSTAS": (4961, 6614),
                   "MANGAS": (5314, 2759)
                   },
        "2 ANOS": {"FRENTE": (4724, 6299),
                   "COSTAS": (4724, 6299),
                   "MANGAS": (5314, 2759)
                   }
    }

    # Coordenadas dos crops
    CROPS = {
        'MANGA_ESQUERDA': (0, 0, 6141.73, 3189.07 ),
        'MANGA_DIREITA': (0, 3493.76, 6141.73, 6682.83),
        'FRENTE': (6455.25, 0, 13541.87, 9448.91),
        'COSTAS': (13855.39, 0, 20942, 9448.91)
    }