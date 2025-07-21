from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import render_to_string
import io
from .models import CertificadoEmitido
from cursos.models import ProgressoModulo, Modulo
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from core.models import PerfilUsuario, Equipamento, Empresa, ModeloEquipamento
import random

def gerar_numero_certificado():
    ano = timezone.now().year
    for _ in range(20):
        numero = f"{ano}-{random.randint(1000, 9999)}"
        if not CertificadoEmitido.objects.filter(numero_certificado=numero).exists():
            return numero
    raise Exception('Não foi possível gerar um número de certificado único.')

@login_required
def certificado_form(request):
    certificado = CertificadoEmitido.objects.filter(usuario=request.user).first()
    if certificado:
        perfil = PerfilUsuario.objects.get(user=request.user)
        empresa_nome = perfil.empresa.nome if perfil.empresa else "-"
        contexto = {
            'certificado_ja_emitido': True,
            'data_conclusao': certificado.data_conclusao,
            'nome_completo': certificado.nome_completo,
            'empresa_nome': empresa_nome,
            'treinamento': 'Treinamento de Equipamento e Plataforma - Grupo Golden Sat',
        }
        return render(request, 'certificados/certificado.html', contexto)

    # Buscar apenas os módulos que o usuário tem acesso (pelos equipamentos do perfil)
    try:
        perfil = PerfilUsuario.objects.get(user=request.user)
        equipamentos_permitidos = perfil.equipamentos.all()
        modulos_usuario = Modulo.objects.filter(equipamento__in=equipamentos_permitidos).order_by('ordem')
        empresa_nome = perfil.empresa.nome if perfil.empresa else "-"
    except PerfilUsuario.DoesNotExist:
        modulos_usuario = Modulo.objects.none()
        empresa_nome = "-"
    total_modulos = modulos_usuario.count()
    concluidos = ProgressoModulo.objects.filter(usuario=request.user, modulo__in=modulos_usuario, concluido=True)
    concluidos_count = concluidos.count()

    pode_gerar = (concluidos_count == total_modulos and total_modulos > 0)

    if request.method == 'POST':
        if not pode_gerar:
            messages.error(request, 'Você precisa concluir todos os módulos para emitir o certificado.')
            return redirect('certificado_form')
        nome_completo = request.POST.get('nome_completo')
        # Data de conclusão = data do último módulo concluído
        ultimo = concluidos.order_by('-atualizado_em').first()
        data_conclusao = ultimo.atualizado_em if ultimo else timezone.now()
        numero_certificado = gerar_numero_certificado()
        certificado = CertificadoEmitido.objects.create(
            usuario=request.user,
            nome_completo=nome_completo,
            data_conclusao=data_conclusao,
            numero_certificado=numero_certificado
        )
        contexto = {
            'certificado_ja_emitido': True,
            'data_conclusao': certificado.data_conclusao,
            'nome_completo': certificado.nome_completo,
            'empresa_nome': empresa_nome,
            'treinamento': 'Treinamento de Equipamento e Plataforma - Grupo Golden Sat',
        }
        return render(request, 'certificados/certificado.html', contexto)

    return render(request, 'certificados/certificado_form.html', {'pode_gerar': pode_gerar})

@login_required
def certificado_pdf(request):
    if request.method == 'POST':
        nome_completo = request.POST.get('nome_completo')
        data_conclusao = timezone.now().strftime('%d/%m/%Y')
        contexto = {
            'nome_completo': nome_completo,
            'data_conclusao': data_conclusao,
            'treinamento': 'Treinamento de Equipamento e Plataforma - Grupo Golden Sat',
        }
        html = render_to_string('certificados/certificado.html', contexto)
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode('utf-8')), result, encoding='utf-8')
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="certificado.pdf"'
            return response
        return HttpResponse('Erro ao gerar PDF', status=500)
    return HttpResponse('Método não permitido', status=405)

@user_passes_test(lambda u: u.is_staff)
def usuarios(request):
    q = request.GET.get('q', '').strip()
    usuarios = User.objects.all()
    if q:
        from django.db.models import Q
        usuarios = usuarios.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(email__icontains=q)
        )
    perfis = {p.user_id: p for p in PerfilUsuario.objects.select_related('empresa').prefetch_related('equipamentos').all()}
    equipamentos = Equipamento.objects.all()
    empresas = Empresa.objects.all()
    modelos_equipamento = ModeloEquipamento.objects.all()
    if request.method == 'POST':
        acao = request.POST.get('acao')
        if acao == 'criar':
            username = request.POST.get('username')
            nome = request.POST.get('nome')
            email = request.POST.get('email')
            senha = request.POST.get('senha')
            is_staff = request.POST.get('is_staff') == '1'
            empresa_id = request.POST.get('empresa_id')
            equipamentos_ids = request.POST.getlist('equipamentos[]')
            modelos_ids = request.POST.getlist('modelos_equipamento[]')
            user = User.objects.create(
                username=username,
                first_name=nome,
                email=email,
                password=make_password(senha),
                is_staff=is_staff
            )
            perfil = PerfilUsuario.objects.create(user=user, empresa_id=empresa_id)
            perfil.equipamentos.set(equipamentos_ids)
            perfil.modelos_equipamento.set(modelos_ids)
            return redirect('usuarios')
        elif acao == 'editar':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            user.username = request.POST.get('username')
            user.first_name = request.POST.get('nome')
            user.email = request.POST.get('email')
            user.is_staff = request.POST.get('is_staff') == '1'
            user.save()
            perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
            empresa_id = request.POST.get('empresa_id')
            if empresa_id:
                empresa_obj = Empresa.objects.get(id=int(empresa_id))
                perfil.empresa = empresa_obj
            equipamentos_ids = request.POST.getlist('equipamentos[]')
            modelos_ids = request.POST.getlist('modelos_equipamento[]')
            perfil.equipamentos.set(equipamentos_ids)
            perfil.modelos_equipamento.set(modelos_ids)
            perfil.save()
            perfil.refresh_from_db()
            return redirect('usuarios')
        elif acao == 'excluir':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            user.delete()
            return redirect('usuarios')
        elif acao == 'resetar_senha':
            user_id = request.POST.get('user_id')
            nova_senha = request.POST.get('nova_senha')
            user = get_object_or_404(User, id=user_id)
            user.set_password(nova_senha)
            user.save()
            return redirect('usuarios')
    perfis = {p.user_id: p for p in PerfilUsuario.objects.select_related('empresa').prefetch_related('equipamentos').all()}
    equipamentos = Equipamento.objects.all()
    empresas = Empresa.objects.all()
    equipamentos_usuario = {p.user_id: list(p.equipamentos.values_list('id', flat=True)) for p in perfis.values()}
    empresa_usuario = {p.user_id: p.empresa_id for p in perfis.values()}
    return render(request, 'certificados/usuarios.html', {
        'usuarios': usuarios,
        'perfis': perfis,
        'equipamentos': equipamentos,
        'empresas': empresas,
        'equipamentos_usuario': equipamentos_usuario,
        'empresa_usuario': empresa_usuario,
        'modelos_equipamento': modelos_equipamento,
    })

@user_passes_test(lambda u: u.is_staff)
def dashboard_usuarios(request):
    from core.models import PerfilUsuario
    from django.utils.timezone import localtime
    from cursos.models import Modulo
    q = request.GET.get('q', '').strip()
    usuarios = User.objects.filter(is_active=True)
    if q:
        from django.db.models import Q
        usuarios = usuarios.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(email__icontains=q)
        )
    dados_usuarios = []
    usuarios_sem_progresso = 0
    for usuario in usuarios:
        try:
            perfil = PerfilUsuario.objects.get(user=usuario)
            equipamentos_permitidos = perfil.equipamentos.all()
            modulos_permitidos = Modulo.objects.filter(equipamento__in=equipamentos_permitidos).order_by('ordem')
        except PerfilUsuario.DoesNotExist:
            modulos_permitidos = Modulo.objects.none()
        total_modulos = modulos_permitidos.count()
        progresso_qs = ProgressoModulo.objects.filter(usuario=usuario, modulo__in=modulos_permitidos)
        concluidos = progresso_qs.filter(concluido=True)
        concluidos_count = concluidos.count()
        percentual = (concluidos_count / total_modulos) * 100 if total_modulos else 0
        certificado = CertificadoEmitido.objects.filter(usuario=usuario).first()
        data_conclusao = localtime(certificado.data_conclusao) if certificado and certificado.data_conclusao else None
        data_inicio = progresso_qs.order_by('atualizado_em').first().atualizado_em if progresso_qs.exists() else None
        data_ultimo = progresso_qs.order_by('-atualizado_em').first().atualizado_em if progresso_qs.exists() else None
        modulos_concluidos = list(concluidos.values_list('modulo__titulo', flat=True))
        modulos_pendentes = list(modulos_permitidos.exclude(id__in=concluidos.values_list('modulo_id', flat=True)).values_list('titulo', flat=True))
        dados_usuarios.append({
            'usuario': usuario,
            'percentual': percentual,
            'concluidos': concluidos_count,
            'total_modulos': total_modulos,
            'data_conclusao': data_conclusao,
            'data_inicio': data_inicio,
            'data_ultimo': data_ultimo,
            'modulos_concluidos': modulos_concluidos,
            'modulos_pendentes': modulos_pendentes,
        })
        if total_modulos > 0 and concluidos_count == 0:
            usuarios_sem_progresso += 1
    total_modulos = Modulo.objects.count()
    if dados_usuarios:
        taxa_conclusao = sum(u['percentual'] for u in dados_usuarios) / len(dados_usuarios)
    else:
        taxa_conclusao = 0
    context = {
        'total_usuarios': usuarios.count(),
        'dados_usuarios': dados_usuarios,
        'total_modulos': total_modulos,
        'taxa_conclusao': round(taxa_conclusao, 2),
        'usuarios_sem_progresso': usuarios_sem_progresso,
    }
    return render(request, 'certificados/dashboard_usuarios.html', context)
