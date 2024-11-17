# app_ml/utils/data_processing.py
import os
from PIL import Image
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder



def preprocess_single_image(image):
    try:
        img = Image.open(image)
        img = img.convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img).flatten()  # Aplanar la imagen
        return img_array.reshape(1, -1)  # Necesitamos devolver una forma de 2D para scikit-learn
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def load_and_preprocess_data(file_list, zip_file):
    images = []
    labels = []
    total_files = len(file_list)
    processed_files = 0

    for i, file_name in enumerate(file_list):
        # Ignorar directorios
        if file_name.endswith('/'):
            continue

        try:
            # Leer archivo de la carpeta comprimida
            with zip_file.open(file_name) as file:
                image = Image.open(file)
                image = image.convert('RGB')  # Asegúrate de que todas las imágenes sean RGB
                image = image.resize((224, 224))  # Redimensionar la imagen
                image_array = np.array(image).flatten()  # Aplanar la imagen
                images.append(image_array)

                # Suponiendo que el nombre de la carpeta es la etiqueta
                label = os.path.basename(os.path.dirname(file_name))
                labels.append(label)
        except Exception as e:
            print(f"Error processing image {file_name}: {e}")

        # Actualizar el progreso y enviar notificación cada 50 archivos
        processed_files += 1
 
   
    images = np.array(images)
    labels = np.array(labels)
    # print('labels')
    # print(labels)

    # Ya no necesitamos LabelEncoder aquí
    # Dividir en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test, None  # Retornamos None en lugar de le