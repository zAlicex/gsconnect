from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Empresa(models.Model):
    nome = models.CharField(max_length=200)
    # Adicione outros campos como CNPJ, endereço, etc, se desejar
    def __str__(self):
        return self.nome

class Equipamento(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    def __str__(self):
        return self.nome

class EmpresaEquipamento(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.empresa} - {self.equipamento}"

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    empresa = models.ForeignKey('Empresa', on_delete=models.SET_NULL, null=True, blank=True)
    equipamentos = models.ManyToManyField('Equipamento', blank=True)
    modelos_equipamento = models.ManyToManyField('ModeloEquipamento', blank=True)
    sessao_ativa = models.CharField(max_length=40, blank=True, null=True)  # Para sessão exclusiva
    def __str__(self):
        return f"{self.user} ({self.empresa})"

class ModeloEquipamento(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class ConteudoEquipamento(models.Model):
    modelo = models.ForeignKey('ModeloEquipamento', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return f"{self.modelo} - {self.titulo}"

class ProgressoConteudoEquipamento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    conteudo = models.ForeignKey('core.ConteudoEquipamento', on_delete=models.CASCADE)
    tempo_assistido = models.PositiveIntegerField(default=0)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('usuario', 'conteudo')
