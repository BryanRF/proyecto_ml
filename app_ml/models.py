from django.db import models
from django.core.validators import RegexValidator 
class Dataset(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Hacemos que el nombre sea único
    file = models.FileField(upload_to='media/', null=True, blank=True, default=None)
    best_model_path = models.FileField(upload_to='media/', null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TipoClase(models.Model):
    dataset = models.ForeignKey(Dataset, related_name='tipos_clase', on_delete=models.CASCADE)  # Relación con Dataset
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    color = models.CharField(
        max_length=7,
        validators=[RegexValidator(regex=r'^#[0-9A-Fa-f]{6}$', message="El color debe estar en formato HEX, por ejemplo: #FFFFFF")],
        
        help_text="Color en formato HEX (por ejemplo, #836752)."
        , null=True, blank=True, default=None
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('dataset', 'name')  # Asegura que no haya dos tipos con el mismo nombre dentro de un dataset

    def __str__(self):
        return f"{self.name} ({self.dataset.name})"


class Clase(models.Model):
    dataset = models.ForeignKey(Dataset, related_name='clases', on_delete=models.CASCADE)
    tipo_clase = models.ForeignKey(TipoClase, related_name='clases', on_delete=models.CASCADE,null=True, blank=True)  # Relación con TipoClase
    name = models.CharField(max_length=255)
    index = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    normal = models.BooleanField(default=True)

    class Meta:
        unique_together = ('dataset', 'index')

    def __str__(self):
        return f"{self.dataset.name} - {self.name} ({self.index})"


class Entrenamiento(models.Model):
    dataset = models.ForeignKey(Dataset, related_name='entrenamientos', on_delete=models.CASCADE)
    algorithm = models.CharField(max_length=100)
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    auc = models.FloatField()
    cpu_usage = models.FloatField()
    execution_time = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.dataset.name} - {self.algorithm} - {self.created_at}"


class Prediccion(models.Model):
    dataset = models.ForeignKey(Dataset, related_name='predicciones', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploaded_images/')
    predicted_class = models.ForeignKey(Clase, related_name='predicciones', on_delete=models.CASCADE)
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.dataset.name} - {self.predicted_class.name}"
