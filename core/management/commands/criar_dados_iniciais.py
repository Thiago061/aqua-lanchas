from datetime import date, time, timedelta

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from core.models import Lancha, Perfil, Reserva


class Command(BaseCommand):
    help = 'Cria grupos, usuários de demonstração, lanchas e reservas iniciais.'

    def handle(self, *args, **options):
        for nome in ['Administrador', 'Funcionário', 'Cliente']:
            Group.objects.get_or_create(name=nome)

        admin = self.criar_usuario('admin', 'admin@aqualanchas.com.br', 'Admin', 'Aqua', Perfil.TIPO_ADMIN, True, True)
        funcionario = self.criar_usuario('funcionario', 'funcionario@aqualanchas.com.br', 'Marina', 'Operações', Perfil.TIPO_FUNCIONARIO, True, False)
        cliente = self.criar_usuario('cliente', 'cliente@exemplo.com', 'Cliente', 'Demonstração', Perfil.TIPO_CLIENTE, False, False)

        lanchas = [
            ('Aqua Prime 28', 'Lancha confortável para passeios familiares e grupos pequenos.', 8, 650),
            ('Aqua Sport 32', 'Embarcação ágil para rotas panorâmicas e eventos rápidos.', 10, 820),
            ('Aqua Premium 40', 'Lancha ampla para eventos, comemorações e experiências exclusivas.', 14, 1250),
        ]
        objetos = []
        for nome, descricao, capacidade, preco in lanchas:
            lancha, _ = Lancha.objects.get_or_create(
                nome=nome,
                defaults={'descricao': descricao, 'capacidade': capacidade, 'preco_hora': preco},
            )
            objetos.append(lancha)

        Reserva.objects.get_or_create(
            cliente=cliente,
            criada_por=funcionario,
            lancha=objetos[0],
            data=date.today() + timedelta(days=2),
            horario_inicio=time(9, 0),
            horario_fim=time(12, 0),
            defaults={'quantidade_pessoas': 5, 'origem': Reserva.ORIGEM_WHATSAPP, 'status': Reserva.STATUS_APROVADA},
        )

        self.stdout.write(self.style.SUCCESS('Dados iniciais criados. Senha dos usuários: Aqua@12345'))

    def criar_usuario(self, username, email, nome, sobrenome, tipo, is_staff, is_superuser):
        user, created = User.objects.get_or_create(username=username, defaults={
            'email': email,
            'first_name': nome,
            'last_name': sobrenome,
            'is_staff': is_staff,
            'is_superuser': is_superuser,
        })
        if created:
            user.set_password('Aqua@12345')
            user.save()
        perfil = user.perfil
        perfil.tipo = tipo
        perfil.save()
        grupo, _ = Group.objects.get_or_create(name=perfil.get_tipo_display())
        user.groups.add(grupo)
        return user
