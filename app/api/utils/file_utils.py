import os
import shutil

def criar_diretorio_se_nao_existir(diretorio):
    if os.path.exists(diretorio):
        shutil.rmtree(diretorio)
    os.makedirs(diretorio)