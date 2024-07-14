
from django.contrib import admin
from .models import Dataset, DatasetClass, TrainingResult, ClassificationResult

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(DatasetClass)
class DatasetClassAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'name', 'index')
    search_fields = ('dataset__name', 'name',)

@admin.register(TrainingResult)
class TrainingResultAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'algorithm', 'accuracy', 'precision', 'recall', 'f1_score', 'auc', 'created_at', 'is_active',)
    list_filter = ('algorithm', 'created_at', 'is_active')
    search_fields = ('dataset__name', 'algorithm')

@admin.register(ClassificationResult)
class ClassificationResultAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'predicted_class', 'confidence', 'created_at', 'is_active')
    list_filter = ('dataset', 'predicted_class', 'is_active', 'created_at')
    search_fields = ('dataset__name', 'predicted_class')
