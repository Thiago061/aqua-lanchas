from datetime import date, time

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Lancha, Perfil, Reserva


class PerfilTests(TestCase):
    def test_cria_perfil_de_cliente_automaticamente(self):
        user = User.objects.create_user(username='cliente_teste', password='senha-segura')

        self.assertEqual(user.perfil.tipo, Perfil.TIPO_CLIENTE)


class ReservaTests(TestCase):
    def setUp(self):
        self.cliente = User.objects.create_user(username='cliente', password='senha-segura')
        self.funcionario = User.objects.create_user(username='funcionario', password='senha-segura')
        self.funcionario.perfil.tipo = Perfil.TIPO_FUNCIONARIO
        self.funcionario.perfil.save()
        self.lancha = Lancha.objects.create(
            nome='Aqua Teste',
            descricao='Lancha de teste',
            capacidade=6,
            preco_hora=500,
        )

    def test_bloqueia_reserva_acima_da_capacidade(self):
        reserva = Reserva(
            cliente=self.cliente,
            criada_por=self.funcionario,
            lancha=self.lancha,
            data=date.today(),
            horario_inicio=time(9, 0),
            horario_fim=time(11, 0),
            quantidade_pessoas=8,
        )

        with self.assertRaises(ValidationError):
            reserva.full_clean()

    def test_bloqueia_conflito_de_horario_na_mesma_lancha(self):
        Reserva.objects.create(
            cliente=self.cliente,
            criada_por=self.funcionario,
            lancha=self.lancha,
            data=date.today(),
            horario_inicio=time(9, 0),
            horario_fim=time(12, 0),
            quantidade_pessoas=4,
        )
        conflito = Reserva(
            cliente=self.cliente,
            criada_por=self.funcionario,
            lancha=self.lancha,
            data=date.today(),
            horario_inicio=time(11, 0),
            horario_fim=time(13, 0),
            quantidade_pessoas=4,
        )

        with self.assertRaises(ValidationError):
            conflito.full_clean()
