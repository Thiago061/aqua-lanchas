# Aqua Lanchas

Sistema web para a gestão de passeios, frota e reservas da **Aqua Lanchas**. Desenvolvido em Django, reúne a apresentação institucional da empresa e uma área operacional para clientes, funcionários e administradores.

## Recursos

- Página institucional responsiva com frota, serviços, galeria, contato e FAQ.
- Cadastro e autenticação de clientes.
- Painel com visão geral das reservas e operações.
- Gestão de lanchas, clientes, funcionários, reservas e lembretes.
- Calendário de reservas e consulta assíncrona de disponibilidade.
- Validação de conflitos de horário e da capacidade das embarcações.
- Relatórios operacionais e administração pelo Django Admin.
- Perfis e permissões para administrador, funcionário e cliente.

## Tecnologias

- Python 3
- Django 6
- SQLite
- Bootstrap
- Pillow

## Como executar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/Thiago061/aqua-lanchas.git
cd aqua-lanchas
```

### 2. Crie e ative um ambiente virtual

No Windows (PowerShell):

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

No macOS ou Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Prepare o banco de dados

```bash
python manage.py migrate
python manage.py criar_dados_iniciais
```

### 5. Inicie o servidor

```bash
python manage.py runserver
```

Abra [http://127.0.0.1:8000/](http://127.0.0.1:8000/) no navegador.

## Acessos de demonstração

Após executar `criar_dados_iniciais`, os seguintes usuários ficam disponíveis:

| Perfil | Usuário | Senha |
| --- | --- | --- |
| Administrador | `admin` | `Aqua@12345` |
| Funcionário | `funcionario` | `Aqua@12345` |
| Cliente | `cliente` | `Aqua@12345` |

> Essas credenciais são exclusivamente para desenvolvimento. Altere-as antes de qualquer publicação em produção.

## Estrutura do projeto

```text
config/       # Configurações globais e rotas do Django
core/         # Modelos, regras de negócio, formulários e views
templates/    # Templates HTML
static/       # CSS, JavaScript e imagens
manage.py     # Comandos de administração do Django
```

## Comandos úteis

```bash
# Executar os testes
python manage.py test

# Criar um administrador próprio
python manage.py createsuperuser
```

O painel administrativo fica em `http://127.0.0.1:8000/admin/`.

## Produção

Antes de publicar o sistema, defina uma `SECRET_KEY` segura, configure `DEBUG = False`, ajuste `ALLOWED_HOSTS`, use um banco de dados apropriado para produção e revise as credenciais de demonstração.

## Licença

Projeto desenvolvido para a Aqua Lanchas.
