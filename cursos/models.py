from django.db import models
from django.contrib.auth.models import User
from core.models import Equipamento

class Curso(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class Modulo(models.Model):
    curso = models.ForeignKey(Curso, related_name='modulos', on_delete=models.CASCADE)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    ordem = models.PositiveIntegerField()
    video = models.FileField(upload_to='videos/', null=True, blank=True)  # ✅ aqui
    imagem_capa = models.ImageField(upload_to='capas_modulos/', null=True, blank=True)  # NOVO CAMPO
    beneficios = models.TextField(blank=True, default='')  # Um benefício por linha

    def __str__(self):
        return f'{self.ordem}. {self.titulo} ({self.curso.titulo})'

class ProgressoModulo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE)
    tempo_assistido = models.PositiveIntegerField(default=0)  # em segundos
    concluido = models.BooleanField(default=False)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('usuario', 'modulo')

    def __str__(self):
        return f"{self.usuario} - {self.modulo} ({self.tempo_assistido}s)"
