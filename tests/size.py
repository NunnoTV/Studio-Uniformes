from PIL import Image
import io

image_data = open('tests/test_image.jpg', 'rb').read()

image = Image.open(io.BytesIO(image_data))

print(image.size)
