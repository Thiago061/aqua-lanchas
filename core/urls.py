from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cadastro/', views.CadastroClienteView.as_view(), name='cadastro'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('senha/redefinir/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('senha/redefinir/enviado/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('senha/redefinir/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('senha/redefinir/concluido/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('perfil/', views.perfil, name='perfil'),
    path('reservas/', views.reservas, name='reservas'),
    path('reservas/nova/', views.reserva_criar, name='reserva_criar'),
    path('reservas/<int:pk>/', views.reserva_detalhe, name='reserva_detalhe'),
    path('reservas/<int:pk>/editar/', views.reserva_editar, name='reserva_editar'),
    path('reservas/<int:pk>/status/<str:status>/', views.reserva_status, name='reserva_status'),
    path('calendario/', views.calendario, name='calendario'),
    path('api/disponibilidade/', views.disponibilidade_api, name='disponibilidade_api'),
    path('lembretes/', views.lembretes, name='lembretes'),
    path('lembretes/novo/', views.lembrete_criar, name='lembrete_criar'),
    path('lanchas/', views.lanchas, name='lanchas'),
    path('lanchas/nova/', views.lancha_criar, name='lancha_criar'),
    path('clientes/', views.clientes, name='clientes'),
    path('funcionarios/novo/', views.funcionario_criar, name='funcionario_criar'),
    path('relatorios/', views.relatorios, name='relatorios'),
]
