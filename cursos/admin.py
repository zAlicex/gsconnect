from django.contrib import admin
from .models import Curso, Modulo

class ModuloInline(admin.StackedInline):
    model = Modulo
    extra = 1
    fields = ['equipamento', 'titulo', 'conteudo', 'ordem', 'video', 'imagem_capa']  # Adiciona imagem_capa

class CursoAdmin(admin.ModelAdmin):
    inlines = [ModuloInline]
    list_display = ['titulo', 'criado_em']

admin.site.register(Curso, CursoAdmin)
