from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class Perfil(models.Model):
    TIPO_CLIENTE = 'CLIENTE'
    TIPO_FUNCIONARIO = 'FUNCIONARIO'
    TIPO_ADMIN = 'ADMIN'

    TIPOS = [
        (TIPO_CLIENTE, 'Cliente'),
        (TIPO_FUNCIONARIO, 'Funcionário'),
        (TIPO_ADMIN, 'Administrador'),
    ]

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil'
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS,
        default=TIPO_CLIENTE
    )
    telefone = models.CharField(max_length=20, blank=True)
    documento = models.CharField(max_length=20, blank=True, help_text='CPF ou documento de identificação')
    endereco = models.CharField(max_length=255, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        nome = self.usuario.get_full_name() or self.usuario.username
        return f'{nome} - {self.get_tipo_display()}'


class Lancha(models.Model):
    STATUS_ATIVA = 'ATIVA'
    STATUS_MANUTENCAO = 'MANUTENCAO'
    STATUS_INATIVA = 'INATIVA'
    STATUS_CHOICES = [
        (STATUS_ATIVA, 'Ativa'),
        (STATUS_MANUTENCAO, 'Em manutenção'),
        (STATUS_INATIVA, 'Inativa'),
    ]

    nome = models.CharField(max_length=120)
    descricao = models.TextField()
    capacidade = models.PositiveIntegerField()
    preco_hora = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ATIVA)
    imagem = models.ImageField(upload_to='lanchas/', blank=True, null=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Lancha'
        verbose_name_plural = 'Lanchas'

    def __str__(self):
        return self.nome


class Reserva(models.Model):
    STATUS_PENDENTE = 'PENDENTE'
    STATUS_APROVADA = 'APROVADA'
    STATUS_CANCELADA = 'CANCELADA'
    STATUS_CONCLUIDA = 'CONCLUIDA'
    STATUS_CHOICES = [
        (STATUS_PENDENTE, 'Pendente'),
        (STATUS_APROVADA, 'Aprovada'),
        (STATUS_CANCELADA, 'Cancelada'),
        (STATUS_CONCLUIDA, 'Concluída'),
    ]

    ORIGEM_CLIENTE = 'CLIENTE'
    ORIGEM_FUNCIONARIO = 'FUNCIONARIO'
    ORIGEM_PRESENCIAL = 'PRESENCIAL'
    ORIGEM_TELEFONE = 'TELEFONE'
    ORIGEM_WHATSAPP = 'WHATSAPP'
    ORIGEM_CHOICES = [
        (ORIGEM_CLIENTE, 'Cliente'),
        (ORIGEM_FUNCIONARIO, 'Funcionário'),
        (ORIGEM_PRESENCIAL, 'Presencial'),
        (ORIGEM_TELEFONE, 'Telefone'),
        (ORIGEM_WHATSAPP, 'WhatsApp'),
    ]

    cliente = models.ForeignKey(User, on_delete=models.PROTECT, related_name='reservas_cliente')
    criada_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='reservas_criadas')
    lancha = models.ForeignKey(Lancha, on_delete=models.PROTECT, related_name='reservas')
    data = models.DateField()
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    quantidade_pessoas = models.PositiveIntegerField()
    origem = models.CharField(max_length=20, choices=ORIGEM_CHOICES, default=ORIGEM_CLIENTE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDENTE)
    observacoes = models.TextField(blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data', '-horario_inicio']
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self):
        return f'{self.lancha} - {self.cliente} em {self.data:%d/%m/%Y}'

    def get_absolute_url(self):
        return reverse('reserva_detalhe', args=[self.pk])

    def clean(self):
        if self.horario_inicio and self.horario_fim and self.horario_fim <= self.horario_inicio:
            raise ValidationError('O horário final deve ser maior que o horário inicial.')
        if self.lancha_id and self.quantidade_pessoas > self.lancha.capacidade:
            raise ValidationError('A quantidade de pessoas excede a capacidade da embarcação.')
        if self.lancha_id and self.data and self.horario_inicio and self.horario_fim:
            conflitos = Reserva.objects.filter(
                lancha=self.lancha,
                data=self.data,
                status__in=[self.STATUS_PENDENTE, self.STATUS_APROVADA],
                horario_inicio__lt=self.horario_fim,
                horario_fim__gt=self.horario_inicio,
            )
            if self.pk:
                conflitos = conflitos.exclude(pk=self.pk)
            if conflitos.exists():
                raise ValidationError('Já existe uma reserva para esta lancha neste intervalo.')


class Lembrete(models.Model):
    FREQUENCIA_UNICO = 'UNICO'
    FREQUENCIA_DIAS_ANTES = 'DIAS_ANTES'
    FREQUENCIA_2H = '2H'
    FREQUENCIA_4H = '4H'
    FREQUENCIA_DIARIO = 'DIARIO'
    FREQUENCIAS = [
        (FREQUENCIA_UNICO, 'Data específica'),
        (FREQUENCIA_DIAS_ANTES, 'Dias antes do evento'),
        (FREQUENCIA_2H, 'A cada 2 horas'),
        (FREQUENCIA_4H, 'A cada 4 horas'),
        (FREQUENCIA_DIARIO, 'Diariamente'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lembretes')
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='lembretes', null=True, blank=True)
    titulo = models.CharField(max_length=140)
    mensagem = models.TextField(blank=True)
    data_hora = models.DateTimeField()
    frequencia = models.CharField(max_length=20, choices=FREQUENCIAS, default=FREQUENCIA_UNICO)
    dias_antes = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data_hora']
        verbose_name = 'Lembrete'
        verbose_name_plural = 'Lembretes'

    def __str__(self):
        return self.titulo


class Notificacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    titulo = models.CharField(max_length=140)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criada_em']
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'

    def __str__(self):
        return self.titulo


class ImagemGaleria(models.Model):
    titulo = models.CharField(max_length=120)
    imagem = models.ImageField(upload_to='galeria/')
    descricao = models.CharField(max_length=255, blank=True)
    publicada = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criada_em']
        verbose_name = 'Imagem da galeria'
        verbose_name_plural = 'Imagens da galeria'

    def __str__(self):
        return self.titulo


class LogSistema(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    acao = models.CharField(max_length=120)
    descricao = models.TextField(blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Log do sistema'
        verbose_name_plural = 'Logs do sistema'

    def __str__(self):
        return self.acao
