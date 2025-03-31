from django.db import models

# Create your models here.
class Document(models.Model):
    document = models.FileField(upload_to='docs/')
    sign = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)