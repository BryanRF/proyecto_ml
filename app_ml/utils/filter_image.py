from PIL import Image  # Asegúrate de importar PIL
import cv2
import os
import uuid
import numpy as np
from django.conf import settings

def generate_filter_overlay(original_image, color_to_highlight="#836752"):
    # Abrir la imagen usando PIL
    pil_image = Image.open(original_image).convert('RGB')  # Asegurarse de trabajar en RGB
    width, height = pil_image.size  # Obtener dimensiones de la imagen

    # Convertir la imagen PIL a formato numpy
    original_np = np.array(pil_image)

    # Convertir el color objetivo de HEX a RGB
    target_color = tuple(int(color_to_highlight.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

    # Convertir a HSV para una mejor detección de colores
    hsv_image = cv2.cvtColor(original_np, cv2.COLOR_RGB2HSV)
    target_hsv = cv2.cvtColor(np.uint8([[target_color]]), cv2.COLOR_RGB2HSV)[0][0]

    # Definir rangos de color (variantes del color)
    lower_bound = np.array([target_hsv[0] - 10, 50, 50])  # Hue, Saturation, Value mín.
    upper_bound = np.array([target_hsv[0] + 10, 255, 255])  # Hue, Saturation, Value máx.

    # Crear una máscara para detectar el color en la imagen
    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)

    # Encontrar contornos en la máscara
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Dibujar rectángulos alrededor de las áreas detectadas
    for contour in contours:
        if cv2.contourArea(contour) > 100:  # Filtrar áreas muy pequeñas
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(original_np, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Rectángulo rojo (BGR: 255, 0, 0)

    # Guardar la imagen resultante
    file_name = f"filtered_{uuid.uuid4().hex}.png"
    file_path = os.path.join(settings.MEDIA_ROOT, "filters", file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    cv2.imwrite(file_path, cv2.cvtColor(original_np, cv2.COLOR_RGB2BGR))

    # Retornar la URL para acceso al cliente
    return os.path.join(settings.MEDIA_URL, "filters", file_name)
