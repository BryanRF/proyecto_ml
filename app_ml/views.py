# app_ml/views.py

import os
from django.conf import settings
from rest_framework import viewsets, status
from django.core.files.base import ContentFile
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Dataset, TrainingResult, ClassificationResult
from .serializers import DatasetSerializer, TrainingResultSerializer, ClassificationResultSerializer
from .utils.data_processing import load_and_preprocess_data, preprocess_single_image
from .ml_algorithms.logistic_regression import train_logistic_regression
from .ml_algorithms.neural_network import train_neural_network
from .ml_algorithms.svm import train_svm
from .ml_algorithms.naive_bayes import train_naive_bayes
from .ml_algorithms.decision_tree import train_decision_tree
from .utils.report_generation import generate_report, generate_comparison_report
import zipfile
import joblib
from django.core.files.storage import default_storage
from pusher import Pusher

class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    
    
    @action(detail=False, methods=['post'])
    def train_dataset(self, request):
        name = request.data.get('name')
        dataset_file = request.FILES.get('file')
        if not dataset_file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        # Save the uploaded file temporarily
        temp_path = default_storage.save('temp_dataset.zip', ContentFile(dataset_file.read()))

        try:
            # Process the file
            with zipfile.ZipFile(default_storage.path(temp_path), 'r') as zip_file:
                file_list = zip_file.namelist()
                
                # Load and preprocess the data
                X_train, X_test, y_train, y_test, le = load_and_preprocess_data(file_list, zip_file)

            # Create a new dataset entry
            dataset = Dataset.objects.create(name=name, file=dataset_file)

            # Train all models
            algorithms = {
                'Logistic Regression': train_logistic_regression,
                'Neural Network': train_neural_network,
                'SVM': train_svm,
                'Naive Bayes': train_naive_bayes,
                'Decision Tree': train_decision_tree
            }

            results = {}
            best_model = None
            best_accuracy = 0

            for name, train_func in algorithms.items():
                result = train_func(X_train, y_train, X_test, y_test)
                results[name] = result
                
                # Save training result
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
                pusher_client = Pusher(
        app_id='1722267',
        key='be0524da244ba0c38862',
        secret='1af3100d62ea2b6d5c93',
        cluster='sa1',
        ssl=True
    )
                pusher_client.trigger('my-channel', 'file_processed', {'count': 100, 'algorithm': name})

                # Keep track of the best model
                if result['accuracy'] > best_accuracy:
                    best_accuracy = result['accuracy']
                    best_model = result['model']

            # Save the best model
            if best_model:
                model_path = f'best_model_{dataset.id}.joblib'
                joblib.dump(best_model, model_path)
                dataset.best_model_path = model_path
                dataset.save()

        except Exception as e:
            default_storage.delete(temp_path)
            return Response({'error': f'Error processing dataset: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            # Clean up the temporary file
            default_storage.delete(temp_path)

        return Response({
            'message': 'Dataset trained successfully',
            'dataset_id': dataset.id,
            'results': results
        }, status=status.HTTP_201_CREATED)
class ClassificationViewSet(viewsets.ModelViewSet):
    queryset = ClassificationResult.objects.all()
    serializer_class = ClassificationResultSerializer

    @action(detail=False, methods=['post'])
    def classify_image(self, request):
        image = request.FILES.get('image')
        dataset_id = request.data.get('dataset_id')

        if not image or not dataset_id:
            return Response({'error': 'Image and dataset_id are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dataset = Dataset.objects.get(id=dataset_id)
        except Dataset.DoesNotExist:
            return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)

        if not dataset.best_model_path:
            return Response({'error': 'No trained model available for this dataset'}, status=status.HTTP_400_BAD_REQUEST)

        # Load the best model
        best_model = joblib.load(dataset.best_model_path)

        # Preprocess the image
        X = preprocess_single_image(image)

        if X is None:
            return Response({'error': 'Error processing the image'}, status=status.HTTP_400_BAD_REQUEST)

        # Classify the image
        prediction = best_model.predict(X)[0]
        confidence = best_model.predict_proba(X)[0].max()

        # Save the classification result
        classification = ClassificationResult.objects.create(
            dataset=dataset,
            image=image,
            predicted_class=prediction,
            confidence=confidence
        )

        return Response({
            'predicted_class': prediction,
            'confidence': confidence
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def generate_report(self, request):
        dataset_id = request.query_params.get('dataset_id')

        if not dataset_id:
            return Response({'error': 'dataset_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dataset = Dataset.objects.get(id=dataset_id)
        except Dataset.DoesNotExist:
            return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)

        training_results = TrainingResult.objects.filter(dataset=dataset)

        if not training_results:
            return Response({'error': 'No training results found for this dataset'}, status=status.HTTP_404_NOT_FOUND)

        results = {result.algorithm: {
            'accuracy': result.accuracy,
            'precision': result.precision,
            'recall': result.recall,
            'f1_score': result.f1_score,
            'auc': result.auc,
            'cpu_usage': result.cpu_usage,
            'execution_time': result.execution_time
        } for result in training_results}

        # Generate the report
        report_path = os.path.join(settings.MEDIA_ROOT, 'reports', f'report_{dataset_id}.pdf')
        generate_comparison_report(results, report_path)

        # You might want to serve this file or return its URL
        return Response({'message': 'Report generated successfully', 'report_path': report_path}, status=status.HTTP_200_OK)