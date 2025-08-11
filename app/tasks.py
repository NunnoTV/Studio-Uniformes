from celery import Celery
from PIL import Image, ImageDraw, ImageFont
import os
import zipfile
import tempfile
import uuid
from .config import Config
import io

# Para lidar com imagens grandes e evitar o DecompressionBombWarning,
# definimos o limite máximo de pixels como None (ilimitado).
Image.MAX_IMAGE_PIXELS = None

def make_celery(app_name=__name__):
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    return Celery(app_name, backend=redis_url, broker=redis_url)

celery = make_celery()

@celery.task
def process_image_task(image_data, tamanhos_solicitados):
    """
    Celery task to process an image.
    """
    image = Image.open(io.BytesIO(image_data))
    
    # The logic from process_image and create_zip_file goes here.
    # This is a simplified version for demonstration.
    # In a real application, you would move the full logic from app/processing.py here.
    
    temp_dir = tempfile.mkdtemp()
    processed_files = []

    # Simplified processing logic
    for tamanho, quantidade in tamanhos_solicitados.items():
        if tamanho not in Config.TAMANHOS:
            continue
        for crop_name, crop_coords in Config.CROPS.items():
            cropped_image = image.crop(crop_coords)
            
            # Determine the name of the crop for the dictionary of sizes
            if 'MANGA' in crop_name:
                tamanho_key = 'MANGAS'
            else:
                tamanho_key = crop_name

            if tamanho_key in Config.TAMANHOS[tamanho]:
                target_size = Config.TAMANHOS[tamanho][tamanho_key]
                # CORREÇÃO: Redimensiona a imagem e a atribui a 'final_image'.
                # A falta desta linha causava o UnboundLocalError.
                final_image = cropped_image.resize(target_size, Image.Resampling.LANCZOS)
            else:
                final_image = cropped_image

            draw = ImageDraw.Draw(final_image)
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except IOError:
                font = ImageFont.load_default()
            draw.text((10, 10), f"{tamanho} - {crop_name}", font=font, fill="red")

            filename = f"{crop_name}_{tamanho}_{quantidade}_unidades.jpg"
            filepath = os.path.join(temp_dir, filename)
            final_image.save(filepath, 'JPEG', quality=95)
            processed_files.append(filepath)

    zip_path = os.path.join(Config.OUTPUT_FOLDER, f"processed_images_{uuid.uuid4().hex[:8]}.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in processed_files:
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname)
            
    return zip_path
