# app_ml/serializers.py

from rest_framework import serializers
from .models import Dataset, TrainingResult, ClassificationResult

class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = '__all__'

class TrainingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingResult
        fields = '__all__'

class ClassificationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassificationResult
        fields = '__all__'

# app_ml/views.py

import zipfile
import os
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Dataset, TrainingResult, ClassificationResult
from .serializers import DatasetSerializer, TrainingResultSerializer, ClassificationResultSerializer
from .ml_algorithms import train_and_evaluate, classify_image

class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

    @action(detail=False, methods=['post'])
    def upload_dataset(self, request):
        zip_file = request.FILES.get('file')
        if not zip_file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        dataset_name = os.path.splitext(zip_file.name)[0]
        dataset = Dataset.objects.create(name=dataset_name, file=zip_file)

        # Extraer el archivo ZIP
        with zipfile.ZipFile(dataset.file.path, 'r') as zip_ref:
            extract_path = os.path.join(settings.MEDIA_ROOT, 'media', dataset_name)
            zip_ref.extractall(extract_path)

        # Entrenar los modelos
        results = train_and_evaluate(extract_path)

        # Guardar los resultados
        for algorithm, metrics in results.items():
            TrainingResult.objects.create(
                dataset=dataset,
                algorithm=algorithm,
                accuracy=metrics['accuracy'],
                precision=metrics['precision'],
                recall=metrics['recall'],
                f1_score=metrics['f1_score'],
                auc=metrics['auc'],
                cpu_usage=metrics['cpu_usage'],
                execution_time=metrics['execution_time']
            )

        return Response({'message': 'Dataset uploaded and processed successfully'}, status=status.HTTP_201_CREATED)

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
            dataset = Dataset.objects.get(id=dataset_id, is_active=True)
        except Dataset.DoesNotExist:
            return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)

        result = classify_image(image, dataset)
        classification = ClassificationResult.objects.create(
            dataset=dataset,
            image=image,
            predicted_class=result['class'],
            confidence=result['confidence']
        )

        serializer = self.get_serializer(classification)
        return Response(serializer.data, status=status.HTTP_201_CREATED)