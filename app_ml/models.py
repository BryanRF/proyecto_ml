from django.db import models

class Dataset(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Hacemos que el nombre sea único
    file = models.FileField(upload_to='media/', null=True, blank=True, default=None)
    best_model_path = models.FileField(upload_to='media/', null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class DatasetClass(models.Model):
    dataset = models.ForeignKey(Dataset, related_name='classes', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    index = models.IntegerField()

    class Meta:
        unique_together = ('dataset', 'index')

    def __str__(self):
        return f"{self.dataset.name} - {self.name} ({self.index})"
    
class TrainingResult(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
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

class ClassificationResult(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploaded_images/')
    predicted_class = models.ForeignKey(DatasetClass, on_delete=models.CASCADE)
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.dataset.name} - {self.predicted_class}"
