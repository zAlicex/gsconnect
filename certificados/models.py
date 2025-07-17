from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class CertificadoEmitido(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nome_completo = models.CharField(max_length=255)
    data_emissao = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)  # Data real de conclusão dos módulos
    numero_certificado = models.CharField(max_length=20, unique=True, blank=True)

    def __str__(self):
        return f"{self.nome_completo} ({self.data_emissao:%d/%m/%Y})"
