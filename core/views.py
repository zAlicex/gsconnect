from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from cursos.models import Modulo, ProgressoModulo
from .models import PerfilUsuario, ModeloEquipamento, ConteudoEquipamento
from .forms import CustomAuthenticationForm

# Função auxiliar para adicionar módulos ao contexto

def get_modulos_nav():
    return Modulo.objects.all().order_by('ordem')

# Página inicial protegida por login
@login_required
def home(request):
    context = {'modulos_nav': get_modulos_nav()}
    return render(request, 'core/home.html', context)

# View de login
class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    authentication_form = CustomAuthenticationForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modulos_nav'] = get_modulos_nav()
        return context
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.user.is_authenticated:
            from .models import PerfilUsuario
            perfil, _ = PerfilUsuario.objects.get_or_create(user=self.request.user)
            if not self.request.session.session_key:
                self.request.session.save()
            perfil.sessao_ativa = self.request.session.session_key
            perfil.save()
        return response

# View de logout
class CustomLogoutView(LogoutView):
    next_page = '/login/'

# View de registro/cadastro
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # faz login automático após cadastro
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'core/register.html', {'form': form, 'modulos_nav': get_modulos_nav()})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def equipamentos_usuario(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    modelos = perfil.modelos_equipamento.all()
    conteudos = ConteudoEquipamento.objects.filter(modelo__in=modelos)
    return render(request, 'core/equipamentos_usuario.html', {'conteudos': conteudos})

# View de perfil do usuário
@login_required
def perfil_usuario(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    empresa = perfil.empresa
    nome = request.user.get_full_name() or request.user.username
    modulos_concluidos = ProgressoModulo.objects.filter(usuario=request.user, concluido=True).select_related('modulo')
    return render(request, 'core/perfil_usuario.html', {
        'perfil': perfil,
        'empresa': empresa,
        'nome': nome,
        'modulos_concluidos': modulos_concluidos,
    })
