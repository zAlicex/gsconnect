from django.urls import path
from . import views
from .views import CustomLoginView, CustomLogoutView
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.home, name='home'),                # /
    path('home/', views.home, name='home_url'),       # /home/
    path('login/', CustomLoginView.as_view(), name='login'),   # /login/
    path('logout/', views.logout_view, name='logout'), # /logout/
    path('register/', views.register_view, name='register'),    # /register/
    path('meus-equipamentos/', views.equipamentos_usuario, name='meus_equipamentos'),
    path('meu-perfil/', views.perfil_usuario, name='perfil_usuario'),
]

urlpatterns += [
    path('politica-de-privacidade/', TemplateView.as_view(template_name='politica_privacidade.html'), name='politicas'),
]

urlpatterns += [
    path('status-plataforma/', TemplateView.as_view(template_name='status_plataforma.html'), name='status'),
]
