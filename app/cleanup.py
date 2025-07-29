import os
import time
from threading import Thread
import logging

# Configuração do logging
logger = logging.getLogger(__name__)

def cleanup_orphan_files(folder, max_age_seconds):
    """
    Remove arquivos órfãos de uma pasta que são mais antigos que max_age_seconds.
    """
    while True:
        try:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    try:
                        file_age = time.time() - os.path.getmtime(file_path)
                        if file_age > max_age_seconds:
                            os.remove(file_path)
                            logger.info(f"Arquivo órfão removido: {file_path}")
                    except FileNotFoundError:
                        # O arquivo pode ter sido removido por um download concorrente
                        logger.warning(f"Arquivo não encontrado durante a verificação de limpeza: {file_path}")
                        continue
        except Exception as e:
            logger.error(f"Erro durante a limpeza de arquivos órfãos: {e}", exc_info=True)
        
        # Espera 1 hora antes de verificar novamente
        time.sleep(3600)

def start_cleanup_thread(app):
    """
    Inicia a thread de limpeza de arquivos órfãos em segundo plano.
    """
    folder = app.config['OUTPUT_FOLDER']
    # Define um tempo de vida longo para arquivos órfãos (24 horas por padrão)
    max_age = app.config.get('MAX_ORPHAN_FILE_AGE_SECONDS', 86400)
    
    cleanup_thread = Thread(target=cleanup_orphan_files, args=(folder, max_age), daemon=True)
    cleanup_thread.start()
    logger.info("Thread de limpeza de arquivos órfãos iniciada.")
