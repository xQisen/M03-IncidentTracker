from django.db import models

# Create your models here.
class SecurityIncident(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20)
    detected_at = models.DateTimeField()
    
    def __str__(self):
        return self.title
