from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Lancha, Lembrete, Perfil, Reserva

class FuncionarioForm(forms.ModelForm):

    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'password'
        ]

class BootstrapFormMixin:
    def aplicar_bootstrap(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(widget, forms.Select):
                widget.attrs.update({'class': 'form-select'})
            else:
                widget.attrs.update({'class': 'form-control'})


class CadastroClienteForm(BootstrapFormMixin, UserCreationForm):
    first_name = forms.CharField(label='Nome', max_length=150)
    last_name = forms.CharField(label='Sobrenome', max_length=150)
    email = forms.EmailField(label='E-mail')
    telefone = forms.CharField(label='Telefone', max_length=20, required=False)
    documento = forms.CharField(label='CPF', max_length=20, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username','first_name','last_name','email','password1','password2')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_bootstrap()
        placeholders = {
            'first_name': 'Seu nome',
            'last_name': 'Seu sobrenome',
            'email': 'voce@exemplo.com',
            'telefone': '(00) 00000-0000',
            'documento': '000.000.000-00',
            'username': 'Escolha um nome de usuário',
            'password1': 'Crie uma senha',
            'password2': 'Digite a senha novamente',
        }
        autocompletes = {
            'first_name': 'given-name',
            'last_name': 'family-name',
            'email': 'email',
            'telefone': 'tel',
            'documento': 'off',
            'username': 'username',
            'password1': 'new-password',
            'password2': 'new-password',
        }
        for field_name, placeholder in placeholders.items():
            self.fields[field_name].widget.attrs.update({
                'placeholder': placeholder,
                'autocomplete': autocompletes[field_name],
            })

    def save(self, commit=True):
        user = super().save(commit=False)

        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()

        perfil, criado = Perfil.objects.get_or_create(
            usuario=user,
            defaults={'tipo': Perfil.TIPO_CLIENTE}
        )

        perfil.telefone = self.cleaned_data.get('telefone', '')
        perfil.documento = self.cleaned_data.get('documento', '')
        perfil.save()

        return user


class PerfilForm(BootstrapFormMixin, forms.ModelForm):
    first_name = forms.CharField(label='Nome', max_length=150)
    last_name = forms.CharField(label='Sobrenome', max_length=150)
    email = forms.EmailField(label='E-mail')

    class Meta:
        model = Perfil
        fields = ('telefone', 'documento', 'endereco', 'data_nascimento')
        widgets = {'data_nascimento': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['first_name'].initial = self.user.first_name
        self.fields['last_name'].initial = self.user.last_name
        self.fields['email'].initial = self.user.email
        self.aplicar_bootstrap()

    def save(self, commit=True):
        perfil = super().save(commit=False)
        self.user.first_name = self.cleaned_data['first_name']
        self.user.last_name = self.cleaned_data['last_name']
        self.user.email = self.cleaned_data['email']
        if commit:
            self.user.save()
            perfil.save()
        return perfil


class LanchaForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Lancha
        fields = ('nome', 'descricao', 'capacidade', 'preco_hora', 'status', 'imagem')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_bootstrap()


class ReservaForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ('cliente', 'lancha', 'data', 'horario_inicio', 'horario_fim', 'quantidade_pessoas', 'origem', 'status', 'observacoes')
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'horario_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'horario_fim': forms.TimeInput(attrs={'type': 'time'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = User.objects.filter(perfil__tipo=Perfil.TIPO_CLIENTE, is_active=True)
        self.fields['lancha'].queryset = Lancha.objects.filter(status=Lancha.STATUS_ATIVA)
        if self.usuario and self.usuario.perfil.tipo == Perfil.TIPO_CLIENTE:
            self.fields.pop('cliente')
            self.fields.pop('origem')
            self.fields.pop('status')
        self.aplicar_bootstrap()

    def save(self, commit=True):
        reserva = super().save(commit=False)
        if self.usuario:
            reserva.criada_por = self.usuario
            if self.usuario.perfil.tipo == Perfil.TIPO_CLIENTE:
                reserva.cliente = self.usuario
                reserva.origem = Reserva.ORIGEM_CLIENTE
                reserva.status = Reserva.STATUS_PENDENTE
        reserva.full_clean()
        if commit:
            reserva.save()
        return reserva


class LembreteForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Lembrete
        fields = ('reserva', 'titulo', 'mensagem', 'data_hora', 'frequencia', 'dias_antes', 'ativo')
        widgets = {
            'data_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'mensagem': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        if self.usuario:
            self.fields['reserva'].queryset = Reserva.objects.filter(cliente=self.usuario) | Reserva.objects.filter(criada_por=self.usuario)
        self.aplicar_bootstrap()

    def save(self, commit=True):
        lembrete = super().save(commit=False)
        if self.usuario:
            lembrete.usuario = self.usuario
        if commit:
            lembrete.save()
        return lembrete
