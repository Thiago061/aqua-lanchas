from django.contrib import admin

from .models import ImagemGaleria, Lancha, Lembrete, LogSistema, Notificacao, Perfil, Reserva


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'telefone', 'ativo', 'criado_em')
    list_filter = ('tipo', 'ativo')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'telefone', 'documento')


@admin.register(Lancha)
class LanchaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'capacidade', 'preco_hora', 'status')
    list_filter = ('status',)
    search_fields = ('nome', 'descricao')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('lancha', 'cliente', 'data', 'horario_inicio', 'horario_fim', 'status', 'origem')
    list_filter = ('status', 'origem', 'data', 'lancha')
    search_fields = ('cliente__username', 'cliente__first_name', 'cliente__last_name', 'lancha__nome')
    date_hierarchy = 'data'


@admin.register(Lembrete)
class LembreteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'data_hora', 'frequencia', 'ativo')
    list_filter = ('frequencia', 'ativo')
    search_fields = ('titulo', 'usuario__username')


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'lida', 'criada_em')
    list_filter = ('lida',)
    search_fields = ('titulo', 'usuario__username')


@admin.register(ImagemGaleria)
class ImagemGaleriaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'publicada', 'criada_em')
    list_filter = ('publicada',)
    search_fields = ('titulo', 'descricao')


@admin.register(LogSistema)
class LogSistemaAdmin(admin.ModelAdmin):
    list_display = ('acao', 'usuario', 'ip', 'criado_em')
    list_filter = ('acao',)
    search_fields = ('acao', 'descricao', 'usuario__username')
