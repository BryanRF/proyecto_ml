# app_ml/views.py
from datetime import datetime
import os
import numpy as np
from django.http import HttpResponse
from django.conf import settings
from rest_framework import viewsets, status
from django.core.files.base import ContentFile
from rest_framework.decorators import action
from rest_framework.response import Response

from app_ml.utils.filter_image import generate_filter_overlay
from .models import *
from .serializers import DatasetSerializer, EntrenamientoSerializer, PrediccionSerializer
from .utils.data_processing import load_and_preprocess_data, preprocess_single_image
from .ml_algorithms.logistic_regression import train_logistic_regression
from .ml_algorithms.neural_network import train_neural_network
from .ml_algorithms.svm import train_svm
from .ml_algorithms.naive_bayes import train_naive_bayes
from .ml_algorithms.decision_tree import train_decision_tree
from .utils.report_generation import generate_report, generate_comparison_report
import zipfile
from django.db import transaction
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.views.generic import View
import joblib
from django.core.files.storage import default_storage
from pusher import Pusher

def enviar_mensaje_pusher(channel, uuid, message, progreso=None):
    pusher_client = Pusher(
        app_id='1722267',
        key='be0524da244ba0c38862',
        secret='1af3100d62ea2b6d5c93',
        cluster='sa1',
        ssl=True
    )

    hora_actual = datetime.now()
    hora_formateada = hora_actual.strftime('%d/%m/%Y, %H:%M:%S')

    data = {
        'message': message,
        'hora': hora_formateada
    }

    if progreso is not None:
        data['progreso'] = progreso

    pusher_client.trigger(channel, uuid, data)
class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    @action(detail=False, methods=['post'])
    def train_dataset(self, request):
        name = request.data.get('name')
        datasetname = request.data.get('name')
        dataset_file = request.FILES.get('file')
        uuid = request.data.get('uuid')

        if not dataset_file:
            return Response({'mensaje': 'No se ha subido ningún archivo'}, status=status.HTTP_201_CREATED)

        temp_path = default_storage.save('temp_dataset.zip', ContentFile(dataset_file.read()))

        try:
            # Procesar el archivo subido
            with zipfile.ZipFile(default_storage.path(temp_path), 'r') as zip_file:
                file_list = zip_file.namelist()
                # print(file_list)

                # Cargar y preprocesar los datos
                X_train, X_test, y_train, y_test, le = load_and_preprocess_data(file_list, zip_file)

            # Verificar si ya existe un dataset con el mismo nombre
            if Dataset.objects.filter(name=name).exists():
                return Response({'mensaje': 'Ya existe un dataset con este nombre!'}, status=status.HTTP_201_CREATED)

            # Crear una nueva entrada de dataset
            dataset = Dataset.objects.create(name=name)
            unique_classes = np.unique(np.concatenate((y_train, y_test)))
            progreso = 0

            enviar_mensaje_pusher('my-channel', uuid, 'Se inició el entrenamiento correctamente.', progreso)

            # Crear clases en la base de datos
            for index, class_name in enumerate(unique_classes):
                Clase.objects.create(dataset=dataset, name=class_name, index=index)

            # Definir los algoritmos y entrenarlos
            algorithms = {
                # 'SVM': train_svm,
                # 'Naive Bayes': train_naive_bayes,
                'Decision Tree': train_decision_tree,
                'Logistic Regression': train_logistic_regression,
                # 'Neural Network': train_neural_network,
            }

            total_algorithms = len(algorithms)
            progreso_incremento = 100 / total_algorithms
            results = {}
            best_model = None
            best_accuracy = 0

            for i, (algo_name, train_func) in enumerate(algorithms.items(), start=1):
                enviar_mensaje_pusher('my-channel', uuid, f'Entrenamiento con el algoritmo {algo_name} iniciado.', progreso)

                try:
                    # Entrenar el modelo
                    result = train_func(X_train, y_train, X_test, y_test)
                    results[algo_name] = result

                    # Guardar resultados en la base de datos
                    Entrenamiento.objects.create(
                        dataset=dataset,
                        algorithm=algo_name,
                        accuracy=result['accuracy'],
                        precision=result['precision'],
                        recall=result['recall'],
                        f1_score=result['f1_score'],
                        auc=result['auc'],
                        cpu_usage=result['cpu_usage'],
                        execution_time=result['execution_time']
                    )

                    # Verificar si es el mejor modelo
                    if result['accuracy'] > best_accuracy:
                        best_accuracy = result['accuracy']
                        best_model = result['model']

                    progreso += progreso_incremento
                    enviar_mensaje_pusher('my-channel', uuid, f'Entrenamiento con el algoritmo {algo_name} finalizado.', progreso)

                except Exception as e:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    print(f"Error entrenando con el algoritmo {algo_name}: {e}")
                    enviar_mensaje_pusher('my-channel', uuid, f'Error con el algoritmo {algo_name}.', progreso)

            # Guardar el mejor modelo entrenado
            if best_model:
                model_path = f'media/mejor_modelo_{dataset.id}.joblib'
                joblib.dump(best_model, os.path.join(settings.MEDIA_ROOT, model_path))
                dataset.best_model_path = model_path
                dataset.save()

            enviar_mensaje_pusher('my-channel', uuid, f'El dataset {datasetname} fue entrenado exitosamente.', 100)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return Response({'mensaje': 'Dataset entrenado exitosamente', 'creacion': dataset.id}, status=status.HTTP_201_CREATED)

        except IntegrityError as e :
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return Response({'mensaje': f'{str(e)}'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error general: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return Response({'mensaje': f'Error al entrenar el dataset: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            # Asegurar que se elimine el archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)

class ClassificationViewSet(viewsets.ModelViewSet):
    queryset = Prediccion.objects.all()
    serializer_class = PrediccionSerializer

    @action(detail=False, methods=['post'])
    def classify_image(self, request):
        image = request.FILES.get('image')
        dataset_id = request.data.get('dataset_id')

        if not image or not dataset_id:
            return Response({'mensaje': 'Requiere dataset seleccionado'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dataset = Dataset.objects.get(id=dataset_id)
        except Dataset.DoesNotExist:
            return Response({'mensaje': 'Dataset no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if not dataset.best_model_path:
            return Response({'mensaje': 'El modelo del dataset fue eliminado'}, status=status.HTTP_404_NOT_FOUND)

        # Cargar mejor modelo
        best_model = joblib.load(dataset.best_model_path)

        # Procesar imagen
        X = preprocess_single_image(image)

        if X is None:
            return Response({'mensaje': 'Error al procesar la imagen'}, status=status.HTTP_400_BAD_REQUEST)

        # Clasificar imagen
        prediction = best_model.predict(X)[0]
        confidence = best_model.predict_proba(X)[0].max()

        try:
            predicted_class = Clase.objects.get(dataset=dataset, name=prediction)
        except Clase.DoesNotExist:
            return Response({'mensaje': 'La predicción no tiene clases registradas. Vuelve a entrenar otro dataset.'}, status=status.HTTP_404_NOT_FOUND)

        # Crear la predicción en la base de datos
        Prediccion.objects.create(
            dataset=dataset,
            image=image,
            predicted_class=predicted_class,
            confidence=confidence
        )

        # Incluir más detalles de la clase
        color = predicted_class.tipo_clase.color if predicted_class.tipo_clase.color else None
        print(color)
        filter_image_path = None
        if not predicted_class.normal and color !=None:
            filter_image_path = generate_filter_overlay(image, color)  # Generar imagen con filtro

        # Incluir más detalles de la clase
        response_data = {
            'predicted_class': predicted_class.name,
            'confidence': confidence,
            'description': predicted_class.description,
            'tipo_clase': predicted_class.tipo_clase.name if predicted_class.tipo_clase else "Sin tipo",
            'filter_image_url': filter_image_path if filter_image_path else None,
             'normal': predicted_class.normal
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def generate_report(self, request):
        dataset_id = request.GET.get('dataset_id')

        if not dataset_id:
            return Response({'mensaje': 'Se requiere un dataset seleccionado'}, status=status.HTTP_201_CREATED)

        try:
            dataset = get_object_or_404(Dataset, id=dataset_id)
        except Dataset.DoesNotExist:
            return Response({'mensaje': 'Dataset no encontrado'}, status=status.HTTP_201_CREATED)

        if dataset.file and os.path.exists(os.path.join(settings.MEDIA_ROOT, dataset.file.name)):
            report_path = os.path.join(settings.MEDIA_ROOT, dataset.file.name)
            return FileResponse(
                open(report_path, 'rb'),
                as_attachment=True,
                filename=f'reporte_{dataset_id}.pdf'
            )
        else:
            training_results = Entrenamiento.objects.filter(dataset=dataset)

            if not training_results:
                return Response({'mensaje': 'No se encontraron datos entrenados'}, status=status.HTTP_201_CREATED)

            results = {result.algorithm: {
                'accuracy': result.accuracy,
                'precision': result.precision,
                'recall': result.recall,
                'f1_score': result.f1_score,
                'auc': result.auc,
                'cpu_usage': result.cpu_usage,
                'execution_time': result.execution_time
            } for result in training_results}

            report_path = os.path.join(settings.MEDIA_ROOT, 'media', f'report_{dataset_id}.pdf')
            try:
                generate_comparison_report(results, report_path)
                dataset.file = f'media/reporte_{dataset_id}.pdf'  # Actualizamos el campo file con la ruta del PDF
                dataset.save()
            except Exception as e:
                return Response({'mensaje': f'Error al generar reporte: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if os.path.exists(report_path):
                return FileResponse(
                    open(report_path, 'rb'),
                    as_attachment=True,
                    filename=f'reporte_{dataset_id}.pdf'
                )
            else:
                return Response({'mensaje': 'Error de sistema '}, status=status.HTTP_201_CREATED)