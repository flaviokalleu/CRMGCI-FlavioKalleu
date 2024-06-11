import io
import logging
from pathlib import Path
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from PyPDF2 import PdfReader, PdfWriter
from django.core.exceptions import PermissionDenied
import os
from django.template.loader import render_to_string
import zipfile
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from io import BytesIO
from django.http import Http404, HttpResponseServerError
from django.db.models import Q
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.shortcuts import render, redirect

from users.backup.backup import perform_backup
from .forms import AddNoteForm, ClienteForm2, ContratoForm, EditarProcessoForm, ImovelForm, MaterialForm, ProcessoForm, ProprietarioEditForm, UploadBackupForm, UserUpdateForm, VideoForm
from django.core.management import call_command
from .models import Backup, Contrato, Imovel, MaterialDeMarketing, Nota_notification, Tag, Video, VideoView
from django.http import HttpResponse
import os
from decimal import Decimal
from django.core.paginator import Paginator
from django.views.decorators.clickjacking import xframe_options_exempt
from django import template
from .forms import ProprietarioForm
from .forms import DeletarProcessoForm
from .serializers import ClienteSerializer
from django.db import connection
import requests
from .models import Cliente, Corretores, OpcaoProcesso, Processo, Proprietario, CustomUser, TipoProcesso, OpcaoSelecionada
from .forms import OpcoesForm
import shutil
from django.http import HttpResponse
from PyPDF2 import DocumentInformation, PdfReader, PdfWriter
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CorretorForm, ClienteForm, CorrespondenteForm, TransactionForm, DocumentoForm
from django.contrib.auth.models import Group, User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.db.models import Sum
from .models import Cliente, Corretores, Correspondente, Transaction, FixedExpense, Documento
from django.db import models
from datetime import datetime
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import os
from django.views.decorators.http import require_POST
import fitz
from .models import NotaPrivada
from .models import VendaCorretor
from .models import Nota
import re
from django.conf import settings
from django.forms import inlineformset_factory
from PIL import Image
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import os
import base64
import json
from django.core.serializers import serialize
from .consulta import consulta_cpf_func
from django.http import HttpRequest
from .forms import UserSettingsForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
import requests
from django.db.models import F
from django.db.models import Subquery, OuterRef
# Importando o modelo UserAccessLog que você deve ter definido anteriormente
from .models import UserAccessLog
from django.shortcuts import render
from datetime import timedelta
from .models import Proprietario, Contato
from django.utils import timezone
from datetime import date
from django.db.models.functions import ExtractMonth, ExtractYear
from django.core.serializers import serialize
from django.shortcuts import render, redirect
import calendar
from django.db.models import Count
from django.utils.translation import gettext as _
from .models import Nota_notification
from django.shortcuts import render
from PyPDF2 import PdfReader
from django.http import JsonResponse
import io
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Cliente
from users.models import CustomUser
from django.http import HttpResponse
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from django.utils import timezone
from .models import Cliente


def index(request):
    # Recuperar todas as tags
    tags = Tag.objects.all()
    
    if tags.exists():
        # Selecionar aleatoriamente uma tag
        random_tag = random.choice(tags)
        
        # Recuperar os imóveis que possuem a tag selecionada
        imoveis_tag = Imovel.objects.filter(tags=random_tag)
        
        # Recuperar os imóveis novos
        imoveis_novos = Imovel.objects.filter(tipo='NOVO')
        
        # Recuperar os imóveis usados
        imoveis_usados = Imovel.objects.filter(tipo='USADO')
        
        # Recuperar os imóveis ágio
        imoveis_agios = Imovel.objects.filter(tipo='AGIO')
        
        # Passar os imóveis e o nome da tag aleatória para o template usando um contexto
        context = {
            'imoveis_novos': imoveis_novos,
            'imoveis_usados': imoveis_usados,
            'imoveis_agios': imoveis_agios,
            'imoveis_tag': imoveis_tag,
            'tag_name': random_tag.name
        }
    else:
        # Caso não existam tags, passar uma lista vazia de imóveis e uma mensagem de erro
        context = {
            'imoveis_novos': [],
            'imoveis_usados': [],
            'imoveis_agios': [],
            'imoveis_tag': [],
            'tag_name': None,
            'error_message': 'Nenhuma tag disponível.'
        }

    return render(request, 'index.html', context)


@csrf_exempt
def backup_view(request):
    global backup_progress  # Definindo como global

    if request.method == 'POST':
        # Função de retorno de chamada para relatar o progresso em tempo real
        def progress_callback(progress):
            # Atualiza a variável global de progresso
            global backup_progress
            backup_progress = progress

        perform_backup(progress_callback=progress_callback)
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'error': 'Only POST requests are allowed for this endpoint'})
    
def allimoveis(request):
    tipo_imovel = request.GET.get('tipo_imovel')
    localizacao = request.GET.get('localizacao')
    tags = request.GET.getlist('tags')  # getlist para pegar múltiplas tags

    imoveis_list = Imovel.objects.all()

    if tipo_imovel:
        imoveis_list = imoveis_list.filter(tipo=tipo_imovel)
    
    if localizacao:
        imoveis_list = imoveis_list.filter(localizacao=localizacao)

    if tags:
        imoveis_list = imoveis_list.filter(tags__name__in=tags).distinct()

    paginator = Paginator(imoveis_list, 20)  # 20 imóveis por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    all_tags = Tag.objects.all()

    return render(request, 'allimoveis.html', {
        'page_obj': page_obj,
        'all_tags': all_tags
    })



def detalhes_imovel(request, imovel_id):
    imovel = Imovel.objects.get(pk=imovel_id)
    return render(request, 'detalhes_imovel.html', {'imovel': imovel})

def get_client_ip(request: HttpRequest) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_location_from_ip(ip: str) -> str:
    try:
        # Usando um serviço gratuito para pegar a localização pelo IP
        response = requests.get(f'https://ipapi.co/{ip}/json/')
        data = response.json()
        return f"{data.get('city')}, {data.get('region')}, {data.get('country_name')}"
    except Exception as e:
        return 'Unknown location'


def redirect_to_dashboard(request):
    # Substitua pelo caminho adequado para o painel de controle em seu aplicativo
    return HttpResponseRedirect('/admin_dashboard/')


def login_view(request):
    # Se o usuário já estiver autenticado, redirecione para o dashboard
    if request.user.is_authenticated:
        return redirect_to_dashboard(request)

    # Se a solicitação for um POST, processar o formulário de login
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            ip = get_client_ip(request)
            location = get_location_from_ip(ip)
            browser_info = request.headers.get('User-Agent')

            UserAccessLog.objects.create(
                user=user,
                ip_address=ip,
                location=location,
                browser_info=browser_info,
                action='User logged in'
            )
            messages.success(request, 'Bem-vindo de volta! Sua autenticação foi feita com sucesso.')

            return redirect_to_dashboard(request)
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def is_corretor(user):
    return user.groups.filter(name='Corretores').exists()


def is_correspondent(user):
    return user.groups.filter(name='correspondente').exists()


def is_admin(user):
    return user.is_superuser


def redirect_to_dashboard(request):
    if request.user.is_superuser:
        return HttpResponseRedirect(reverse('admin_dashboard'))
    elif request.user.groups.filter(name='Corretores').exists():
        return HttpResponseRedirect(reverse('broker_dashboard'))
    elif request.user.groups.filter(name='correspondente').exists():
        return HttpResponseRedirect(reverse('correspondent_dashboard'))
    else:
        # Se não houver um redirecionamento específico para o tipo de usuário, redirecione para a página inicial
        return redirect_to_dashboard(request)





@user_passes_test(is_correspondent)
@login_required
def correspondent_dashboard(request):
    # Coleta de dados
    fixed_expenses = get_fixed_expenses(request.user)
    dias = [i for i in range(1, 32)]

    despesas = Transaction.objects.filter(tipo='DESPESA').aggregate(
        total=models.Sum('valor'))['total'] or 0
    receitas = Transaction.objects.filter(tipo='RECEITA').aggregate(
        total=models.Sum('valor'))['total'] or 0
    total_receitas = Transaction.objects.filter(
        user=request.user, tipo='RECEITA').aggregate(total=Sum('valor'))['total'] or 0
    total_despesas = Transaction.objects.filter(
        user=request.user, tipo='DESPESA').aggregate(total=Sum('valor'))['total'] or 0
    saldo = receitas - despesas

    # Obter a contagem de vários modelos
    total_corretores = Corretores.objects.count()
    total_clientes = Cliente.objects.count()
    total_correspondentes = Correspondente.objects.count()
    recent_transactions = Transaction.objects.all().order_by('-id')[:8]

    total_proprietarios = Proprietario.objects.count()
    total_contatos = Contato.objects.count()
    contatos_hoje = Contato.objects.filter(
        data_registro=datetime.now().date()).count()
    contatos_7_dias = Contato.objects.filter(
        data_registro__gte=datetime.now() - timedelta(days=7)).count()

    status_counts = Cliente.objects.values(
        'status').annotate(total=Count('status'))
    status_counts_dict = {item['status']: item['total']
                          for item in status_counts}
    all_statuses = [
        {'status': choice[0], 'total': status_counts_dict.get(
            choice[0], 0), 'display': choice[1]}
        for choice in Cliente.STATUS_CHOICES
    ]

    # Converta STATUS_CHOICES em um dicionário para fácil acesso
    status_dict = dict(Cliente.STATUS_CHOICES)

    # Gerar dados mensais
    monthly_counts = Cliente.objects.filter(data_de_criacao__isnull=False).annotate(
        month=ExtractMonth('data_de_criacao'),
        year=ExtractYear('data_de_criacao')
    ).values('month', 'year').annotate(total=Count('id')).order_by('year', 'month')

    # Gerar dados anuais
    annual_counts = Cliente.objects.filter(data_de_criacao__isnull=False).annotate(
        year=ExtractYear('data_de_criacao')
    ).values('year').annotate(total=Count('id')).order_by('year')

    # Converter os QuerySets em JSON
    monthly_data_json = json.dumps(list(monthly_counts))
    annual_data_json = json.dumps(list(annual_counts))

# Mapeia o número do mês para o nome do mês
    months = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }

    # Corrige os rótulos do gráfico
    chart_labels = []
    for entry in monthly_counts:
        month = entry.get('month')
        year = entry.get('year')
        if month and month in months:
            chart_labels.append(f"{months[month]} {year}")
        else:
            chart_labels.append(f"Mês Desconhecido {year if year else ''}")

    chart_data = {
        'labels': chart_labels,
        'data': [entry.get('total', 0) for entry in monthly_counts]
    }

    chart_data_json = json.dumps(chart_data)

    today = datetime.now().day
    expenses_due_soon = [expense for expense in fixed_expenses if 0 < (
        expense.due_day - today) <= 3]

    current_year = datetime.now().year
    last_year = current_year - 1
    current_month = datetime.now().month

    total_current = Cliente.objects.filter(
        data_de_criacao__year=current_year,
        data_de_criacao__month=current_month
    ).count()
    total_last_year = Cliente.objects.filter(
        data_de_criacao__year=last_year,
        data_de_criacao__month=current_month
    ).count()

    try:
        percent_change = (
            (total_current - total_last_year) / total_last_year) * 100
    except ZeroDivisionError:
        percent_change = 0

    vendas_corretores = VendaCorretor.objects.all().order_by('-id')

   # Calcula os top 4 status
    top_statuses_data = Cliente.objects.values('status').annotate(
        total=Count('status')).order_by('-total')[:4]

    top_statuses = [
        {
            'status': item['status'],
            'total': item['total'],
            'display': Cliente(status=item['status']).get_status_display()
        }
        for item in top_statuses_data
    ]

    clientes = Cliente.objects.all()

    processos = Processo.objects.all().order_by('-data_inicio')
    processos_em_andamento = [
        processo for processo in processos if processo.data_finalizacao is None]
    total_processos_em_andamento = len(processos_em_andamento)

    try:
        corretor_group = Group.objects.get(name='Corretores')
        corretores = corretor_group.user_set.all()
    except Group.DoesNotExist:
        corretores = []

    # Calcular o progresso para cada processo
    for processo in processos:
        processo.progresso = calcular_progresso(
            processo, processo.id, processo.cliente)
        if processo.cliente:
            processo.opcoes_selecionadas = OpcaoSelecionada.objects.filter(processo=processo)

    data_referencia = datetime.now() - timedelta(days=7)
    total_clientes_recentes = Cliente.objects.filter(
        data_de_criacao__gte=data_referencia).count()

    context = {
        'total_clientes_recentes': total_clientes_recentes,
        'total_processos_em_andamento': total_processos_em_andamento,
        'current_year': current_year,
        'current_month': current_month,
        'percent_change': int(percent_change),
        'monthly_data_json': monthly_data_json,
        'annual_data_json': annual_data_json,
        'chart_data_json': chart_data_json,
        'chart_data': chart_data,
        'expenses_due_soon': expenses_due_soon,
        'total_proprietarios': total_proprietarios,
        'total_contatos': total_contatos,
        'contatos_hoje': contatos_hoje,
        'contatos_7_dias': contatos_7_dias,
        'recent_transactions': recent_transactions,
        'total_corretores': total_corretores,
        'total_clientes': total_clientes,
        'total_correspondentes': total_correspondentes,
        'saldo': saldo,
        'despesas': despesas,
        'receitas': receitas,
        'fixed_expenses': fixed_expenses,
        'dias': dias,
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'notas_privadas': NotaPrivada.objects.filter(user=request.user).order_by('-data'),
        'all_statuses': all_statuses,
        'username': request.user.username,
        'vendas_corretores': vendas_corretores,
        'top_statuses': top_statuses,
        'status_choices': dict(Cliente.STATUS_CHOICES),
        'clientes': clientes,
        'processos': processos,
    }

    return render(request, 'correspondent_dashboard.html', context)


@login_required
def adicionar_nota_cliente(request):
    
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        texto_nota = request.POST.get('texto')

        if not texto_nota:
            return JsonResponse({'status': 'error', 'message': 'O texto da nota é obrigatório.'}, status=400)

        cliente = get_object_or_404(Cliente, pk=cliente_id)
        Nota.objects.create(cliente=cliente, texto=texto_nota, criado_por=request.user)
        return JsonResponse({'status': 'success', 'message': 'Nota adicionada com sucesso.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método inválido.'}, status=405)


def carregar_notas_cliente(request, cliente_id):
    notas = Nota.objects.filter(cliente_id=cliente_id)
    notas_json = serialize('json', notas)
    return JsonResponse(notas_json, safe=False)


@require_POST
def deletar_nota_cliente(request, nota_id):
    nota = get_object_or_404(Nota, pk=nota_id)
    nota.delete()
    return JsonResponse({'status': 'success', 'message': 'Nota deletada com sucesso.'})

#lista de cliente
def lista_de_clientes(request):
    if is_corretor(request.user):
        todos_clientes = Cliente.objects.filter(corretor=request.user)
    elif is_admin(request.user) or is_correspondent(request.user):
        todos_clientes = Cliente.objects.all()
    else:
        raise Http404("Você não tem permissão para acessar esta página.")

    status_filter = request.GET.get('status')
    if status_filter:
        todos_clientes = todos_clientes.filter(status=status_filter)

    corretor_filter = request.GET.get('corretor')
    if corretor_filter:
        todos_clientes = todos_clientes.filter(corretor__pk=corretor_filter)

    data_inicio_filter = request.GET.get('data_inicio')
    data_fim_filter = request.GET.get('data_fim')

    if data_inicio_filter and data_fim_filter:
        try:
            data_inicio_filter = datetime.strptime(data_inicio_filter, '%Y-%m-%d')
            data_fim_filter = datetime.strptime(data_fim_filter, '%Y-%m-%d')

            todos_clientes = todos_clientes.filter(
                data_de_criacao__date__range=(data_inicio_filter, data_fim_filter)
            )
        except ValueError:
            pass

    # Filtrando clientes com status 'aguardando_aprovacao' e 'aguardando_cancelamento_qv'
    clientes_aguardando = todos_clientes.filter(Q(status='aguardando_aprovacao') | Q(status='aguardando_cancelamento_qv'))

    # Filtrando outros clientes
    clientes_outros = todos_clientes.exclude(Q(status='aguardando_aprovacao') | Q(status='aguardando_cancelamento_qv'))

    # Concatenando as listas para garantir que os clientes com status 'aguardando_aprovacao' e 'aguardando_cancelamento_qv' apareçam primeiro
    todos_clientes = list(clientes_aguardando) + list(clientes_outros)

    # Convertendo todos_clientes de volta para uma queryset para poder filtrar novamente
    todos_clientes = Cliente.objects.filter(id__in=[cliente.id for cliente in todos_clientes])

    # Filtrando por mês e contando os clientes
    meses = []
    for i in range(1, 13):
        nome_mes = _(calendar.month_name[i])
        qtd_clientes = todos_clientes.filter(data_de_criacao__month=i).count()
        meses.append({'nome_mes': nome_mes, 'qtd_clientes': qtd_clientes})

    # Obtenção das notas dos clientes
    for cliente in todos_clientes:
        cliente.notas = cliente.get_notas()  # Certifique-se de que isso só adiciona notas quando necessário
        cliente.notas_count = cliente.notas.filter(cliente=cliente).count()
        cliente.tem_nota_nova = cliente.notas.filter(nova=True).exists()

    # Serialização dos clientes, incluindo dados de renda
    clientes_serializados = ClienteSerializer(todos_clientes, many=True).data
    for cliente, cliente_serializado in zip(todos_clientes, clientes_serializados):
        cliente_serializado['valor_da_renda'] = cliente.valor_da_renda

    todos_corretores = Corretores.objects.all()
   
    contexto = {
        'clientes': todos_clientes,
        'clientes_json': json.dumps(clientes_serializados),
        'username': request.user.username,
        'user_id': request.user.id,
        'meses': meses,
        'corretores': todos_corretores,
    }

    if request.GET.get('concluido') == 'true':
        messages.success(request, "A mensagem Foi enviada com sucesso!")

    return render(request, 'lista_clientes.html', contexto)

@login_required
def deletar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    cliente.delete()
    messages.success(request, 'Cliente deletado com sucesso.')

    # Redirecione para a página 'lista_clientes'
    return redirect('lista_clientes')

@login_required
def deletar_venda(request, venda_id):
    venda = get_object_or_404(VendaCorretor, id=venda_id)

    # Salva a URL referente à página atual antes da deleção
    referer_url = request.META.get('HTTP_REFERER', None)

    if request.method == 'POST':
        venda.delete()
        messages.success(request, 'Venda deletada com sucesso.')

        # Redireciona para a URL salva (página anterior)
        return redirect(referer_url)

    # Não precisa mais renderizar o template
    return HttpResponse(status=204)

@login_required
def atualizar_status_cliente(request):
    try:
        if request.method == 'POST':
            cliente_id = request.POST.get('cliente_id')
            novo_status = request.POST.get('novo_status')

            # Atualizar o status do cliente
            cliente = Cliente.objects.get(pk=cliente_id)
            cliente.status = novo_status
            cliente.save()

            # Chame a função send_notification aqui
            send_notification(cliente)
            

            # Enviar uma resposta indicando sucesso
            return JsonResponse({"status": "success"})
    except Exception as e:
        # Isso retornará a descrição do erro para a resposta, ajudando na depuração.
        return JsonResponse({"status": "error", "error_message": str(e)})

    # Se algo der errado, retorne uma resposta de erro
    return JsonResponse({"status": "error", "error_message": "Método inválido ou outra falha"})

@login_required
def lista_de_corretores(request):
    if request.method == 'POST':
        try:
            corretor_id = request.POST.get('corretor_id')
            corretor_email = request.POST.get('email')
            corretor_senha = request.POST.get('senha')

            corretor = get_object_or_404(Corretores, id=corretor_id)
            corretor.email = corretor_email
            if corretor_senha:
                corretor.set_password(corretor_senha)
            corretor.save()

            return JsonResponse({'success': True})
        except ValidationError as e:
            return JsonResponse({'success': False, 'error': str(e)})

    todos_corretores = Corretores.objects.all()
    return render(request, 'lista_corretores.html', {'corretores': todos_corretores})

@login_required
def atualizar_corretor(request, corretor_id):
    if request.method == 'POST':
        corretor = get_object_or_404(CustomUser, id=corretor_id)

        form = UserUpdateForm(request.POST, instance=corretor)

        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Formulário inválido'}, status=400)

    return JsonResponse({'error': 'Método inválido'}, status=400)

def editar_corretor_view(request, corretor_id):
    corretor = get_object_or_404(CustomUser, pk=corretor_id)
    return render(request, 'editar_corretor.html', {'corretor': corretor})

@login_required
def atualizar_corretor_view(request, corretor_id):
    if request.method == 'POST':
        corretor = get_object_or_404(CustomUser, id=corretor_id)
        
        if 'password' in request.POST and 'confirm_password' in request.POST:
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']
            
            if password == confirm_password:
                corretor.set_password(password)
                corretor.save()
                
                # Adiciona a mensagem de sucesso
                messages.success(request, 'Senha atualizada com sucesso!')
                
                # Redireciona de volta para a página de edição
                return redirect('editar_corretor', corretor_id=corretor_id)
            else:
                messages.error(request, 'As senhas não coincidem')
                return redirect('editar_corretor', corretor_id=corretor_id)

    return JsonResponse({'error': 'Método inválido'}, status=400)

def deletar_corretor(request, corretor_id):
    corretor = get_object_or_404(CustomUser, id=corretor_id)
    
    if request.method == 'POST':
        corretor.delete()
        return redirect('lista_corretores')  # Substitua 'lista_corretores' pelo nome da sua URL de listagem de corretores
    
    return render(request, 'deletar_corretor.html', {'corretor': corretor})

@login_required
def cadastro_corretores(request):
    if request.method == 'POST':
        form = CorretorForm(request.POST, request.FILES)  # Adicione request.FILES aqui para lidar com uploads de arquivos
        if form.is_valid():
            # Primeiro, salve o objeto Corretor sem fazer commit no banco
            corretor = form.save(commit=False)

            # Adicione o prefixo +55 ao telefone
            telefone = form.cleaned_data.get('telefone')
            if telefone and not telefone.startswith('55'):
                corretor.telefone = '55' + telefone

            # Defina a senha usando set_password
            corretor.set_password(form.cleaned_data['password'])

            # Verifique se um arquivo de imagem foi fornecido
            if 'photo' in request.FILES:
                corretor.photo = request.FILES['photo']  # Salva a imagem no campo 'photo' do objeto Corretor

            corretor.save()
            return HttpResponseRedirect(reverse('admin_dashboard'))
    else:
        form = CorretorForm()
    return render(request, 'cadastro_corretores.html', {'form': form, 'username': request.user.username})


# cadastro de clientes

from django.contrib import messages
from PyPDF2 import PdfMerger  # Adicione esta linha

def parse_decimal(value_str):
    try:
        # Remove os símbolos de moeda e formatação, substitui ',' por '.' e converte para Decimal
        cleaned_value = value_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
        return Decimal(cleaned_value)
    except:
        return None
    
def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm2(request.POST, request.FILES)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.corretor = request.user
            cliente.save()

            corretor_folder = os.path.join("media/documentos", f"{request.user.username}/{cliente.cpf}")
            os.makedirs(corretor_folder, exist_ok=True)

            tipos_documentos = ['documentos_pessoais', 'extrato_bancario', 'documentos_dependente', 'documentos_conjuge']

            for tipo_documento in tipos_documentos:
                # Reinicia o processo para cada tipo de documento
                process_document_type(request, tipo_documento, corretor_folder, cliente)

            messages.success(request, 'Cliente cadastrado com sucesso!')
            send_notification_to_correspondente(cliente)  # Assuming this function is defined
            form = ClienteForm2()

    else:
        form = ClienteForm2()

    corretores = Corretores.objects.all()  # Ajuste conforme seu modelo de Corretores
    return render(request, 'cliente_form_template.html', {'form': form, 'corretores': corretores})

def process_document_type(request, tipo_documento, corretor_folder, cliente):
    folder_path = os.path.join(corretor_folder, tipo_documento.lower())
    os.makedirs(folder_path, exist_ok=True)
    uploaded_files = request.FILES.getlist(f'{tipo_documento}_file')

    combined_pdf_path = os.path.join(folder_path, f"{tipo_documento}_combined.pdf")
    
    # Verifica se o arquivo combinado já existe e remove se necessário
    if os.path.exists(combined_pdf_path):
        os.remove(combined_pdf_path)

    pdf_writer = PdfWriter()

    for uploaded_file in uploaded_files:
        file_path = os.path.join(folder_path, uploaded_file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        if uploaded_file.content_type.startswith(('image', 'application/tiff')) or uploaded_file.name.lower().endswith(('.jpeg', '.jpg', '.png')):
            converted_pdf_path = convert_to_pdf(file_path, folder_path, cliente)
            pdf_reader = PdfReader(converted_pdf_path)
            for page_number in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_number])
            # Exclui o arquivo de imagem após a conversão para PDF
            os.remove(file_path)
            os.remove(converted_pdf_path)
        elif uploaded_file.content_type == 'application/pdf':
            pdf_reader = PdfReader(file_path)
            for page_number in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_number])
            # Exclui o arquivo PDF após a adição ao PDF combinado
            os.remove(file_path)

    with open(combined_pdf_path, 'wb') as combined_pdf_file:
        pdf_writer.write(combined_pdf_file)

def convert_to_pdf(image_path, output_path, cliente):
    base_name, _ = os.path.splitext(os.path.basename(image_path))
    pdf_name = f"{cliente.nome.replace(' ', '')}-{cliente.cpf}-{base_name}.pdf"
    pdf_path = os.path.join(output_path, pdf_name)
    image = Image.open(image_path)
    width, height = image.size

    # Cria um objeto PDF
    pdf = canvas.Canvas(pdf_path, pagesize=(width, height))

    # Adiciona a imagem ao PDF
    pdf.drawInlineImage(image, 0, 0, width, height)

    # Salva o PDF
    pdf.save()

    # Fecha a imagem aberta
    image.close()

    return pdf_path

@csrf_exempt
def atualizar_cliente(request, client_id):
    
    if request.method == 'POST':
        try:
            cliente = Cliente.objects.get(pk=client_id)
        except Cliente.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Cliente não encontrado.'}, status=404)

        novo_status = request.POST.get('novo_status')
        nota_texto = request.POST.get('nota')
       
        # Verificar se o status foi alterado
        if novo_status and novo_status != cliente.status:
            cliente.status = novo_status
            cliente.save()

        # Adicionar nova nota, se aplicável
        if nota_texto and nota_texto.strip():
            # Aqui, incluímos request.user como o valor para o campo criado_por
            nova_nota = Nota.objects.create(cliente=cliente, texto=nota_texto, criado_por=request.user)
            
            # Verificar se a nota é nova e enviar notificação para o corretor
            if nova_nota.nova:
                corretor = cliente.corretor
                mensagem = f"⚠️ ATENÇÃO⚠️:\n O CLIENTE *{cliente.nome}* *TEM UMA NOTA E A NOTA É*:.\nDetalhes da nota: *{nova_nota.texto}*"

                send_notification_to_corretor_mensagem_personalizada(corretor, mensagem)
                # Marcar a nota como não nova após enviar a notificação
                nova_nota.nova = False
                nova_nota.save()

        # Processamento de documentos, apenas se o corretor e o CPF estiverem disponíveis
        if cliente.corretor and cliente.cpf:
            base_folder_path = os.path.join("media", "documentos", cliente.corretor.username, cliente.cpf)

            tipos_documentos = {
                'documentos_pessoais': 'documentos_pessoais',
                'extrato_bancario': 'extrato_bancario',
                'documentos_dependente': 'documentos_dependente',
                'documentos_conjuge': 'documentos_conjuge'
            }

            for tipo_doc, subpasta in tipos_documentos.items():
                documentos = request.FILES.getlist(tipo_doc)
                if documentos:
                    folder_path = os.path.join(base_folder_path, subpasta)
                    os.makedirs(folder_path, exist_ok=True)
                    pdf_filename = os.path.join(folder_path, f"{subpasta}_combined.pdf")

                    pdf_writer = PdfWriter()

                    if os.path.exists(pdf_filename) and os.path.getsize(pdf_filename) > 0:
                        with open(pdf_filename, "rb") as existing_pdf_file:
                            existing_pdf = PdfReader(existing_pdf_file)
                            for page in existing_pdf.pages:
                                pdf_writer.add_page(page)

                    for uploaded_file in documentos:
                        new_path = os.path.join(folder_path, os.path.basename(uploaded_file.name))
                        with open(new_path, 'wb+') as destination:
                            for chunk in uploaded_file.chunks():
                                destination.write(chunk)

                        try:
                            if uploaded_file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.tif')):
                                pdf_filename_temp = os.path.join(folder_path, f'temp_{subpasta}.pdf')
                                with open(pdf_filename_temp, 'wb') as temp_pdf:
                                    c = canvas.Canvas(temp_pdf)
                                    c.drawImage(new_path, 0, 0, width=595.276, height=841.890)  # A4 size
                                    c.showPage()
                                    c.save()

                                with open(pdf_filename_temp, 'rb') as img_pdf_file:
                                    img_pdf = PdfReader(img_pdf_file)
                                    for page in img_pdf.pages:
                                        pdf_writer.add_page(page)
                            elif uploaded_file.name.lower().endswith('.pdf'):
                                with open(new_path, 'rb') as new_pdf_file:
                                    new_pdf = PdfReader(new_pdf_file)
                                    for page in new_pdf.pages:
                                        pdf_writer.add_page(page)
                        finally:
                            os.remove(new_path)

                    with open(pdf_filename, 'wb') as merged_pdf_file:
                        pdf_writer.write(merged_pdf_file)

        return JsonResponse({'status': 'success', 'message': 'Cliente atualizado com sucesso.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método inválido.'}, status=405)

    


@login_required
def cadastro_correspondentes(request):
    if request.method == 'POST':
        form = CorrespondenteForm(request.POST, request.FILES)  # Note a inclusão de request.FILES
        if form.is_valid():
            correspondente = form.save(commit=False)  # Não salve ainda

            # Adicione o prefixo +55 ao telefone
            telefone = form.cleaned_data.get('telefone')
            if telefone and not telefone.startswith('55'):
                correspondente.telefone = '55' + telefone

            correspondente.set_password(form.cleaned_data['password'])
            correspondente.save()

            # Tente obter o grupo "correspondente" ou crie se não existir
            group, _ = Group.objects.get_or_create(name='correspondente')

            if 'photo' in request.FILES:
                correspondente.photo = request.FILES['photo']  # Salva a imagem no campo 'photo' do objeto Corretor

            # Adicione o correspondente ao grupo
            # Verifique se 'correspondente' é uma instância do modelo User
            if isinstance(correspondente, User):
                group.user_set.add(correspondente)

            return HttpResponseRedirect(reverse('admin_dashboard'))

    else:
        form = CorrespondenteForm()

    return render(request, 'cadastro_correspondentes.html', {'form': form, 'username': request.user.username})


@csrf_exempt
@login_required
def consulta_cpf(request):
    if request.method == "POST":
        cpf_raw = request.POST.get('cpf', '')
        cpf = re.sub(r'[^0-9]', '', cpf_raw)

        if not cpf or len(cpf) != 11:
            return JsonResponse({'error': 'CPF inválido'})

        try:
            result = consulta_cpf_func(cpf)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': str(e)})

    return render(request, 'consulta_cpf.html', {'username': request.user.username})


@login_required
@user_passes_test(is_corretor)
def broker_dashboard(request):
    
    corretor = request.user
    # Obter a contagem de vários modelos
    total_corretores = Corretores.objects.count()
    clientes_do_corretor = Cliente.objects.filter(corretor=corretor)

    # Obtém o número total de clientes associados ao corretor
    total_clientes = clientes_do_corretor.count()
    
    total_correspondentes = Correspondente.objects.count()
    recent_transactions = Transaction.objects.all().order_by('-id')[:8]
   
    total_contatos = Contato.objects.count()
    contatos_hoje = Contato.objects.filter(
        data_registro=datetime.now().date()).count()
    contatos_7_dias = Contato.objects.filter(
        data_registro__gte=datetime.now() - timedelta(days=7)).count()

    status_counts = Cliente.objects.filter(corretor=corretor).values(
        'status').annotate(total=Count('status'))
    status_counts_dict = {item['status']: item['total']
                          for item in status_counts}
    all_statuses = [
        {'status': choice[0], 'total': status_counts_dict.get(
            choice[0], 0), 'display': choice[1]}
        for choice in Cliente.STATUS_CHOICES
    ]

    # Filtrar apenas os clientes vinculados ao corretor
    clientes = clientes_do_corretor

    # Gerar dados mensais
    monthly_counts = clientes.annotate(
        month=ExtractMonth('data_de_criacao'),
        year=ExtractYear('data_de_criacao')
    ).values('month', 'year').annotate(total=Count('id')).order_by('year', 'month')

    # Gerar dados anuais
    annual_counts = clientes.annotate(
        year=ExtractYear('data_de_criacao')
    ).values('year').annotate(total=Count('id')).order_by('year')

    # Converter os QuerySets em JSON
    monthly_data_json = list(monthly_counts)
    annual_data_json = list(annual_counts)

    # Converter os QuerySets em JSON
    monthly_data_json = json.dumps(list(monthly_counts))
    annual_data_json = json.dumps(list(annual_counts))

    # Mapeia o número do mês para o nome do mês
    months = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }

    # Corrige os rótulos do gráfico
    chart_labels = []
    for entry in monthly_counts:
        month = entry.get('month')
        year = entry.get('year')
        if month and month in months:
            chart_labels.append(f"{months[month]} {year}")
        else:
            chart_labels.append(f"Mês Desconhecido {year if year else ''}")

    chart_data = {
        'labels': chart_labels,
        'data': [entry.get('total', 0) for entry in monthly_counts]
    }

    chart_data_json = json.dumps(chart_data)    

    current_year = datetime.now().year
    last_year = current_year - 1
    current_month = datetime.now().month

    total_current = Cliente.objects.filter(
        data_de_criacao__year=current_year,
        data_de_criacao__month=current_month,
        corretor=corretor
    ).count()
    total_last_year = Cliente.objects.filter(
        data_de_criacao__year=last_year,
        data_de_criacao__month=current_month,
        corretor=corretor
    ).count()

    try:
        percent_change = (
            (total_current - total_last_year) / total_last_year) * 100
    except ZeroDivisionError:
        percent_change = 0    

    # Calcula os top 4 status
    top_statuses_data = Cliente.objects.filter(corretor=corretor).values('status').annotate(
        total=Count('status')).order_by('-total')[:4]

    top_statuses = [
        {
            'status': item['status'],
            'total': item['total'],
            'display': Cliente(status=item['status']).get_status_display()
        }
        for item in top_statuses_data
    ]

    clientes = clientes_do_corretor
    
    # Filtra os processos associados ao corretor
    processos = Processo.objects.filter(responsaveis=corretor).order_by('-data_inicio')

    processos_em_andamento = [
        processo for processo in processos if processo.data_finalizacao is None]
    total_processos_em_andamento = len(processos_em_andamento)

    try:
        corretor_group = Group.objects.get(name='Corretores')
        corretores = corretor_group.user_set.all()
    except Group.DoesNotExist:
        corretores = []

    # Calcular o progresso para cada processo
    for processo in processos:
        processo.progresso = calcular_progresso(
            processo, processo.id, processo.cliente)
        if processo.cliente:
            processo.opcoes_selecionadas = OpcaoSelecionada.objects.filter(processo=processo)

    data_referencia = datetime.now() - timedelta(days=7)
    total_clientes_recentes = Cliente.objects.filter(
        corretor=corretor,
        data_de_criacao__gte=data_referencia
    ).count()

    context = {
        'total_clientes_recentes': total_clientes_recentes,
        'total_processos_em_andamento': total_processos_em_andamento,
        'current_year': current_year,
        'current_month': current_month,
        'percent_change': int(percent_change),
        'monthly_data_json': monthly_data_json,
        'annual_data_json': annual_data_json,
        'chart_data_json': chart_data_json,
        'chart_data': chart_data,       
        'total_contatos': total_contatos,
        'contatos_hoje': contatos_hoje,
        'contatos_7_dias': contatos_7_dias,
        'recent_transactions': recent_transactions,
        'total_corretores': total_corretores,
        'total_clientes': total_clientes,
        'total_correspondentes': total_correspondentes,        
        'notas_privadas': NotaPrivada.objects.filter(user=request.user).order_by('-data'),
        'all_statuses': all_statuses,
        'username': request.user.username,
        'top_statuses': top_statuses,
        'status_choices': dict(Cliente.STATUS_CHOICES),
        'clientes': clientes,
        'processos': processos,
    }

    return render(request, 'broker_dashboard.html', context)

from django.db.models.functions import TruncDay

#administrador
@user_passes_test(is_admin)

@login_required
def admin_dashboard(request):
    context = {}  # Initialize the context dictionary

    # Coleta de dados
    fixed_expenses = get_fixed_expenses(request.user)
    dias = [i for i in range(1, 32)]

    # Obter a contagem de vários modelos
    total_corretores = Corretores.objects.count()
    total_clientes = Cliente.objects.count()
    total_correspondentes = Correspondente.objects.count()
    recent_transactions = Transaction.objects.all().order_by('-id')[:8]

    total_proprietarios = Proprietario.objects.count()
    total_contatos = Contato.objects.count()
    contatos_hoje = Contato.objects.filter(
        data_registro=timezone.now().date()).count()
    contatos_7_dias = Contato.objects.filter(
        data_registro__gte=timezone.now() - timedelta(days=7)).count()

    status_counts = Cliente.objects.values(
        'status').annotate(total=Count('status'))
    status_counts_dict = {item['status']: item['total']
                          for item in status_counts}
    all_statuses = [
        {'status': choice[0], 'total': status_counts_dict.get(
            choice[0], 0), 'display': choice[1]}
        for choice in Cliente.STATUS_CHOICES
    ]

    # Gerar dados mensais
    monthly_counts = Cliente.objects.filter(data_de_criacao__isnull=False).annotate(
        month=ExtractMonth('data_de_criacao'),
        year=ExtractYear('data_de_criacao')
    ).values('month', 'year').annotate(total=Count('id')).order_by('year', 'month')

    # Gerar dados anuais
    annual_counts = Cliente.objects.filter(data_de_criacao__isnull=False).annotate(
        year=ExtractYear('data_de_criacao')
    ).values('year').annotate(total=Count('id')).order_by('year')

    # Converter os QuerySets em JSON
    monthly_data_json = json.dumps(list(monthly_counts))
    annual_data_json = json.dumps(list(annual_counts))

    # Mapeia o número do mês para o nome do mês
    months = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }

    # Corrige os rótulos do gráfico
    chart_labels = []
    for entry in monthly_counts:
        month = entry.get('month')
        year = entry.get('year')
        if month and month in months:
            chart_labels.append(f"{months[month]} {year}")
        else:
            chart_labels.append(f"Mês Desconhecido {year if year else ''}")

    chart_data = {
        'labels': chart_labels,
        'data': [entry.get('total', 0) for entry in monthly_counts]
    }

    chart_data_json = json.dumps(chart_data)

    today = timezone.now().day
    expenses_due_soon = [expense for expense in fixed_expenses if 0 < (
        expense.due_day - today) <= 3]

    current_year = timezone.now().year
    last_year = current_year - 1
    current_month = timezone.now().month

    total_current = Cliente.objects.filter(
        data_de_criacao__year=current_year,
        data_de_criacao__month=current_month
    ).count()
    total_last_year = Cliente.objects.filter(
        data_de_criacao__year=last_year,
        data_de_criacao__month=current_month
    ).count()

    try:
        percent_change = (
            (total_current - total_last_year) / total_last_year) * 100
    except ZeroDivisionError:
        percent_change = 0

    vendas_corretores_list = VendaCorretor.objects.all()
    paginator = Paginator(vendas_corretores_list, 15)

    page_number = request.GET.get('page')
    vendas_corretores = paginator.get_page(page_number)
    clientes = Cliente.objects.all()
    corretores = Corretores.objects.all()

    # Obter a contagem de clientes por corretor no mês atual
    top_corretores_mes_atual = Cliente.objects.filter(
        data_de_criacao__month=current_month,
        data_de_criacao__year=current_year
    ).values(
        'corretor__first_name',
        'corretor__username'
    ).annotate(
        total=Count('id'),
        month=ExtractMonth('data_de_criacao')
    ).order_by('-total')[:5]

    # Se não houver resultados com 'first_name', tente 'username'
    if not top_corretores_mes_atual.exists():
        top_corretores_mes_atual = Cliente.objects.filter(
            data_de_criacao__month=current_month,
            data_de_criacao__year=current_year
        ).values(
            'corretor__username'
        ).annotate(
            total=Count('id'),
            month=ExtractMonth('data_de_criacao')
        ).order_by('-total')[:15]

    # Criar a lista final de top corretores
    top_corretores_list = [
        {
            'nome': entry.get('corretor__first_name') or entry.get('corretor__username') or 'Nome Desconhecido',
            'total': entry['total'],
            'month': entry['month']
        }
        for entry in top_corretores_mes_atual]

    processos = Processo.objects.all().order_by('-data_inicio')
    processos_em_andamento = Processo.objects.filter(
        data_finalizacao__isnull=True
    ).exclude(
        id__in=OpcaoSelecionada.objects.filter(opcao='Finalizado').values_list('processo_id', flat=True)
    ).order_by('data_inicio')

    processos_em_andamento = [
        processo for processo in processos if processo.data_finalizacao is None]
    total_processos_em_andamento = len(processos_em_andamento)

    for processo in processos_em_andamento:
        # Aqui você pode acessar as opções selecionadas para cada processo
        opcoes_selecionadas = OpcaoSelecionada.objects.filter(processo=processo)

    # Define processo before using it
    processo = None
    if processos_em_andamento:
        # Assign first processo from processos_em_andamento
        processo = processos_em_andamento[0]

    tipo_processo = None
    if processo:
        tipo_processo = TipoProcesso.objects.get(nome=processo.tipo)

    # Calcular o progresso para cada processo
    for processo in processos:
        if processo:
            processo.progresso = int(calcular_progresso(
                processo, processo.id, processo.cliente))
            processo.num_notas = Nota_notification.objects.filter(processo=processo).count()
            processo.num_notas_nao_concluidas = Nota_notification.objects.filter(processo=processo, nova=True).count()
            if processo.cliente:
                processo.opcoes_selecionadas = OpcaoSelecionada.objects.filter(processo=processo)
            else:
                processo.opcoes_selecionadas = None  # or whatever default value you want

    # Define opcoes_selecionadas here to ensure it's always defined
    opcoes_selecionadas = []
    # Gerar dados diários
    daily_counts = Cliente.objects.filter(data_de_criacao__isnull=False).annotate(
        day=TruncDay('data_de_criacao')
    ).values('day').annotate(total=Count('id')).order_by('day')

    # Converter os QuerySets em JSON
    daily_data_json = json.dumps(list(daily_counts), cls=DjangoJSONEncoder)

    # Passar daily_data_json para o contexto
    context['daily_data_json'] = daily_data_json

    tipo_processo = None
    opcoes_disponiveis = []
    opcoes_selecionadas_list = []
    opcoes_selecionadas_dict = {}

    if processo:
        tipo_processo = TipoProcesso.objects.get(nome=processo.tipo)
        opcoes_disponiveis = [opcao.strip() for opcao in tipo_processo.obter_opcoes()]
        opcoes_selecionadas = OpcaoSelecionada.objects.filter(processo=processo)

        opcoes_selecionadas_list = [(opcao.opcao.strip(), opcao.data_selecionada.strftime('%d/%m/%Y')) for opcao in opcoes_selecionadas]
        opcoes_selecionadas_dict = {opcao.opcao.strip(): opcao.data_selecionada.strftime('%d/%m/%Y') for opcao in opcoes_selecionadas}

    context = {
        'top_corretores_list': top_corretores_list,
        'corretores': corretores,
        'processos': processos_em_andamento,
        'total_processos_em_andamento': total_processos_em_andamento,
        'current_year': current_year,
        'current_month': current_month,
        'percent_change': int(percent_change),
        'monthly_data_json': monthly_data_json,
        'annual_data_json': annual_data_json,
        'chart_data_json': chart_data_json,
        'chart_data': chart_data,
        'expenses_due_soon': expenses_due_soon,
        'total_proprietarios': total_proprietarios,
        'total_contatos': total_contatos,
        'contatos_hoje': contatos_hoje,
        'contatos_7_dias': contatos_7_dias,
        'recent_transactions': recent_transactions,
        'total_corretores': total_corretores,
        'total_clientes': total_clientes,
        'total_correspondentes': total_correspondentes,
        'fixed_expenses': fixed_expenses,
        'dias': dias,
        'notas_privadas': NotaPrivada.objects.filter(user=request.user).order_by('-data'),
        'all_statuses': all_statuses,
        'opcoes_selecionadas': opcoes_selecionadas,
        'opcoes_selecionadas_list': opcoes_selecionadas_list,
        'opcoes_disponiveis': opcoes_disponiveis,
        'opcoes_selecionadas_dict': opcoes_selecionadas_dict,
        'username': request.user.username,
        'vendas_corretores': vendas_corretores,
        'clientes': clientes,
    }

    # Obter clientes recentes deste mês
    current_date = timezone.now()
    current_month = current_date.month
    current_year = current_date.year
    start_of_month = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - timedelta(days=1)

    recent_clients = Cliente.objects.filter(
        data_de_criacao__gte=start_of_month,
        data_de_criacao__lte=end_of_month
    )
    total_recent_clients = recent_clients.count()

    context['total_recent_clients'] = total_recent_clients
    context['recent_clients'] = recent_clients

    return render(request, 'admin_dashboard.html', context)




def delete_expense(request, expense_id):
    if expense_id:  # Verifica se o ID não está vazio
        expense = get_object_or_404(FixedExpense, id=expense_id)
        expense.delete()

    return redirect('financas_view')



# Define o codificador personalizado
class DecimalEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

# Função para calcular saldo
def calcular_saldo(totais):
    saldo_acumulado = 0
    for total in totais:
        saldo_acumulado += float(total['receitas'] or 0)
        saldo_acumulado -= float(total['despesas'] or 0)
        total['saldo'] = saldo_acumulado
    return totais
# Sua view completa

def financas_view(request):
    # Obtém todas as transações do usuário atual ordenadas pelo ID
    transacoes = Transaction.objects.filter(user=request.user).order_by('id')

    # Inicializa o formulário de transação
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transacao = form.save(commit=False)
            transacao.user = request.user
            transacao.save()
            return redirect('financas_view')
    else:
        form = TransactionForm()

    # Calcula totais mensais e anuais de receitas e despesas
    totais_mensais = transacoes.annotate(
        mes=ExtractMonth('created_at'),
        ano=ExtractYear('created_at')
    ).values('mes', 'ano').annotate(
        receitas=Sum('valor', filter=Q(tipo='receita')),
        despesas=Sum('valor', filter=Q(tipo='despesa'))
    ).order_by('ano', 'mes')

    # Estrutura de dados para o gráfico
    chart_data = {
        'meses': [],
        'receitas': [],
        'despesas': []
    }

    for total in totais_mensais:
        chart_data['meses'].append(f"{total['mes']}/{total['ano']}")
        chart_data['receitas'].append(total['receitas'] or 0)
        chart_data['despesas'].append(total['despesas'] or 0)

    # Convertendo totais mensais para JSON usando o codificador personalizado
    totais_mensais_json = json.dumps(chart_data, cls=DecimalEncoder)

    # Aplicar filtro com base na descrição, se fornecido
    search_description = request.GET.get('search_description')
    if search_description:
        transacoes = transacoes.filter(
            description__icontains=search_description)

    # Configuração da paginação
    page = request.GET.get('page', 1)
    paginator = Paginator(transacoes, 5)

    try:
        transacoes = paginator.page(page)
    except PageNotAnInteger:
        transacoes = paginator.page(1)
    except EmptyPage:
        transacoes = paginator.page(paginator.num_pages)

    # Calcular totais gerais de receitas e despesas
    total_receita_geral = totais_mensais.aggregate(Sum('receitas'))['receitas__sum'] or 0
    total_despesa_geral = totais_mensais.aggregate(Sum('despesas'))['despesas__sum'] or 0
    total_geral = total_receita_geral - total_despesa_geral

    # Obter despesas fixas
    fixed_expenses = get_fixed_expenses(request.user)

    # Obter transações do mês atual
    current_month_transactions = Transaction.objects.filter(
        user=request.user,
        created_at__month=timezone.now().month,
        created_at__year=timezone.now().year
    )

    # Calcular despesas totais e receitas totais
    total_despesas = current_month_transactions.filter(tipo='despesa').aggregate(total=Sum('valor'))['total'] or 0
    total_receitas = current_month_transactions.filter(tipo='receita').aggregate(total=Sum('valor'))['total'] or 0

    # Calcular saldo atual
    saldo = total_receitas - total_despesas

    # Obter contagem de vários modelos
    total_corretores = Corretores.objects.count()
    total_clientes = Cliente.objects.count()
    total_correspondentes = Correspondente.objects.count()

    # Obter transações recentes
    recent_transactions = Transaction.objects.all().order_by('-id')[:8]

    # Renderizar o template
    return render(request, 'financas.html', {
        'transacoes': transacoes,
        'form': form,
        'totais_mensais_json': totais_mensais_json,
        'total_receita_geral': total_receita_geral,
        'total_despesa_geral': total_despesa_geral,
        'total_geral': total_geral,
        'fixed_expenses': fixed_expenses,
        'saldo': saldo,
        'total_corretores': total_corretores,
        'total_clientes': total_clientes,
        'total_correspondentes': total_correspondentes,
        'recent_transactions': recent_transactions,
    })
    
# Adicione esta nova view para lidar com a solicitação AJAX

# Financeiro


@login_required
def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    transaction.delete()
    return redirect('financas_view')


def filtrar_por_mes_ano(request):
    if request.method == 'GET':
        user = request.user
        mes = request.GET.get('mes')
        ano = request.GET.get('ano')

        # Filtre as transações com base no mês e no ano
        transacoes_filtradas = Transaction.objects.filter(
            user=user,
            created_at__month=mes,
            created_at__year=ano
        )

        # Realize as operações necessárias para obter os totais mensais e anuais
        totais_mensais = transacoes_filtradas.annotate(
            mes=ExtractMonth('created_at'),
            ano=ExtractYear('created_at')
        ).values('mes', 'ano').annotate(
            receitas=Sum('valor', filter=Q(tipo='receita')),
            despesas=Sum('valor', filter=Q(tipo='despesa'))
        ).order_by('ano', 'mes')

        totais_anuais = transacoes_filtradas.annotate(
            ano=ExtractYear('created_at')
        ).values('ano').annotate(
            receitas=Sum('valor', filter=Q(tipo='receita')),
            despesas=Sum('valor', filter=Q(tipo='despesa'))
        ).order_by('ano')

        totais_mensais_saldo = calcular_saldo(list(totais_mensais))
        totais_anuais_saldo = calcular_saldo(list(totais_anuais))

        # Retorne os totais mensais e anuais como JSON
        data = {
            'totais_mensais': totais_mensais_saldo,
            'totais_anuais': totais_anuais_saldo,
        }
        return JsonResponse(data, safe=False)


def get_fixed_expenses(user):
    today = datetime.today()
    for expense in FixedExpense.objects.filter(user=user):
        if expense.month_paid and expense.month_paid != today.month:
            expense.is_paid = False
            expense.save()
    return FixedExpense.objects.filter(user=user)


def calcular_porcentagem(valor_atual, valor_anterior):
    if valor_anterior == 0:
        return 0
    return ((valor_atual - valor_anterior) / valor_anterior) * 100


@login_required
def lista_proprietarios(request):
    proprietarios = Proprietario.objects.all()
    notas_privadas = NotaPrivada.objects.filter(user=request.user).order_by('-data')

    total_proprietarios = proprietarios.count()
    total_contatos = Contato.objects.count()
    contatos_hoje = Contato.objects.filter(data_registro=timezone.now().date()).count()
    contatos_7_dias = Contato.objects.filter(data_registro__gte=timezone.now() - timezone.timedelta(days=7)).count()

    context = {
        'proprietarios': proprietarios,
        'notas_privadas': notas_privadas,
        'form': ProprietarioForm(),
        'total_proprietarios': total_proprietarios,
        'total_contatos': total_contatos,
        'contatos_hoje': contatos_hoje,
        'contatos_7_dias': contatos_7_dias,        
        'username': request.user.username
    }

    return render(request, 'lista_proprietarios.html', context)

def editar_proprietario(request, proprietario_id):
    proprietario = get_object_or_404(Proprietario, pk=proprietario_id)

    if request.method == 'POST':
        form = ProprietarioForm(request.POST, request.FILES, instance=proprietario)
        if form.is_valid():
            form.save()
            return redirect('lista_proprietarios')
    else:
        form = ProprietarioForm(instance=proprietario)

    return render(request, 'editar_proprietario.html', {'form': form, 'proprietario': proprietario})

def adicionar_nota(request):
    if request.method == "POST":
        conteudo = request.POST.get('conteudo')        

        nota = NotaPrivada(user=request.user, conteudo=conteudo)
        nota.save()        

        return redirect('lista_proprietarios')



def editar_nota(request, nota_id):
    nota = get_object_or_404(NotaPrivada, id=nota_id)

    if request.method == "POST":
        conteudo = request.POST.get('conteudo')
        nota.conteudo = conteudo
        nota.save()
        return redirect('lista_proprietarios')
    else:
        context = {
            'nota': nota
        }
        return render(request, 'lista_proprietarios.html', context)


def concluir_nota(request, nota_id):
    nota = get_object_or_404(NotaPrivada, id=nota_id)
    nota.concluido = True
    nota.save()
    return redirect('lista_proprietarios')


def deletar_nota(request, nota_id):
    nota = get_object_or_404(Nota_notification, id=nota_id)
    nota.delete()
    # Após excluir a nota, redirecione para uma página adequada
    return redirect('lista_processos')



@login_required
def add_fixed_expense(request):
    if request.method == 'POST':
        description = request.POST.get('description')
        due_day = int(request.POST.get('due_day'))
        amount = request.POST.get('amount')
        user = request.user

        # Cria uma nova despesa fixa e salva no banco de dados
        FixedExpense.objects.create(
            description=description, due_day=due_day, amount=amount, user=user)

        # Redireciona para a página do dashboard após adicionar a despesa
        return redirect('financas_view')

    dias = list(range(1, 32))
    context = {
        'dias': dias
    }
    return render(request, 'financas.html', context)


def reset_fixed_expenses():
    last_month = datetime.today().month - 1
    if last_month == 0:
        last_month = 12
    FixedExpense.objects.filter(month_paid=last_month).update(
        is_paid=False, month_paid=None)


@login_required
def mark_as_paid(request, expense_id):
    expense = get_object_or_404(FixedExpense, id=expense_id, user=request.user)
    expense.is_paid = True
    expense.month_paid = date.today().month
    expense.save()
    return redirect('financas_view')


def toggle_expense_status(request, expense_id):
    expense = FixedExpense.objects.get(id=expense_id)
    expense.is_paid = not expense.is_paid
    expense.save()
    return redirect('financas_view')


def delete_expense(request, expense_id):
    expense = get_object_or_404(FixedExpense, id=expense_id)
    expense.delete()
    messages.success(request, "Despesa excluída com sucesso.")
    return redirect('financas_view')


# Função whatsapp notificação


@csrf_exempt
def send_notification(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        clienteId = data.get('cliente_id')

        try:
            cliente = Cliente.objects.get(pk=clienteId)

            whatsapp_num = f"{cliente.corretor.telefone}@c.us"
            message = f'O status do cliente *{cliente.nome}*  foi atualizado para *{cliente.status.replace("_", " ")}*.'

            payload = {
                'number': whatsapp_num,
                'message': message
            }

            response = requests.post(
                'http://localhost:5000/send-message', json=payload)

            if response.json().get('success'):
                return JsonResponse({"message": "Notification sent successfully"})
            else:
                error_message = response.json().get('error', 'Unknown error')
                return JsonResponse({"error": f"Failed to send the message on WhatsApp due to: {error_message}"}, status=500)
        except Cliente.DoesNotExist:
            return JsonResponse({"error": "Cliente not found"}, status=404)

import random
def send_notification_to_correspondente(cliente):
   
    
    correspondentes = Correspondente.objects.all()
    success = 0
    failed = 0

    messages = [
        f'🎉 Olá! O cliente *{cliente.nome}* foi cadastrado pelo corretor *{cliente.corretor.first_name}* *{cliente.corretor.last_name}* com sucesso no sistema! Por favor, verifique o CRM para mais detalhes. 😊',
        f'Ei, temos uma novidade! 🚀 O cliente *{cliente.nome}* acabou de ser cadastrado pelo corretor *{cliente.corretor.first_name}* *{cliente.corretor.last_name}* no sistema. Não deixe de dar uma conferida no CRM! 👀',
        f'Hey! 🎈 Só queria te contar que o corretor *{cliente.corretor.first_name}* *{cliente.corretor.last_name}* acabou de cadastrar o cliente *{cliente.nome}* no sistema com sucesso! Não esqueça de dar uma olhada no CRM. 😉'
    ]

    for correspondente in correspondentes:
        try:
            # Formatando o telefone
            whatsapp_num = f"{correspondente.telefone}@c.us"

            payload = {
                'number': whatsapp_num,
                'message': random.choice(messages)
            }

            response = requests.post(
                'http://localhost:5000/send-message', json=payload)

            if response.json().get('success'):
                success += 1
            else:
                error_message = response.json().get('error', 'Unknown error')
                
                failed += 1

        except Exception as e:
            
            failed += 1

    return {"message": f"Notifications sent successfully to {success} correspondentes, failed for {failed}."}

def verificar_clientes_aguardando_aprovacao():
   
    try:
        # Verifica se o dia atual é um dia útil (segunda a sexta-feira)
        hoje = datetime.now()  # Correção aqui
        dia_semana = hoje.weekday()  # Segunda = 0, Terça = 1, ..., Sexta = 4

        if dia_semana < 5:  # Verifica se é um dia da semana (segunda a sexta)
            # Verifica se o horário atual está dentro do intervalo de 7h às 18h
            hora_atual = hoje.hour
            if 7 <= hora_atual < 18:
                # Verifica se há clientes aguardando aprovação
                clientes_aguardando = Cliente.objects.filter(status='aguardando_aprovacao')

                if clientes_aguardando.exists():
                    # Obtém todos os correspondentes
                    correspondentes = Correspondente.objects.all()

                    messages = [
                        '🚨 Atenção! Existem clientes aguardando aprovação. Por favor, verifique o CRM para mais detalhes.',
                        '🔔 Notificação: Há clientes aguardando aprovação no sistema. Favor verificar o CRM.'
                    ]

                    # Envia a mensagem para cada correspondente
                    for correspondente in correspondentes:
                        whatsapp_num = f"{correspondente.telefone}@c.us"
                        message = random.choice(messages)

                        payload = {'number': whatsapp_num, 'message': message}

                        # Envia a mensagem para o correspondente
                        response = requests.post('http://localhost:5000/send-message', json=payload)

                        if response.status_code == 200:
                            print(f"Message sent successfully to {whatsapp_num}")
                        else:
                            print(f"Failed to send message to {whatsapp_num}")

                    return "Mensagens enviadas com sucesso para todos os correspondentes."
                else:
                    return "Não há clientes aguardando aprovação."
            else:
                return "Fora do horário de envio (7h às 18h)."
        else:
            return "Hoje não é um dia útil (fim de semana)."
    except Exception as e:
        return f"Erro ao enviar mensagens: {str(e)}"



def concluir_processo(request, cliente_id):
    try:
        # Obtenha o cliente usando o cliente_id
        cliente = Cliente.objects.get(pk=cliente_id)

        # Altere o status do cliente para 'aguardando_aprovacao'
        cliente.status = 'aguardando_aprovacao'
        cliente.save()

        # Adicione sua lógica existente aqui
        mensagem = f"🚀 Atualização Importante: O corretor {cliente.corretor.first_name} {cliente.corretor.last_name} acabou de concluir o processo para o cliente *{cliente.nome}*! Por favor, verifique a nota do cliente para garantir que tudo esteja em ordem. 📝✅"

        send_notification_to_correspondente_mensagem_personalizada(cliente, mensagem)

        # Adicione lógica adicional conforme necessário

        # Redirecione para a página 'lista_clientes'
        messages.success(request, "Processo concluído com sucesso.")
        return redirect('lista_clientes')
    except Cliente.DoesNotExist:
        # Lide com o caso em que o cliente não existe
        messages.error(request, "Cliente não encontrado.")
        return redirect('lista_clientes')
    
def send_notification_to_corretor_mensagem_personalizada(corretor, mensagem):
    try:
        # Formatando o telefone
        whatsapp_num = f"{corretor.telefone}@c.us"

        payload = {
            'number': whatsapp_num,
            'message': mensagem
        }

        response = requests.post(
            'http://localhost:5000/send-message', json=payload)

        if response.json().get('success'):
            return True  # Indica que a notificação foi enviada com sucesso
        else:
            error_message = response.json().get('error', 'Unknown error')
            return False  # Indica que houve um erro ao enviar a notificação

    except Exception as e:
        return False  # Indica que houve um erro ao enviar a notificação


def send_notification_to_correspondente_mensagem_personalizada(request, mensagem):
    correspondentes = Correspondente.objects.all()
    success = 0
    failed = 0
    
    for correspondente in correspondentes:
        try:
            # formatando o telefone
            whatsapp_num = f"{correspondente.telefone}@c.us"

            payload = {
                'number': whatsapp_num,
                'message': mensagem
            }

            response = requests.post(
                'http://localhost:5000/send-message', json=payload)

            if response.json().get('success'):
                success += 1
            else:
                error_message = response.json().get('error', 'Unknown error')
                failed += 1

        except Exception as e:
            failed += 1

    # Redirecione para a página 'lista_processos'
    return redirect('lista_processos')

@login_required
def enviar_mensagem_correspondente(request):
    try:
        # Obtenha os dados do AJAX
        processo_id = request.POST.get('processo_id')
        nota_id = request.POST.get('nota_id')

        # Obtenha a nota associada ao ID fornecido
        nota = get_object_or_404(Nota_notification, id=nota_id)

        # Obtenha o cliente associado à nota
        cliente = nota.processo.cliente

        # Chame a função existente para enviar a mensagem para o correspondente
        mensagem = f"Olá, a nota do cliente *{cliente.nome}* foi marcada como concluída. Por favor, verificar se está tudo certo."
        result = send_notification_to_correspondente_mensagem_personalizada(cliente, mensagem)

        # Obtenha a URL de referência da solicitação
        referer = request.META.get('HTTP_REFERER')

        # Adicione a URL à resposta JSON
        result["reload_page"] = {"url": referer}

        return redirect('lista_processos')

    except Nota_notification.DoesNotExist:
        
        return JsonResponse({'error': 'Nota não encontrada'}, status=400)
    except Cliente.DoesNotExist:
        
        return JsonResponse({'error': 'Cliente não encontrado para a nota'}, status=400)
    except Exception as e:
        
        return JsonResponse({"error": str(e)}, status=500)

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_correspondente)
def lista_de_corretores(request):
    corretores = Corretores.objects.all()

    if request.method == 'POST':
        form = CorretorForm(request.POST)
        if form.is_valid():
            form.save()
            # Retorne uma mensagem de sucesso se desejar

    return render(request, 'listadecorretores.html', {'corretores': corretores, 'username': request.user.username})


@login_required
def settings_view(request):
    # Inicialização padrão dos forms
    form = UserSettingsForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        if 'update_settings' in request.POST:
            form = UserSettingsForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(
                    request, 'Configurações atualizadas com sucesso!')
                return redirect('settings')
            else:
                messages.error(request, 'Por favor, corrija os erros abaixo.')
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                # Atualiza a sessão após a mudança de senha para evitar deslogar o usuário
                update_session_auth_hash(request, user)
                messages.success(request, 'Senha alterada com sucesso!')
                return redirect('settings')
            else:
                messages.error(request, 'Erro ao alterar a senha.')

    context = {
        'form': form,
        'password_form': password_form,
        'username': request.user.username
    }

    return render(request, 'settings_template.html', context)



@csrf_exempt
def adicionar_proprietario(request):
    if request.method == 'POST':
        form = ProprietarioForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                proprietario = form.save()

                # Creating the 'proprietario' folder based on the owner's id
                folder_path = Path("media/proprietario") / str(proprietario.id)
                folder_path.mkdir(parents=True, exist_ok=True)

                documentos = request.FILES.getlist('documentacao')
                if documentos:
                    folder_path = Path("media/proprietario") / f"{proprietario.nome}-{proprietario.cpf_cnpj}"
                    folder_path.mkdir(parents=True, exist_ok=True)
                    pdf_filename = folder_path / f"{proprietario.nome}-{proprietario.cpf_cnpj}.pdf"

                    pdf_writer = PdfWriter()

                    for uploaded_file in documentos:
                        new_path = folder_path / uploaded_file.name
                        with open(new_path, 'wb+') as destination:
                            for chunk in uploaded_file.chunks():
                                destination.write(chunk)

                        try:
                            if uploaded_file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.tif')):
                                with Image.open(new_path) as img:
                                    img.convert('RGB').save(new_path, format='PDF')
                                    with open(new_path, "rb") as img_pdf_file:
                                        pdf_writer.add_page(
                                            PdfReader(img_pdf_file).pages[0])
                            elif uploaded_file.name.lower().endswith('.pdf'):
                                with open(new_path, "rb") as new_pdf_file:
                                    new_pdf = PdfReader(new_pdf_file)
                                    for page in new_pdf.pages:
                                        pdf_writer.add_page(page)
                        finally:
                            new_path.unlink()

                    with open(pdf_filename, "wb") as out_pdf_file:
                        pdf_writer.write(out_pdf_file)

                        messages.success(request, 'Proprietário adicionado com sucesso!')
                        return redirect('lista_proprietarios')

            except ValidationError as e:
                error_message = f"Erro ao adicionar proprietário: {e}"
                messages.error(request, error_message)
                

                # If an error occurs, delete the owner to avoid inconsistent data
                proprietario.delete()
                return redirect('lista_proprietarios')

            except Exception as e:
                error_message = f"Erro ao adicionar proprietário: {e}"
                messages.error(request, error_message)
               

                # If an error occurs, delete the owner to avoid inconsistent data
                proprietario.delete()
                return redirect('lista_proprietarios')

        else:
            error_message = "Formulário inválido. Verifique os campos."
            messages.error(request, error_message)
            

    else:
        form = ProprietarioForm()

    return render(request, 'lista_proprietarios.html', {'form': form})


def deletar_proprietario(request, proprietario_id):
    proprietario = get_object_or_404(Proprietario, id=proprietario_id)
    try:
        proprietario.delete()
        messages.success(request, 'Proprietário deletado com sucesso!')
    except Exception as e:
        messages.error(request, f"Erro ao deletar proprietário: {e}")

    return redirect('lista_proprietarios')

def calcular_progresso(processo, processo_id, cliente):
    processo = get_object_or_404(Processo, id=processo_id, cliente=cliente)

    tipo_processo = TipoProcesso.objects.get(nome=processo.tipo)
    opcoes_disponiveis = [opcao.strip()
                          for opcao in tipo_processo.obter_opcoes()]
    opcoes_selecionadas = OpcaoSelecionada.objects.filter(processo=processo)

    if not opcoes_disponiveis:
        return 0

    progresso = len(opcoes_selecionadas) / len(opcoes_disponiveis) * 100
    return int(progresso)
def apply_filters(request, processos):
    tipo_filtro = request.GET.get('filtroTipo', '')
    responsavel_filtro = request.GET.get('filtroResponsaveis', '')
    progresso_filtro = request.GET.get('filtroProgresso', '')
    proprietario_filtro = request.GET.get('filtroProprietarios', '')
    filtro_opcoes = request.GET.get('filtroOpcoes', '')
    data_inicio = request.GET.get('dataInicio')
    data_fim = request.GET.get('dataFim')

    if tipo_filtro:
        processos = processos.filter(tipo__iexact=tipo_filtro)

    if responsavel_filtro:
        responsavel = CustomUser.objects.filter(id=responsavel_filtro).first()
        if responsavel:
            processos = processos.filter(responsaveis=responsavel)

    if progresso_filtro:
        if progresso_filtro == 'concluido':
            processos = processos.exclude(data_finalizacao__isnull=True)
        elif progresso_filtro == 'nao_concluido':
            processos = processos.filter(data_finalizacao__isnull=True)

    if proprietario_filtro:
        proprietario = Proprietario.objects.filter(id=proprietario_filtro).first()
        if proprietario:
            processos = processos.filter(proprietario=proprietario)
        else:
            processos = Processo.objects.none()  # Retorna uma queryset vazia se o proprietário não for encontrado

    filtro_opcoes = request.GET.get('filtroOpcoes', '')
    if filtro_opcoes:
        # Subconsulta para obter a última opção selecionada para cada processo
        ultima_opcao_subquery = OpcaoSelecionada.objects.filter(processo=OuterRef('pk')).order_by('-id')[:1]
        
        # Filtrar os processos pela última opção selecionada
        processos = processos.annotate(ultima_opcao=Subquery(ultima_opcao_subquery.values('opcao')))
        processos = processos.filter(ultima_opcao__icontains=filtro_opcoes)

    if data_inicio and data_fim:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        processos = processos.filter(Q(data_inicio__gte=data_inicio) & Q(data_inicio__lte=data_fim))

    return processos

def update_process_status(processos):
    for processo in processos:
        processo.progresso = int(calcular_progresso(processo, processo.id, processo.cliente))
        processo.num_notas = Nota_notification.objects.filter(processo=processo).count()
        processo.num_notas_nao_concluidas = Nota_notification.objects.filter(processo=processo, nova=True).count()
        if processo.cliente:
            processo.opcoes_selecionadas = OpcaoSelecionada.objects.filter(processo=processo)
            
            
            
def lista_processos(request):
    corretores_group = Group.objects.filter(name='Corretores').first()
    is_corretor = corretores_group and request.user.groups.filter(pk=corretores_group.pk).exists()

    if is_corretor:
        processos = Processo.objects.filter(responsaveis=request.user)
    else:
        processos = Processo.objects.all()

    # Adicionando progresso e contagem de notas aos processos
    for processo in processos:
        processo.progresso = int(calcular_progresso(processo, processo.id, processo.cliente))
        processo.num_notas = Nota_notification.objects.filter(processo=processo).count()
        processo.num_notas_nao_concluidas = Nota_notification.objects.filter(processo=processo, nova=True).count()
        if processo.cliente:
            processo.opcoes_selecionadas = OpcaoSelecionada.objects.filter(processo=processo)

    total_processos = processos.count()
    tipos_processo = TipoProcesso.objects.all()

    # Ordenando os processos pelo ID de forma decrescente
    
    filtro_opcoes = request.GET.get('filtroOpcoes', '')
    if filtro_opcoes:
        processos = processos.filter(opcaoselecionada__opcao__icontains=filtro_opcoes)

    opcoes_por_tipo_processo = {}

    tipo_filtro = request.GET.get('filtroTipo', '')
    responsavel_filtro = request.GET.get('filtroResponsaveis', '')
    progresso_filtro = request.GET.get('filtroProgresso', '')
    proprietario_filtro = request.GET.get('filtroProprietarios', '')

    if tipo_filtro:
        processos = processos.filter(tipo__iexact=tipo_filtro)

    if responsavel_filtro:
        responsavel = CustomUser.objects.filter(id=responsavel_filtro).first()
        if responsavel:
            processos = processos.filter(responsaveis=responsavel)

    if progresso_filtro:
        if progresso_filtro == 'concluido':
            processos = processos.exclude(data_finalizacao__isnull=True)
        elif progresso_filtro == 'nao_concluido':
            processos = processos.filter(data_finalizacao__isnull=True)

    if proprietario_filtro:
        proprietario = Proprietario.objects.filter(id=proprietario_filtro).first()
        if proprietario:
            processos = processos.filter(proprietario=proprietario)
        else:
            processos = Processo.objects.none()  # Retorna uma queryset vazia se o proprietário não for encontrado

    add_note_form = AddNoteForm()
    
    tipo_filtro = request.GET.get('tipo_processo', '')
    responsavel_filtro = request.GET.get('filtroResponsaveis', '')
    progresso_filtro = request.GET.get('progresso', '')
    proprietario_filtro = request.GET.get('proprietario', '')

    if tipo_filtro:
        processos = processos.filter(tipo__iexact=tipo_filtro)

    if responsavel_filtro:
        responsavel = CustomUser.objects.filter(id=responsavel_filtro).first()
        if responsavel:
            processos = processos.filter(responsaveis=responsavel)

    if progresso_filtro:
        if progresso_filtro == 'concluido':
            processos = processos.exclude(data_finalizacao__isnull=True)
        elif progresso_filtro == 'nao_concluido':
            processos = processos.filter(data_finalizacao__isnull=True)

    if proprietario_filtro:
        proprietario = Proprietario.objects.filter(id=proprietario_filtro).first()
        if proprietario:
            processos = processos.filter(proprietario=proprietario)
        else:
            processos = Processo.objects.none()

    clientes = Cliente.objects.all().order_by('nome')
    total_contatos = clientes.count()

    proprietarios = Proprietario.objects.all().order_by('nome')

    imoveis_disponiveis = Imovel.objects.all()
    data_inicio = request.GET.get('dataInicio')
    data_fim = request.GET.get('dataFim')
    processos = apply_filters(request, processos)

        # Atualizar o status dos processos com base nos filtros aplicados
    update_process_status(processos)
    if data_inicio and data_fim:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        processos = processos.filter(Q(data_inicio__gte=data_inicio) & Q(data_inicio__lte=data_fim))

    if request.method == "POST":
        form = ProcessoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Processo editado com sucesso.')

    # Se o processo_id e o cliente_id não estiverem vazios, redirecione para a página 'nova_nota'
    processo_id = request.GET.get('processo_id', None)
    cliente_id = request.GET.get('cliente_id', None)
    if processo_id and cliente_id:
        # Certifique-se de importar a função 'redirect' do Django
        return redirect('nova_nota', cliente_id=cliente_id, processo_id=processo_id)

    # Se o método de requisição for POST e o formulário for válido, salve o processo e redirecione para a mesma página
    if request.method == "POST":
        form = ProcessoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Processo editado com sucesso.')
            return redirect('lista_processos')  # Redireciona para a mesma página
    opcoes_unicas = set()
    for processo in processos:
        opcoes_selecionadas = OpcaoSelecionada.objects.filter(processo=processo)
        for opcao in opcoes_selecionadas:
                opcoes_unicas.add(opcao.opcao)

    opcoes_por_tipo_processo_json = json.dumps(opcoes_por_tipo_processo)
    order_of_options = ['Pendente', 'Conformidade', 'Conforme', 'Inconforme', 'Emissão de minuta', 'Contrato assinado', 'Aguardando Comissão', 'Entrega de chaves', 'Aguardando Laudo', 'Cartório', 'Finalizado']

    sorted_processos = sorted(processos, key=lambda p: order_of_options.index(p.opcoes_selecionadas.last().opcao) if p.opcoes_selecionadas.exists() and p.opcoes_selecionadas.last().opcao in order_of_options else len(order_of_options))

    return render(request, 'processos.html', {
        'processos': sorted_processos,
        'total_processos': total_processos,
        'tipos_processo': tipos_processo,        
        'clientes': clientes,
        'opcoes_unicas': opcoes_unicas,
        'total_contatos': total_contatos,
        'corretores': corretores_group.user_set.all() if corretores_group else [],
        'username': request.user.username,
        'proprietarios': proprietarios,
        'opcoes_por_tipo_processo_json': opcoes_por_tipo_processo_json,
        'imoveis_disponiveis': imoveis_disponiveis,
    })
    

def alterar_opcao(request, processo_id, opcao_id):
    processo = Processo.objects.get(pk=processo_id)
    opcao_selecionada = OpcaoSelecionada.objects.get(pk=opcao_id)

    # Atualizar a opção selecionada para o processo
    processo.opcoes_selecionadas.clear()
    processo.opcoes_selecionadas.add(opcao_selecionada)

    return JsonResponse({'success': True})

from django.core.exceptions import ValidationError

@login_required
def add_processo(request):
    clientes = Cliente.objects.all()
    tipos_processo = TipoProcesso.objects.all()
    proprietarios = Proprietario.objects.all()
    corretores = Corretores.objects.all()

    # Move esta linha aqui para garantir que os imóveis sejam carregados antes
    imoveis_disponiveis = Imovel.objects.all()

    if request.method == "POST":
        cliente_id = request.POST.get('cliente')
        cliente_instance = Cliente.objects.get(id=cliente_id)

        # Altere o nome do campo para 'tipo'
        tipo_nome = request.POST.get('tipo')
        tags = request.POST.get('tags')
        responsaveis_ids = request.POST.getlist('responsaveis')
        # Obtendo o objeto Corretores com base no ID
        responsaveis_instances = Corretores.objects.filter(id__in=responsaveis_ids)

        data_inicio_str = request.POST.get('data_inicio')
        data_finalizacao_str = request.POST.get('data_finalizacao')

        # Convertendo strings para objetos de data
        data_inicio = datetime.strptime(
            data_inicio_str, '%Y-%m-%d').date() if data_inicio_str else None
        data_finalizacao = datetime.strptime(
            data_finalizacao_str, '%Y-%m-%d').date() if data_finalizacao_str else None

        # Verificar se o tipo de processo já existe
        tipo_processo, created = TipoProcesso.objects.get_or_create(
            nome=tipo_nome)

        # Adicione a obtenção do proprietário
        proprietario_id = request.POST.get('proprietario')
        proprietario_instance = Proprietario.objects.get(id=proprietario_id)     

        # Crie o processo incluindo o proprietário
        processo = Processo.objects.create(
            cliente=cliente_instance,
            tipo=tipo_processo,
            tags=tags,            
            data_inicio=data_inicio,
            data_finalizacao=data_finalizacao,
            proprietario=proprietario_instance,  # Adicione o proprietário aqui
          
        )
        processo.responsaveis.set(responsaveis_instances)

        # Adicione esta linha para vincular os imóveis ao processo
        imoveis_selecionados = request.POST.getlist('imoveis')
        processo.imoveis.set(imoveis_selecionados)
        
        

        # Movido para dentro do bloco 'if' para garantir que o processo seja criado apenas se o arquivo for anexado
        return redirect('lista_processos')

    return render(request, 'processo.html', {'clientes': clientes, 'tipos_processo': tipos_processo, 'proprietarios': proprietarios, 'corretores': corretores, 'imoveis_disponiveis': imoveis_disponiveis})
@login_required
def cliente_processo(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    processos = Processo.objects.filter(cliente=cliente)

    return render(
        request,
        'cliente_processo.html',
        {
            'cliente': cliente,
            'processos': processos,
            'username': request.user.username
        }
    )



def error_404_view(request, exception):
    return render(request, '404.html', {}, status=404)

def deletar_processo(request, processo_id):
    processo = get_object_or_404(Processo, id=processo_id)

    if request.method == 'POST':
        processo.delete()
        return redirect('lista_processos')  # Certifique-se de que está correto

    return render(request, 'processos.html', {'processo': processo})





def debug_csrf(request):
    csrf_token = request.META.get("CSRF_COOKIE")
    return JsonResponse({"csrf_token": csrf_token})

from django.utils.timezone import now
@login_required
def detalhes_do_processo(request, cliente_id, processo_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    processo = get_object_or_404(Processo, id=processo_id, cliente=cliente)

    tipo_processo = TipoProcesso.objects.get(nome=processo.tipo)
    opcoes_disponiveis = [opcao.strip() for opcao in tipo_processo.obter_opcoes()]
    opcoes_selecionadas = OpcaoSelecionada.objects.filter(processo=processo)

    opcoes_selecionadas_list = [(opcao.opcao.strip(), opcao.data_selecionada.strftime('%d/%m/%Y')) for opcao in opcoes_selecionadas]
    opcoes_selecionadas_dict = {opcao.opcao.strip(): opcao.data_selecionada.strftime('%d/%m/%Y') for opcao in opcoes_selecionadas}

    if request.method == "POST":
        form = OpcoesForm(request.POST, tipos_processo=[tipo_processo], opcoes_selecionadas=opcoes_selecionadas)
        if form.is_valid():
            opcao_selecionada = form.cleaned_data['opcoes_processo']  # Opção selecionada
            OpcaoSelecionada.objects.filter(cliente=cliente, processo=processo, tipo_processo=tipo_processo).delete()
            ultima_opcao_selecionada = opcao_selecionada[-1] if opcao_selecionada else 'Nenhuma opção selecionada'
            
            for opcao in opcao_selecionada:
                opcao_obj, created = OpcaoSelecionada.objects.get_or_create(cliente=cliente, processo=processo, tipo_processo=tipo_processo, opcao=opcao)
                opcao_obj.data_selecionada = now()  # Define a data selecionada como a data atual
                opcao_obj.save()

            # Envie a notificação para os responsáveis do processo
            notification_text = f"Prezados, informamos que o processo do cliente *{cliente.nome}* foi atualizado com sucesso. A última ação registrada é: *'{ultima_opcao_selecionada}'*. Agradecemos a atenção e nos colocamos à disposição para quaisquer esclarecimentos adicionais."

            for corretor in processo.responsaveis.all():
                send_whatsapp_notification2(corretor, notification_text)

            # Após atualizar o processo com sucesso, redirecione para a lista de processos
            return redirect('lista_processos')
    else:
        form = OpcoesForm(tipos_processo=[tipo_processo], opcoes_selecionadas=opcoes_selecionadas)

    return render(request, 'cliente_processo.html', {
        'cliente': cliente,
        'processo': processo,
        'tipo_processo': tipo_processo,
        'form': form,
        'opcoes_selecionadas': opcoes_selecionadas,
        'opcoes_selecionadas_list': opcoes_selecionadas_list,
        'opcoes_selecionadas_dict': opcoes_selecionadas_dict,
        'opcoes_disponiveis': opcoes_disponiveis,
        'cliente_id': cliente.id,
        'processo_id': processo.id,
        'username': request.user.username
    })

@login_required
def nova_nota_view(request, cliente_id, processo_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    processo = get_object_or_404(Processo, pk=processo_id)

    if request.method == 'POST':
        note_recipient = request.POST.get('note_recipient')
        note_text = request.POST.get('note_text')
        
        Nota_notification.objects.create(
            cliente=cliente,
            processo=processo,
            destinatario=note_recipient,
            texto=note_text
        )

        if note_recipient == 'owner':
            proprietario = processo.proprietario
            send_whatsapp_notification(proprietario, note_text, cliente.id)  # Passando cliente.id
        elif note_recipient == 'broker':
            for corretor in processo.responsaveis.all():
                send_whatsapp_notification(corretor, note_text, cliente.id)  # Passando cliente.id

        return redirect('nova_nota', cliente_id=cliente.id, processo_id=processo.id)

    return render(request, 'processos.html', {'cliente': cliente, 'processo': processo})






def send_whatsapp_notification(corretor, note_text, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    whatsapp_num = f"{corretor.telefone}@c.us"
    message = f'Nova nota adicionada ao processo do cliente {cliente.nome}: {note_text}'


    payload = {
        'number': whatsapp_num,
        'message': message
    }

    response = requests.post(
        'http://localhost:5000/send-message', json=payload)

    if not response.json().get('success'):
        error_message = response.json().get('error', 'Unknown error')
        raise Exception(f"Failed to send WhatsApp notification due to: {error_message}")

    
def send_whatsapp_notification2(destinatario, notification_text):
    whatsapp_num = f"{destinatario.telefone}@c.us"
  
    message = notification_text  # Usar a mensagem fornecida

    payload = {
        'number': whatsapp_num,
        'message': message
    }

    response = requests.post(
        'http://localhost:5000/send-message', json=payload)

    if not response.json().get('success'):
        error_message = response.json().get('error', 'Unknown error')
        raise Exception(f"Failed to send WhatsApp notification due to: {error_message}")
    
def nota_visu(request):
    processos = Processo.objects.all()

    for processo in processos:
        processo.has_notas = processo.has_notas()

    return render(request, 'processo.html', {'processos': processos})

def excluir_nota_notification(request, nota_id):
    nota_notification = get_object_or_404(Nota_notification, id=nota_id)
    nota_notification.delete()

    # Redireciona de volta para a página atual
    return redirect(request.META.get('HTTP_REFERER'))


@require_POST
def finalizar_processo(request, processo_id):
    if request.method == "POST":
        
        processo = get_object_or_404(Processo, pk=processo_id)
        processo.data_finalizacao = timezone.now()
        
        processo.save()
        

        return redirect('lista_processos')  # Altere 'lista_processos' para o nome correto da sua URL de listagem
    else:
        return redirect('lista_processos')


def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            # Redirecione ou faça algo após salvar as alterações.
    else:
        form = ClienteForm(instance=cliente)

    notas = Nota.objects.filter(cliente=cliente)
    
    # Verificar se há uma nova nota adicionada
    nova_nota = Nota.objects.filter(cliente=cliente, nova=True).last()
    if nova_nota:
        corretor = cliente.corretor  # Pegar o corretor do cliente
        mensagem = f"Nova nota adicionada para o cliente: {cliente.nome}.\nDetalhes da nota: *{nova_nota.texto}*"
        send_notification_to_corretor_mensagem_personalizada(corretor, mensagem)  # Enviar notificação para o corretor

        # Marcar a nota como não nova após enviar a notificação
        nova_nota.nova = False
        nova_nota.save()

    return render(request, 'editar_cliente.html', {'form': form, 'cliente': cliente, 'notas': notas})





def converter_e_anexar_para_pdf(arquivos, pdf_path):
    pdf_writer = PdfWriter()
    
    for arquivo_path in arquivos:
        if arquivo_path.lower().endswith('.pdf'):
            anexar_pdf(arquivo_path, pdf_writer)
        else:
            imagem_para_pdf_e_anexar(arquivo_path, pdf_writer)
    
    # Escreve no PDF final, assegurando que o arquivo é fechado após a escrita
    with open(pdf_path, 'wb') as out:
        pdf_writer.write(out)

def imagem_para_pdf_e_anexar(imagem_path, pdf_writer):
    imagem = Image.open(imagem_path)
    if imagem.mode != "RGB":
        imagem = imagem.convert("RGB")
    imagem_pdf_path = imagem_path.replace('.png', '.pdf').replace('.jpg', '.pdf').replace('.jpeg', '.pdf')
    imagem.save(imagem_pdf_path)
    anexar_pdf(imagem_pdf_path, pdf_writer)
    os.remove(imagem_pdf_path)  # Remove o arquivo PDF temporário criado a partir da imagem

def anexar_pdf(novo_pdf_path, pdf_writer):
    with open(novo_pdf_path, 'rb') as novo_pdf_file:
        novo_pdf = PdfReader(novo_pdf_file)
        for pagina_num in range(len(novo_pdf.pages)):
            pdf_writer.add_page(novo_pdf.pages[pagina_num])

def editar_proprietario(request, proprietario_id):
    proprietario = get_object_or_404(Proprietario, id=proprietario_id)
    if request.method == 'POST':
        form = ProprietarioEditForm(request.POST, request.FILES, instance=proprietario)
        
        # Verifica se pelo menos um campo do formulário (exceto o campo de documentação) foi preenchido
        if any(request.POST.get(field) for field in form.fields if field != 'documentacao'):
            
            if form.is_valid():
                
                proprietario = form.save(commit=False)
                if 'documentacao' in request.FILES:
                    
                    documentacao_nome = f"{proprietario.nome}_{proprietario.cpf_cnpj}.pdf"
                    documentacao_path = os.path.join("media", "proprietario", proprietario.nome)
                    os.makedirs(documentacao_path, exist_ok=True)
                    documentacao_pdf_path = os.path.join(documentacao_path, documentacao_nome)
                    
                    arquivos_path = []
                    for arquivo in request.FILES.getlist('documentacao'):
                        arquivo_path = os.path.join(documentacao_path, arquivo.name)
                        arquivos_path.append(arquivo_path)
                        with open(arquivo_path, 'wb+') as destination:
                            for chunk in arquivo.chunks():
                                destination.write(chunk)
                    
                    # Converter e anexar todos os arquivos para um único PDF
                    converter_e_anexar_para_pdf(arquivos_path, documentacao_pdf_path)
                    
                    # Remover os arquivos originais após a conversão e anexação
                    for arquivo_path in arquivos_path:
                        os.remove(arquivo_path)
                    
                # Salvar o proprietário somente após as operações relacionadas à documentação
                proprietario.save()
                
                return HttpResponseRedirect(reverse('editar_proprietario', kwargs={'proprietario_id': proprietario_id}))
            else:
                
                return JsonResponse({'status': 'error', 'message': 'Formulário inválido.', 'errors': form.errors}, status=400)
        else:
            # Se nenhum campo (exceto o campo de documentação) foi preenchido, redireciona sem fazer nada
            
            return HttpResponseRedirect(reverse('editar_proprietario', kwargs={'proprietario_id': proprietario_id}))
    else:
        form = ProprietarioEditForm(instance=proprietario)
    return render(request, 'editar_proprietario.html', {'form': form, 'proprietario': proprietario})




def visualizar_documentacao(request, proprietario_id):
    proprietario = get_object_or_404(Proprietario, id=proprietario_id)
    documentacao_path = os.path.join("media", "proprietario", proprietario.nome)
    documentacao_nome = f"{proprietario.nome}_{proprietario.cpf_cnpj}.pdf"
    documentacao_url = os.path.join(documentacao_path, documentacao_nome)
    
    # Verifica se o arquivo de documentação existe
    if os.path.exists(documentacao_url):
        with open(documentacao_url, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="documento.pdf"'
            return response
    else:
        return HttpResponse("Documento de documentacao não encontrado.", status=404)
    
@login_required
def upload_video(request):
    if not request.user.is_staff:
        return redirect('404')

    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_video')
    else:
        form = VideoForm()

    return render(request, 'upload_video.html', {'form': form})

def assistir_videos(request):
    videos = Video.objects.all()

    # Verificar quais vídeos o usuário já assistiu
    user_viewed_videos = VideoView.objects.filter(user=request.user).values_list('video__id', flat=True)

    context = {
        'videos': videos,
        'user_viewed_videos': user_viewed_videos,
    }

    return render(request, 'assistir_videos.html', context)

def delete_video(request):
    if request.method == 'POST' and request.user.is_staff:
        data = json.loads(request.body)
        video_id = data.get('video_id')
        video = get_object_or_404(Video, pk=video_id)
        video.delete()
        return JsonResponse({'message': 'Vídeo deletado com sucesso.'})
    return JsonResponse({'message': 'Erro ao deletar o vídeo.'}, status=400)

@csrf_exempt
def registrar_visualizacao(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        video_id = data.get('video_id')
        duration_watched = data.get('duration_watched')
        total_duration = data.get('total_duration')

        video = get_object_or_404(Video, pk=video_id)
        
        # Verificar se o usuário já assistiu a este vídeo
        if not VideoView.objects.filter(user=request.user, video=video).exists():
            VideoView.objects.create(user=request.user, video=video, duration_watched=duration_watched, total_duration=total_duration)

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})

import emoji
from django.utils.html import escape

logger = logging.getLogger(__name__)

def adicionar_imovel(request):
    if request.method == 'POST':
        form = ImovelForm(request.POST, request.FILES)
        if form.is_valid():
            exclusivo = request.POST.get('exclusivo') == 'sim'
            tem_inquilino = request.POST.get('tem_inquilino') == 'sim'

            # Salva o imóvel sem commit para poder adicionar as tags posteriormente
            imovel = form.save(commit=False)
            imovel.exclusivo = exclusivo
            imovel.tem_inquilino = tem_inquilino
            imovel.situacao_do_imovel = request.POST.get('situacao_do_imovel')

            # Trata emojis na descrição do imóvel
            descricao = request.POST.get('descricao')
            if descricao:
                descricao = emoji.demojize(descricao)  # Converte emojis para sua representação textual
            imovel.descricao = descricao
            
            imovel.save()

            # Verifica se uma imagem de capa foi fornecida
            if 'imagem_de_capa' in request.FILES:
                capa = request.FILES['imagem_de_capa']
                try:
                    imovel.imagem_de_capa = capa
                    imovel.save()
                except Exception as e:
                    logger.error(f"Erro ao salvar a imagem de capa: {e}")
                    messages.error(request, f"Erro ao salvar a imagem de capa: {e}")

            # Itera sobre as imagens e as adiciona ao imóvel
            for imagem in request.FILES.getlist('imagens'):
                try:
                    imovel.imagens.create(imagem=imagem)
                except Exception as e:
                    logger.error(f"Erro ao salvar a imagem: {e}")
                    messages.error(request, f"Erro ao salvar a imagem: {e}")

            # Adiciona as tags selecionadas
            try:
                tags = form.cleaned_data['tags']
                imovel.tags.set(tags)
                imovel.save()
            except Exception as e:
                logger.error(f"Erro ao salvar as tags: {e}")
                messages.error(request, f"Erro ao salvar as tags: {e}")

            messages.success(request, 'Imóvel cadastrado com sucesso.')  # Adiciona mensagem de sucesso
            return redirect(request.path_info)  # Redireciona para a mesma página (recarregar a página)
        else:
            # Se o formulário for inválido, exibe os erros
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Erro no campo "{field}": {error}')
            return redirect(request.path_info)  # Redireciona para a mesma página para mostrar os erros
    else:
        form = ImovelForm()

    return render(request, 'adicionar_imovel.html', {'form': form})



def lista_imoveis(request):
    # Buscar todos os imóveis do banco de dados
    imoveis = Imovel.objects.all()

    # Passar a lista de imóveis como contexto para o template
    context = {'imoveis': imoveis}
    
    return render(request, 'lista_imoveis.html', context)

def download_imagens_view(request, imovel_id):
    imovel = get_object_or_404(Imovel, id=imovel_id)

    # Verifica se o imóvel tem imagens
    if not imovel.imagens.exists():
        return HttpResponse("O imóvel não possui imagens para baixar.")

    # Cria um arquivo zip temporário
    zip_filename = f"imagens_imovel_{imovel_id}.zip"
    zip_filepath = os.path.join(settings.MEDIA_ROOT, zip_filename)

    with zipfile.ZipFile(zip_filepath, 'w') as zip_file:
        # Itera sobre as imagens do imóvel e adiciona ao arquivo zip
        for imagem in imovel.imagens.all():
            img_path = os.path.join(settings.MEDIA_ROOT, str(imagem.imagem))
            zip_file.write(img_path, os.path.basename(img_path))

    # Envia o arquivo zip como resposta
    with open(zip_filepath, 'rb') as zip_file:
        response = HttpResponse(zip_file.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
        return response
    
@user_passes_test(lambda u: u.is_staff, login_url='login')
def excluir_imovel(request, imovel_id):
    imovel = get_object_or_404(Imovel, id=imovel_id)
    
    if request.method == 'POST':
        imovel.delete()
        messages.success(request, 'Imóvel excluído com sucesso.')  # Adiciona a mensagem de sucesso
    
        # Redireciona para alguma página após a exclusão, como a lista de imóveis
    return redirect('lista_imoveis')  # Substitua 'nome_da_view' pelo nome da view para a lista de imóveis
    
    



# views.py

def editar_pdf(request, cliente_id, tipo_documento):
    # Obter o objeto cliente ou retornar 404 se não encontrado
    cliente = get_object_or_404(Cliente, id=cliente_id)

    # Mapeamento dos tipos de documentos para suas respectivas subpastas
    tipos_documentos = {
        'pessoais': 'documentos_pessoais',
        'extrato': 'extrato_bancario',
        'dependente': 'documentos_dependente'
    }

    # Obter a subpasta apropriada a partir do tipo de documento, default para 'Documentos_pessoais'
    subpasta = tipos_documentos.get(tipo_documento, 'documentos_pessoais')
    # Construir o caminho completo para o arquivo PDF
    pdf_path = os.path.join('media', 'documentos', cliente.corretor.username, cliente.cpf, subpasta, f'{subpasta}_combined.pdf')

    # Inicialização de variáveis para o contexto
    num_paginas = 0
    pagina_numeros = []

    # Verificar se o arquivo PDF existe antes de tentar abri-lo
    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            num_paginas = len(pdf_reader.pages)
            pagina_numeros = list(range(1, num_paginas + 1))
    

    # Contexto para ser usado no template
    context = {
        'cliente_id': cliente_id,
        'num_paginas': num_paginas,
        'pdf_path': pdf_path,
        'pagina_numeros': pagina_numeros,
        'tipo_documento': tipo_documento,
    }

    # Renderizar o template com o contexto
    return render(request, 'editar_pdf.html', context)


def visualizar_pagina_pdf(request, cliente_id, pagina_numero, tipo_documento):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    tipos_documentos = {
        'pessoais': 'documentos_pessoais',
        'extrato': 'extrato_bancario',
        'dependente': 'documentos_dependente'
    }

    subpasta = tipos_documentos.get(tipo_documento, 'documentos_pessoais')
    pdf_path = f'media/documentos/{cliente.corretor.username}/{cliente.cpf}/{subpasta}/{subpasta}_combined.pdf'

    # Verificar se o arquivo PDF existe
    if not os.path.exists(pdf_path):
        return HttpResponse("PDF não encontrado", status=404)

    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)

        # Verificar se o número da página é válido
        if pagina_numero < 1 or pagina_numero > len(pdf_reader.pages):
            return HttpResponse("Página não encontrada", status=404)

        pagina = pdf_reader.pages[pagina_numero - 1]
        pdf_writer = PdfWriter()
        pdf_writer.add_page(pagina)

        response = HttpResponse(content_type='application/pdf')
        pdf_writer.write(response)

    return response

def deletar_pagina_pdf(request, cliente_id, pagina_numero,tipo_documento):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    tipos_documentos = {
        'pessoais': 'documentos_pessoais',
        'extrato': 'extrato_bancario',
        'dependente': 'documentos_dependente'
    }

    subpasta = tipos_documentos.get(tipo_documento, 'documentos_pessoais')

    # Caminho do arquivo PDF
    pdf_path = f'media/documentos/{cliente.corretor.username}/{cliente.cpf}/{subpasta}/{subpasta}_combined.pdf'

    # Carregar o PDF
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)

        # Criar um novo PDF sem a página desejada
        pdf_writer = PdfWriter()
        for i, page in enumerate(pdf_reader.pages):
            if i + 1 != pagina_numero:
                pdf_writer.add_page(page)

        # Salvar o novo PDF
        with open(pdf_path, 'wb') as output_file:
            pdf_writer.write(output_file)

    return redirect('editar_pdf', cliente_id=cliente_id, tipo_documento=tipo_documento)


def lista_contratos(request):
    contratos = Contrato.objects.all()
    return render(request, 'lista_contratos.html', {'contratos': contratos})

def adicionar_contrato(request):
    if request.method == 'POST':
        form = ContratoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_contratos')
    else:
        form = ContratoForm()
    return render(request, 'adicionar_contrato.html', {'form': form})

def editar_contrato(request, contrato_id):
    contrato = Contrato.objects.get(pk=contrato_id)
    if request.method == 'POST':
        form = ContratoForm(request.POST, request.FILES, instance=contrato)
        if form.is_valid():
            form.save()
            return redirect('lista_contratos')
    else:
        form = ContratoForm(instance=contrato)
    return render(request, 'editar_contrato.html', {'form': form, 'contrato': contrato})

def excluir_contrato(request, contrato_id):
    try:
        contrato = Contrato.objects.get(id=contrato_id)
        contrato.delete()
        # Redirecionar para a página de lista de contratos após a exclusão
        return redirect('lista_contratos')
    except Contrato.DoesNotExist:
        # Lógica para lidar com o contrato não encontrado, por exemplo, exibir uma mensagem de erro
        pass
    
def download_contrato(request, contrato_id):
    contrato = get_object_or_404(Contrato, id=contrato_id)
    
    # Verifique se o contrato possui um arquivo associado
    if contrato.arquivo:
        # Configurar a resposta HTTP para o download
        response = HttpResponse(contrato.arquivo, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{contrato.arquivo.name}"'
        return response
    else:
        raise Http404("Contrato não encontrado")
    
from django.shortcuts import redirect

@login_required
def editar_processo(request, processo_id):
    processo = get_object_or_404(Processo, id=processo_id)
    if request.method == "POST":
        form = EditarProcessoForm(request.POST, instance=processo)
        if form.is_valid():
            form.save()
            # Redirecionar o usuário de volta para a página de detalhes do processo após a edição
            return redirect('editar_processo', processo_id=processo_id)
    else:
        form = EditarProcessoForm(instance=processo)
    return render(request, 'editar_processo.html', {'form': form})


def editar_imovel(request, imovel_id):
    imovel = get_object_or_404(Imovel, pk=imovel_id)
    if request.method == 'POST':
        form = ImovelForm(request.POST, request.FILES, instance=imovel)
        if form.is_valid():
            form.save()
            return redirect('lista_imoveis')
    else:
        form = ImovelForm(instance=imovel)
    tags = Tag.objects.all()  # Retrieve all tags from the database
    return render(request, 'editar_imovel.html', {'form': form, 'tags': tags})


def marketing_view(request):
    materiais = MaterialDeMarketing.objects.all()
    return render(request, 'marketing.html', {'materiais': materiais})

def adicionar_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('marketing')
    else:
        form = MaterialForm()
    return render(request, 'marketing.html', {'form': form})

def excluir_material(request, material_id):
    material = MaterialDeMarketing.objects.get(pk=material_id)
    if request.method == 'POST':
        material.delete()
        return redirect('marketing')
    return render(request, 'marketing.html', {'material': material})

def relatorio_clientes(request):
    clientes = Cliente.objects.all()

    # Aplicar filtros
    status_filter = request.GET.get('status')
    if status_filter:
        clientes = clientes.filter(status=status_filter)

    data_inicio_filter = request.GET.get('data_inicio')
    data_fim_filter = request.GET.get('data_fim')
    if data_inicio_filter and data_fim_filter:
        clientes = clientes.filter(data_de_criacao__range=[data_inicio_filter, data_fim_filter])

    corretor_filter = request.GET.get('corretor')
    if corretor_filter:
        clientes = clientes.filter(corretor__pk=corretor_filter)

    # Obter todos os corretores
    corretores = CustomUser.objects.filter(groups__name='Corretores')

    # Calcular estatísticas
    total_clientes = clientes.count()
    clientes_aprovados = clientes.filter(status='cliente_aprovado').count()
    clientes_reprovados = clientes.filter(status='reprovado').count()

    # Obter a data de início e de fim para este mês
    hoje = timezone.now().date()
    primeiro_dia_mes = hoje.replace(day=1)
    ultimo_dia_mes = primeiro_dia_mes.replace(day=28) + timedelta(days=4)
    ultimo_dia_mes = ultimo_dia_mes - timedelta(days=ultimo_dia_mes.day)

    # Filtrar os clientes criados este mês
    clientes_mes = clientes.filter(data_de_criacao__range=[primeiro_dia_mes, ultimo_dia_mes])

    # Contar o número de clientes criados este mês
    novos_clientes_mes = clientes_mes.count()
    processos_em_aberto = Processo.objects.filter(data_finalizacao__isnull=True).count()
    clientes_aguardando_aprovacao = clientes.filter(status='aguardando_aprovacao').count()
    clientes_documentacao_pendente = clientes.filter(status='documentacao_pendente').count()
    clientes_aguardando_cancelamento_qv = clientes.filter(status='aguardando_cancelamento_qv').count()
    clientes_cliente_aprovado = clientes.filter(status='cliente_aprovado').count()
    clientes_reprovado = clientes.filter(status='reprovado').count()
    clientes_proposta_apresentada = clientes.filter(status='proposta_apresentada').count()
    clientes_visita_efetuada = clientes.filter(status='visita_efetuada').count()
    clientes_nao_deu_continuidade = clientes.filter(status='nao_deu_continuidade').count()
    clientes_venda_concluida = clientes.filter(status='venda_concluida').count()
    clientes_fechamento_proposta = clientes.filter(status='fechamento_proposta').count()

    contexto = {
    'clientes': clientes,
    'total_clientes': total_clientes,
    'clientes_aprovados': clientes_aprovados,
    'clientes_reprovados': clientes_reprovados,
    'novos_clientes_mes': novos_clientes_mes,
    'processos_em_aberto': processos_em_aberto,
    'clientes_aguardando_aprovacao': clientes_aguardando_aprovacao,
    'clientes_documentacao_pendente': clientes_documentacao_pendente,
    'clientes_aguardando_cancelamento_qv': clientes_aguardando_cancelamento_qv,
    'clientes_cliente_aprovado': clientes_cliente_aprovado,
    'clientes_reprovado': clientes_reprovado,
    'clientes_proposta_apresentada': clientes_proposta_apresentada,
    'clientes_visita_efetuada': clientes_visita_efetuada,
    'clientes_nao_deu_continuidade': clientes_nao_deu_continuidade,
    'clientes_venda_concluida': clientes_venda_concluida,
    'clientes_fechamento_proposta': clientes_fechamento_proposta,
    'corretores': corretores,  # Passar os corretores para o template
}

    return render(request, 'relatorio_clientes.html', contexto)

def relatorio_clientes_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_clientes.pdf"'

    # Obtendo os clientes com os filtros aplicados
    status_filter = request.GET.get('status')
    data_inicio_filter = request.GET.get('data_inicio')
    data_fim_filter = request.GET.get('data_fim')
    corretor_filter = request.GET.get('corretor')

    clientes = Cliente.objects.all()
    if status_filter:
        clientes = clientes.filter(status=status_filter)
    if data_inicio_filter and data_fim_filter:
        clientes = clientes.filter(data_de_criacao__range=[data_inicio_filter, data_fim_filter])
    if corretor_filter:
        clientes = clientes.filter(corretor__pk=corretor_filter)

    # Preparando os dados para o relatório
    data = []
    for cliente in clientes:
        corretor_nome = f"{cliente.corretor.first_name} {cliente.corretor.last_name}" if cliente.corretor else ""
        data.append([
            cliente.nome,
            cliente.email,
            cliente.telefone,
            corretor_nome,
            cliente.get_status_display(),
            cliente.data_de_criacao.strftime("%d/%m/%Y") if cliente.data_de_criacao else ""
        ])

    # Calculando a largura das colunas com base no conteúdo mais longo de cada coluna
    column_widths = []
    for row in data:
        for i, value in enumerate(row):
            if len(column_widths) <= i:
                column_widths.append(len(str(value)))
            else:
                column_widths[i] = max(column_widths[i], len(str(value)))

    # Adicionando um padding para melhor legibilidade
    column_widths = [w * 5 for w in column_widths]

    # Criando o documento PDF
    doc = SimpleDocTemplate(response, pagesize=landscape(letter))

    # Criando a tabela com os dados
    table = Table(data, colWidths=column_widths)

    # Estilizando a tabela
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),  # Tamanho da fonte definido como 8
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)

    # Adicionando a tabela ao documento
    doc.build([table])

    return response
