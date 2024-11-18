from django.contrib import admin
from .models import Dataset, Clase, TipoClase, Entrenamiento, Prediccion


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name',)


@admin.register(TipoClase)
class TipoClaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'dataset', 'color', 'created_at')
    list_editable = ('color',)  # Permitir editar directamente el color desde la lista
    search_fields = ('name', 'dataset__name', 'color')


@admin.register(Clase)
class ClaseAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'tipo_clase', 'name', 'index', 'is_active', 'normal')
    list_filter = ('dataset', 'tipo_clase', 'is_active', 'normal')
    search_fields = ('dataset__name', 'tipo_clase__name', 'name')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "tipo_clase":
            if hasattr(request, "_dataset_id"):  # Asegurar que el filtro se aplica
                kwargs["queryset"] = TipoClase.objects.filter(dataset_id=request._dataset_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        # Permitir filtrar tipos de clase según el dataset seleccionado
        if obj:
            request._dataset_id = obj.dataset_id
        return super().get_form(request, obj, **kwargs)


@admin.register(Entrenamiento)
class EntrenamientoAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'algorithm', 'accuracy', 'precision', 'recall', 'f1_score', 'auc', 'created_at', 'is_active')
    list_filter = ('algorithm', 'created_at', 'is_active')
    search_fields = ('dataset__name', 'algorithm')


@admin.register(Prediccion)
class PrediccionAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'predicted_class', 'confidence', 'created_at', 'is_active')
    list_filter = ('dataset', 'predicted_class', 'is_active', 'created_at')
    search_fields = ('dataset__name', 'predicted_class__name')
