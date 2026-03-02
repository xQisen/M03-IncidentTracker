from django.db import models
from django.contrib.auth.models import User

class SecurityIncident(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20)
    detected_at = models.DateTimeField()
    usuari = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='incidents')
    
    def __str__(self):
        return f"{self.title} - {self.usuari.username if self.usuari else 'Sense usuari'}"
