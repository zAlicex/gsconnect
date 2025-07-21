from django.shortcuts import render
from .models import Curso, Modulo, ProgressoModulo
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from core.models import PerfilUsuario, EmpresaEquipamento, ConteudoEquipamento, ProgressoConteudoEquipamento
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

def lista_cursos(request):
    cursos = Curso.objects.all()
    all_modulos = Modulo.objects.all().order_by('ordem')
    return render(request, 'cursos/lista_cursos.html', {'cursos': cursos, 'all_modulos': all_modulos})

from django.shortcuts import get_object_or_404

def ver_modulo(request, modulo_id):
    modulo = get_object_or_404(Modulo, id=modulo_id)
    # Se for admin, libera acesso a qualquer módulo
    if request.user.is_authenticated and request.user.is_staff:
        context = {'modulo': modulo}
        if 'equipamento' in modulo.titulo.lower():
            perfil = PerfilUsuario.objects.get(user=request.user)
            modelos = perfil.modelos_equipamento.all()
            conteudos = ConteudoEquipamento.objects.filter(modelo__in=modelos)
            context['conteudos_equipamentos'] = conteudos
            # Adiciona tempos assistidos de cada vídeo
            tempos_assistidos = {
                str(conteudo.modelo.id): ProgressoConteudoEquipamento.objects.filter(
                    usuario=request.user, conteudo=conteudo
                ).first().tempo_assistido if ProgressoConteudoEquipamento.objects.filter(
                    usuario=request.user, conteudo=conteudo
                ).exists() else 0
                for conteudo in conteudos
            }
            context['tempos_assistidos'] = tempos_assistidos
        # Adiciona tempo_assistido para admin também
        progresso = ProgressoModulo.objects.filter(usuario=request.user, modulo=modulo).first()
        tempo_assistido = progresso.tempo_assistido if progresso else 0
        context['tempo_assistido'] = tempo_assistido
        return render(request, 'cursos/modulo.html', context)
    if modulo.ordem > 1 and request.user.is_authenticated:
        anterior = Modulo.objects.filter(curso=modulo.curso, ordem=modulo.ordem-1).first()
        if anterior:
            progresso = ProgressoModulo.objects.filter(usuario=request.user, modulo=anterior).first()
            if not progresso or progresso.tempo_assistido < 60:
                return HttpResponseForbidden('Você precisa assistir pelo menos 1 minuto do módulo anterior para acessar este módulo.')
    context = {'modulo': modulo}
    if 'equipamento' in modulo.titulo.lower() and request.user.is_authenticated:
        perfil = PerfilUsuario.objects.get(user=request.user)
        modelos = perfil.modelos_equipamento.all()
        conteudos = ConteudoEquipamento.objects.filter(modelo__in=modelos)
        context['conteudos_equipamentos'] = conteudos
        # Adiciona tempos assistidos de cada vídeo
        tempos_assistidos = {
            str(conteudo.modelo.id): ProgressoConteudoEquipamento.objects.filter(
                usuario=request.user, conteudo=conteudo
            ).first().tempo_assistido if ProgressoConteudoEquipamento.objects.filter(
                usuario=request.user, conteudo=conteudo
            ).exists() else 0
            for conteudo in conteudos
        }
        context['tempos_assistidos'] = tempos_assistidos
    # Adiciona tempo_assistido para usuários comuns
    progresso = ProgressoModulo.objects.filter(usuario=request.user, modulo=modulo).first()
    tempo_assistido = progresso.tempo_assistido if progresso else 0
    context['tempo_assistido'] = tempo_assistido
    return render(request, 'cursos/modulo.html', context)

# Nova view para exibir todos os módulos em cards

def todos_modulos(request):
    if request.user.is_authenticated:
        try:
            perfil = PerfilUsuario.objects.get(user=request.user)
            equipamentos_permitidos = perfil.equipamentos.all()
            modulos = Modulo.objects.filter(equipamento__in=equipamentos_permitidos).order_by('ordem')
        except PerfilUsuario.DoesNotExist:
            modulos = Modulo.objects.none()
    else:
        modulos = Modulo.objects.none()
    modulos_liberados = set()
    modulos_concluidos = set()
    modulos_em_andamento = set()
    if request.user.is_authenticated:
        # Se for admin, libera todos os módulos
        if request.user.is_staff:
            modulos_liberados = set(modulo.id for modulo in modulos)
            modulos_concluidos = set()
            modulos_em_andamento = set()
        else:
            progresso = {p.modulo_id: p for p in ProgressoModulo.objects.filter(usuario=request.user)}
            for modulo in modulos:
                prog = progresso.get(modulo.id)
                if prog and prog.concluido:
                    modulos_concluidos.add(modulo.id)
                elif prog and prog.tempo_assistido > 0:
                    modulos_em_andamento.add(modulo.id)
                if modulo.ordem == 1:
                    modulos_liberados.add(modulo.id)
                else:
                    anterior = Modulo.objects.filter(curso=modulo.curso, ordem=modulo.ordem-1).first()
                    # Lógica especial para o módulo de equipamentos
                    if anterior and 'equipamento' in anterior.titulo.lower():
                        perfil = PerfilUsuario.objects.get(user=request.user)
                        modelos_usuario = set(perfil.modelos_equipamento.values_list('id', flat=True))
                        # Buscar todos os modelos cadastrados
                        from core.models import ModeloEquipamento
                        todos_modelos = set(ModeloEquipamento.objects.all().values_list('id', flat=True))
                        if modelos_usuario == todos_modelos:
                            # Se o usuário tem todos os modelos, basta assistir 2 min do primeiro vídeo de modelo
                            if progresso.get(anterior.id) and progresso[anterior.id].tempo_assistido >= 60:
                                modulos_liberados.add(modulo.id)
                        else:
                            # Regra padrão: precisa assistir 2 min do módulo anterior
                            if progresso.get(anterior.id) and progresso[anterior.id].tempo_assistido >= 60:
                                modulos_liberados.add(modulo.id)
                    else:
                        if anterior and progresso.get(anterior.id) and progresso[anterior.id].tempo_assistido >= 60:
                            modulos_liberados.add(modulo.id)
                        elif modulo.id in progresso and progresso[modulo.id].tempo_assistido > 0:
                            modulos_liberados.add(modulo.id)
    return render(request, 'cursos/todos_modulos.html', {
        'modulos': modulos,
        'modulos_liberados': modulos_liberados,
        'modulos_concluidos': modulos_concluidos,
        'modulos_em_andamento': modulos_em_andamento,
    })

@csrf_exempt
@login_required
def registrar_progresso(request, modulo_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tempo_assistido = int(data.get('tempo_assistido', 0))
        except Exception:
            return JsonResponse({'status': 'erro', 'msg': 'Dados inválidos'}, status=400)
        modulo = Modulo.objects.get(id=modulo_id)
        progresso, _ = ProgressoModulo.objects.get_or_create(usuario=request.user, modulo=modulo)
        if tempo_assistido > progresso.tempo_assistido:
            progresso.tempo_assistido = tempo_assistido
            if tempo_assistido >= 60:
                progresso.concluido = True
            progresso.save()
        return JsonResponse({'status': 'ok', 'tempo_assistido': progresso.tempo_assistido, 'concluido': progresso.concluido})
    return JsonResponse({'status': 'erro', 'msg': 'Método não permitido'}, status=405)

@csrf_exempt
@login_required
def registrar_progresso_modelo(request, modulo_id, modelo_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tempo_assistido = int(data.get('tempo_assistido', 0))
        except Exception:
            return JsonResponse({'status': 'erro', 'msg': 'Dados inválidos'}, status=400)
        # Atualiza o progresso do vídeo de equipamento individual
        conteudo = ConteudoEquipamento.objects.get(modelo_id=modelo_id)
        progresso, _ = ProgressoConteudoEquipamento.objects.get_or_create(usuario=request.user, conteudo=conteudo)
        if tempo_assistido > progresso.tempo_assistido:
            progresso.tempo_assistido = tempo_assistido
            progresso.save()
        return JsonResponse({'status': 'ok', 'tempo_assistido': progresso.tempo_assistido})
    return JsonResponse({'status': 'erro', 'msg': 'Método não permitido'}, status=405)

@require_POST
@login_required
def editar_modulo(request, modulo_id):
    if not request.user.is_staff:
        return HttpResponseForbidden('Apenas administradores podem editar módulos.')
    modulo = get_object_or_404(Modulo, id=modulo_id)
    novo_titulo = request.POST.get('titulo')
    novo_conteudo = request.POST.get('conteudo')
    novos_beneficios = request.POST.get('beneficios')
    alterado = False
    if novo_titulo is not None:
        modulo.titulo = novo_titulo
        alterado = True
    if novo_conteudo is not None:
        modulo.conteudo = novo_conteudo
        alterado = True
    if novos_beneficios is not None:
        modulo.beneficios = novos_beneficios
        alterado = True
    if alterado:
        modulo.save()
    return redirect('cursos:todos_modulos')
