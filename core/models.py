from django.db import models

class DatasetSession(models.Model):
    session_key = models.CharField(max_length=100, unique=True)
    original_file = models.CharField(max_length=255)
    upload_time = models.DateTimeField(auto_now_add=True)
    
    # Parámetros de división
    test_size = models.FloatField(default=0.4)
    val_size = models.FloatField(default=0.5)
    random_state = models.IntegerField(default=42)
    stratify_column = models.CharField(max_length=100, blank=True, null=True)
    shuffle = models.BooleanField(default=True)
    
    # Estadísticas
    original_rows = models.IntegerField()
    original_columns = models.IntegerField()
    train_rows = models.IntegerField()
    val_rows = models.IntegerField()
    test_rows = models.IntegerField()