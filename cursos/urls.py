from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_cursos, name='lista_cursos'),
    path('modulo/<int:modulo_id>/', views.ver_modulo, name='ver_modulo'),
    path('modulos/', views.todos_modulos, name='todos_modulos'),
    path('modulo/<int:modulo_id>/registrar_progresso/', views.registrar_progresso, name='registrar_progresso'),
    path('modulo/<int:modulo_id>/modelo/<int:modelo_id>/registrar_progresso/', views.registrar_progresso_modelo, name='registrar_progresso_modelo'),
    path('modulo/<int:modulo_id>/editar/', views.editar_modulo, name='editar_modulo'),
]
