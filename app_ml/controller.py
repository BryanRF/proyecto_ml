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
from .models import *
from .serializers import DatasetSerializer, TrainingResultSerializer, ClassificationResultSerializer
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
            
                # Guardar el archivo subido temporalmente

                # Procesar el archivo
                with zipfile.ZipFile(default_storage.path(temp_path), 'r') as zip_file:
                    file_list = zip_file.namelist()
                    print(file_list)

                    # Cargar y preprocesar los datos
                    X_train, X_test, y_train, y_test, le = load_and_preprocess_data(file_list, zip_file)

                # Verificar si ya existe un dataset con el mismo nombre
                existing_dataset = Dataset.objects.filter(name=name).exists()
                if existing_dataset:
                    return Response({'mensaje': 'Ya existe un dataset con este nombre'}, status=status.HTTP_201_CREATED)

                # Crear una nueva entrada de dataset
                dataset = Dataset.objects.create(name=name)
                unique_classes = np.unique(np.concatenate((y_train, y_test)))
                progreso=0
                enviar_mensaje_pusher('my-channel', uuid, f'Se inicio entrenamiento correctamente.', progreso)
                for index, class_name in enumerate(unique_classes):
                    DatasetClass.objects.create(dataset=dataset, name=class_name, index=index)
                                # Entrenar todos los modelos
                algorithms = {
                    'SVM': train_svm, #5 -15 %
                    'Naive Bayes': train_naive_bayes, #20 -35 %
                    'Decision Tree': train_decision_tree, #40 -55 %
                    'Logistic Regression': train_logistic_regression, #60 -75 %
                    'Neural Network': train_neural_network, #80 -95 %
                }

                results = {}
                best_model = None
                best_accuracy = 0
                
                progreso=0
                for name, train_func in algorithms.items():
                    hora_actual = datetime.now()
                    progreso+=5
                    print(f'Algoritmo en proceso {name}')
                    enviar_mensaje_pusher('my-channel', uuid, f'Entrenamiento con el algoritmo {name} iniciado.', progreso)
                    
                    result = train_func(X_train, y_train, X_test, y_test)
                    results[name] = result
                    
               
                    
                    # Guardar el resultado del entrenamiento
                    TrainingResult.objects.create(
                        dataset=dataset,
                        algorithm=name,
                        accuracy=result['accuracy'],
                        precision=result['precision'],
                        recall=result['recall'],
                        f1_score=result['f1_score'],
                        auc=result['auc'],
                        cpu_usage=result['cpu_usage'],
                        execution_time=result['execution_time']
                    )
                    

                    # Mantener el registro del mejor modelo
                    if result['accuracy'] > best_accuracy:
                        best_accuracy = result['accuracy']
                        best_model = result['model']
                        
                    progreso+=10
                    enviar_mensaje_pusher('my-channel', uuid, f'Entrenamiento con el algoritmo {name} finalizado.', progreso)
                    

                # Guardar el mejor modelo
                if best_model:
                    model_path = f'media/mejor_modelo_{dataset.id}.joblib'
                    joblib.dump(best_model, os.path.join(settings.MEDIA_ROOT, model_path))
                    dataset.best_model_path = model_path
                    dataset.save()

                # Eliminar el archivo temporal
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                enviar_mensaje_pusher('my-channel', uuid, f'El dataset {datasetname} fue entrenado exitosamente.', 100)

                return Response({'mensaje': 'Dataset entrenado exitosamente', 'creacion': dataset.id}, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({'mensaje': 'Ya existe un dataset con este nombre'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return Response({'mensaje': f'Error procesando el dataset: {str(e)}'}, status=status.HTTP_201_CREATED)
    
    
class ClassificationViewSet(viewsets.ModelViewSet):
    queryset = ClassificationResult.objects.all()
    serializer_class = ClassificationResultSerializer

    @action(detail=False, methods=['post'])
    def classify_image(self, request):
        image = request.FILES.get('image')
        dataset_id = request.data.get('dataset_id')

        if not image or not dataset_id:
            return Response({'mensaje': 'Requiere dataset seleccionado'}, status=status.HTTP_201_CREATED)

        try:
            dataset = Dataset.objects.get(id=dataset_id)
        except Dataset.DoesNotExist:
            return Response({'mensaje': 'Dataset no encontrado'}, status=status.HTTP_201_CREATED)

        if not dataset.best_model_path:
            return Response({'mensaje': 'El modelo del dataset fue eliminado'}, status=status.HTTP_201_CREATED)

        # cargamos mejor modelo
        best_model = joblib.load(dataset.best_model_path)

        # Procesamos imagen
        X = preprocess_single_image(image)

        if X is None:
            return Response({'mensaje': 'Error al procesar la imagen'}, status=status.HTTP_201_CREATED)

        # Clasifciamos imagen
        prediction = best_model.predict(X)[0]
        confidence = best_model.predict_proba(X)[0].max()
        
        try:
            predicted_class = DatasetClass.objects.get(dataset=dataset, name=prediction)
        except DatasetClass.DoesNotExist:
            return Response({'mensaje': 'La prediccion no tiene clases registradas vuelve a entrenar otro dataset'}, status=status.HTTP_201_CREATED)

        classification = ClassificationResult.objects.create(
            dataset=dataset,
            image=image,
            predicted_class=predicted_class,
            confidence=confidence
        )

        return Response({
            'predicted_class': predicted_class.name,
            'confidence': confidence
        }, status=status.HTTP_200_OK)

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
            training_results = TrainingResult.objects.filter(dataset=dataset)

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