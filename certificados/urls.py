# treinamento/urls.py

from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', include('core.urls')),  # Isso direciona '' (vazio) para as rotas do app core
    path('emitir/', views.certificado_form, name='certificado_form'),
    path('pdf/', views.certificado_pdf, name='certificado_pdf'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('dashboard/', views.dashboard_usuarios, name='dashboard_usuarios'),
]
