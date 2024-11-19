import os
import uuid

def generate_short_uuid():
    return uuid.uuid4().hex[:10]

def rename_images_in_directory(directory, start_number=1):
    for root, dirs, files in os.walk(directory):
        count = start_number
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.JPG', '.jpeg', '.gif', '.bmp')):
                file_extension = os.path.splitext(file)[1]
                new_uuid = generate_short_uuid()
                new_name = f"{new_uuid}{file_extension}"
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, new_name)
                os.rename(old_path, new_path)
                count += 1

# Ruta de la carpeta principal que contiene las tres carpetas con subcarpetas
main_directory = ''

# Llamada a la función para renombrar imágenes en la carpeta principal y subcarpetas
rename_images_in_directory(main_directory)
