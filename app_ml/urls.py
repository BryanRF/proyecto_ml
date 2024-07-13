from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .controller import DatasetViewSet, ClassificationViewSet
from . import controller

router = DefaultRouter()
router.register(r'datasets', DatasetViewSet)
router.register(r'classifications', ClassificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('train_dataset/', DatasetViewSet.as_view({'post': 'train_dataset'}), name='train_dataset'),
    path('classify_image/', ClassificationViewSet.as_view({'post': 'classify_image'}), name='classify_image'),
    path('generate_report/', ClassificationViewSet.as_view({'get': 'generate_report'}), name='generate_report'),
]
