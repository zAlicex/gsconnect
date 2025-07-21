from django.shortcuts import redirect
from django.contrib.auth import logout
from core.models import PerfilUsuario

class SessaoExclusivaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                perfil = PerfilUsuario.objects.get(user=request.user)
                if perfil.sessao_ativa and perfil.sessao_ativa != request.session.session_key:
                    logout(request)
                    return redirect('login')
            except PerfilUsuario.DoesNotExist:
                pass
        return self.get_response(request) 