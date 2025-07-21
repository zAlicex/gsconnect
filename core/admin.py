from django.contrib import admin
from .models import PerfilUsuario, Empresa, Equipamento, ModeloEquipamento, ConteudoEquipamento

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('nome',)

@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'descricao')
    search_fields = ('nome',)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'empresa')
    list_filter = ('empresa',)
    search_fields = ('user__username', 'empresa__nome')

admin.site.register(ModeloEquipamento)
admin.site.register(ConteudoEquipamento)
