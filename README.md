# Proyecto Django de Clasificación de Imágenes

Este proyecto utiliza Django y Django REST Framework para clasificar imágenes utilizando varios algoritmos de machine learning.

## Instalación

### Requisitos previos

- Python 3.8.10
- pip (instalado junto con Python)
- GitHub Desktop
- Potato Dataset de Kaggle (opcional, para pruebas): https://www.kaggle.com/datasets/arjuntejaswi/plant-village

### Pasos para la instalación

1. **Clonar el repositorio:**
   - Abre GitHub Desktop
   - Selecciona File > Clone Repository
   - Elige el repositorio del proyecto
   - Selecciona la ubicación local donde quieres clonar el proyecto
   - Haz clic en "Clone"

2. **Crear y activar un entorno virtual:**

   ```bash
   python -m venv venv
```
   # En sistemas Linux/Mac
     ```bash
   source venv/bin/activate
```
   # En Windows
     ```bash
   venv\Scripts\activate
   ```

3. **Instalar las dependencias del proyecto:**


Las dependencias del proyecto están listadas en el archivo `requirements.txt`. Para generar o actualizar este archivo, ejecuta el siguiente comando en tu entorno virtual:

    ```bash
    pip freeze > requirements.txt
    ```
    Para instalar nuevas librerias:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   Crea un archivo `.env` en la raíz del proyecto y configura las variables necesarias, como claves secretas y configuraciones específicas.

5. **Aplicar migraciones de la base de datos:**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Crear un superusuario:**

   ```bash
   python manage.py createsuperuser
   ```

   Sigue las instrucciones en la consola para crear un superusuario con acceso al panel de administración.

## Ejecución

### Ejecutar el servidor de desarrollo

Para ejecutar el servidor de desarrollo de Django:

```bash
python manage.py runserver
```

Esto iniciará el servidor en `http://localhost:8000/`.

## APIs Disponibles

### API de Conjuntos de Datos (datasets)

- **GET** `/api/datasets/`: Obtener todos los conjuntos de datos.
- **POST** `/api/datasets/train_dataset/`: Entrenar un nuevo conjunto de datos.

### API de Clasificación de Imágenes (classifications)

- **POST** `/api/classifications/classify_image/`: Clasificar una imagen utilizando el modelo entrenado.
- **GET** `/api/classifications/generate_report/?dataset_id=<dataset_id>`: Generar un informe de los resultados del entrenamiento para un conjunto de datos específico.

## URLs y Enrutamiento

En `app_ml/urls.py`, las URLs se configuran de la siguiente manera:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DatasetViewSet, ClassificationViewSet

router = DefaultRouter()
router.register(r'datasets', DatasetViewSet)
router.register(r'classifications', ClassificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('train_dataset/', DatasetViewSet.as_view({'post': 'train_dataset'}), name='train_dataset'),
    path('classify_image/', ClassificationViewSet.as_view({'post': 'classify_image'}), name='classify_image'),
    path('generate_report/', ClassificationViewSet.as_view({'get': 'generate_report'}), name='generate_report'),
]
```

## Modelos y Migraciones

El proyecto utiliza modelos de Django para representar los datos. Cuando se realizan cambios en los modelos (en `models.py`), es necesario crear y aplicar migraciones:

1. Crear migraciones después de cambios en los modelos:
   ```bash
   python manage.py makemigrations
   ```

2. Aplicar las migraciones a la base de datos:
   ```bash
   python manage.py migrate
   ```

Asegúrate de realizar estos pasos cada vez que modifiques la estructura de los modelos.


## Panel de Administración

Para acceder al panel de administración de Django:

1. Asegúrate de haber creado un superusuario (paso 6 de la instalación).
2. Inicia el servidor de desarrollo.
3. Visita `http://localhost:8000/admin/` en tu navegador.
4. Ingresa con las credenciales del superusuario.

Desde aquí podrás gestionar los modelos y datos de tu aplicación.

## Contribución

Si deseas contribuir al proyecto:

1. Crea una nueva rama en GitHub Desktop.
2. Realiza tus cambios y haz commit desde GitHub Desktop.
3. Publica la rama y crea un Pull Request desde la interfaz de GitHub.

¡Gracias por contribuir!
```

Puedes guardar este contenido directamente como un archivo llamado "README.md" en la carpeta raíz de tu proyecto. Este archivo proporcionará una guía completa para cualquier persona que quiera configurar y ejecutar tu proyecto Django de clasificación de imágenes.