from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView

from .forms import ( CadastroClienteForm, LanchaForm, LembreteForm, PerfilForm, ReservaForm, FuncionarioForm )
from .models import ImagemGaleria, Lancha, Lembrete, Notificacao, Perfil, Reserva


def eh_admin(user):
    return user.is_authenticated and (
        user.is_superuser or
        getattr(user.perfil, 'tipo', '') == Perfil.TIPO_ADMIN
    )


def eh_equipe(user):
    return user.is_authenticated and (
        user.is_staff
        or getattr(user.perfil, 'tipo', '') in [
            Perfil.TIPO_ADMIN,
            Perfil.TIPO_FUNCIONARIO
        ]
    )


def home(request):
    lanchas = Lancha.objects.filter(status=Lancha.STATUS_ATIVA)[:3]
    galeria = ImagemGaleria.objects.filter(publicada=True)[:6]
    return render(request, 'core/home.html', {'lanchas': lanchas, 'galeria': galeria})


class CadastroClienteView(CreateView):
    form_class = CadastroClienteForm
    template_name = 'registration/cadastro.html'

    def form_valid(self, form):
        self.object = form.save()

        login(self.request, self.object)
        messages.success(self.request, 'Conta criada com sucesso. Boas-vindas!')

        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return redirect(next_url)

        return render(
            self.request,
            'registration/cadastro_sucesso.html',
            {
                'usuario': self.object.username
            }
        )

@login_required
def funcionario_criar(request):

    if request.user.perfil.tipo != Perfil.TIPO_ADMIN:
        messages.error(
            request,
            'Você não possui permissão.'
        )
        return redirect('dashboard')

    if request.method == 'POST':

        form = FuncionarioForm(request.POST)

        if form.is_valid():

            usuario = User.objects.create_user(
            username=form.cleaned_data['email'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data.get('last_name', '')
            )

            usuario.perfil.tipo = Perfil.TIPO_FUNCIONARIO
            usuario.perfil.save()

            messages.success(
                request,
                'Funcionário cadastrado com sucesso.'
            )

            return redirect('dashboard')

    else:
        form = FuncionarioForm()

    return render(
        request,
        'core/form.html',
        {
            'form': form,
            'titulo': 'Cadastrar Funcionário'
        }
    )
@login_required
def dashboard(request):
    perfil = request.user.perfil
    hoje = date.today()
    if perfil.tipo == Perfil.TIPO_CLIENTE:
        reservas = Reserva.objects.filter(cliente=request.user)
    else:
        reservas = Reserva.objects.all()

    contexto = {
        'total_reservas': reservas.count(),
        'reservas_hoje': reservas.filter(data=hoje).count(),
        'reservas_pendentes': reservas.filter(status=Reserva.STATUS_PENDENTE).count(),
        'proximas_reservas': reservas.filter(data__gte=hoje).order_by('data', 'horario_inicio')[:8],
        'notificacoes': Notificacao.objects.filter(usuario=request.user, lida=False)[:5],
        'total_lanchas': Lancha.objects.count(),
        'total_clientes': User.objects.filter(perfil__tipo=Perfil.TIPO_CLIENTE).count(),
    }
    return render(request, 'core/dashboard.html', contexto)


@login_required
def perfil(request):
    form = PerfilForm(request.POST or None, instance=request.user.perfil, user=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Perfil atualizado com sucesso.')
        return redirect('perfil')
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Meu perfil'})


@login_required
def reservas(request):
    qs = Reserva.objects.select_related('cliente', 'lancha', 'criada_por')
    if request.user.perfil.tipo == Perfil.TIPO_CLIENTE:
        qs = qs.filter(cliente=request.user)

    status = request.GET.get('status')
    busca = request.GET.get('busca')
    if status:
        qs = qs.filter(status=status)
    if busca:
        qs = qs.filter(Q(cliente__first_name__icontains=busca) | Q(cliente__last_name__icontains=busca) | Q(lancha__nome__icontains=busca))

    return render(request, 'core/reservas.html', {'reservas': qs, 'status_choices': Reserva.STATUS_CHOICES})


@login_required
def reserva_criar(request):
    form = ReservaForm(request.POST or None, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        reserva = form.save()
        messages.success(request, 'Reserva criada com sucesso.')
        return redirect(reserva)
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Nova reserva'})


@login_required
def reserva_editar(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.user.perfil.tipo == Perfil.TIPO_CLIENTE and reserva.cliente != request.user:
        messages.error(request, 'Você não tem permissão para alterar esta reserva.')
        return redirect('reservas')
    form = ReservaForm(request.POST or None, instance=reserva, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Reserva atualizada com sucesso.')
        return redirect(reserva)
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Editar reserva'})


@login_required
def reserva_detalhe(request, pk):
    reserva = get_object_or_404(Reserva.objects.select_related('cliente', 'lancha', 'criada_por'), pk=pk)
    if request.user.perfil.tipo == Perfil.TIPO_CLIENTE and reserva.cliente != request.user:
        messages.error(request, 'Você não tem permissão para acessar esta reserva.')
        return redirect('reservas')
    return render(request, 'core/reserva_detalhe.html', {'reserva': reserva})


@login_required
def reserva_status(request, pk, status):
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.user.perfil.tipo == Perfil.TIPO_CLIENTE:
        if reserva.cliente != request.user or status != Reserva.STATUS_CANCELADA:
            messages.error(request, 'Ação não permitida.')
            return redirect('reservas')
    elif status not in dict(Reserva.STATUS_CHOICES):
        messages.error(request, 'Status inválido.')
        return redirect(reserva)
    reserva.status = status
    reserva.save(update_fields=['status', 'atualizada_em'])
    messages.success(request, 'Status da reserva atualizado.')
    return redirect(reserva)


@login_required
def calendario(request):
    inicio = date.today() - timedelta(days=7)
    fim = date.today() + timedelta(days=45)
    reservas_qs = Reserva.objects.filter(data__range=[inicio, fim]).select_related('lancha', 'cliente')
    if request.user.perfil.tipo == Perfil.TIPO_CLIENTE:
        reservas_qs = reservas_qs.filter(cliente=request.user)
    reservas_json = [
        {
            'title': f'{r.lancha.nome} - {r.cliente.get_full_name() or r.cliente.username}',
            'start': f'{r.data}T{r.horario_inicio}',
            'end': f'{r.data}T{r.horario_fim}',
            'status': r.get_status_display(),
            'url': r.get_absolute_url(),
        }
        for r in reservas_qs
    ]
    return render(request, 'core/calendario.html', {'reservas_json': reservas_json})


@login_required
def disponibilidade_api(request):
    lancha_id = request.GET.get('lancha')
    data_reserva = request.GET.get('data')
    inicio = request.GET.get('inicio')
    fim = request.GET.get('fim')
    conflitos = Reserva.objects.filter(
        lancha_id=lancha_id,
        data=data_reserva,
        status__in=[Reserva.STATUS_PENDENTE, Reserva.STATUS_APROVADA],
        horario_inicio__lt=fim,
        horario_fim__gt=inicio,
    ).exists()
    return JsonResponse({'disponivel': not conflitos})


@login_required
def lembretes(request):
    qs = Lembrete.objects.filter(usuario=request.user)
    return render(request, 'core/lembretes.html', {'lembretes': qs})


@login_required
def lembrete_criar(request):
    form = LembreteForm(request.POST or None, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Lembrete criado com sucesso.')
        return redirect('lembretes')
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Novo lembrete'})


@user_passes_test(eh_equipe)
def lanchas(request):
    return render(request, 'core/lanchas.html', {'lanchas': Lancha.objects.all()})


@user_passes_test(eh_admin)
def lancha_criar(request):
    form = LanchaForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Embarcação cadastrada com sucesso.')
        return redirect('lanchas')
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Nova embarcação'})


@user_passes_test(eh_equipe)
def clientes(request):
    clientes_qs = User.objects.filter(perfil__tipo=Perfil.TIPO_CLIENTE).annotate(total_reservas=Count('reservas_cliente'))
    return render(request, 'core/clientes.html', {'clientes': clientes_qs})


@user_passes_test(eh_admin)
def relatorios(request):
    reservas_por_status = Reserva.objects.values('status').annotate(total=Count('id'))
    reservas_por_origem = Reserva.objects.values('origem').annotate(total=Count('id'))
    return render(request, 'core/relatorios.html', {
        'reservas_por_status': reservas_por_status,
        'reservas_por_origem': reservas_por_origem,
    })


def redirecionar_usuario(usuario):

    if usuario.is_superuser:
        return redirect('dashboard')

    perfil = usuario.perfil

    if perfil.tipo == Perfil.TIPO_ADMIN:
        return redirect('dashboard')

    if perfil.tipo == Perfil.TIPO_FUNCIONARIO:
        return redirect('dashboard')

    return redirect('dashboard')
