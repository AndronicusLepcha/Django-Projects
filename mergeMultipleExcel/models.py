from django.db import models

class UploadedFile(models.Model):
    name=models.CharField(max_length=20)
    file = models.FileField(upload_to='uploads/')