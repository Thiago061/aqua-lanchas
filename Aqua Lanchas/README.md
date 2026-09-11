# Sistema Aqua Lanchas

Sistema web em Django para gestão institucional, clientes, funcionários, frota, reservas, agenda, lembretes e relatórios da Aqua Lanchas.

## Como executar no VS Code

1. Abra a pasta `outputs/aqua_lanchas` no VS Code.
2. Ative o ambiente virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Instale as dependências, se necessário:

```powershell
pip install -r requirements.txt
```

4. Rode as migrações:

```powershell
python manage.py migrate
```

5. Crie dados iniciais:

```powershell
python manage.py criar_dados_iniciais
```

6. Execute o servidor:

```powershell
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`.

## Usuários de demonstração

Todos usam a senha `Aqua@12345`.

- `admin`: administrador com acesso ao painel e `/admin/`.
- `funcionario`: funcionário com acesso operacional.
- `cliente`: cliente final para reservas.

## Estrutura dos arquivos

- `manage.py`: utilitário principal do Django para servidor, migrações, comandos e administração.
- `config/settings.py`: configura idioma `pt-br`, fuso `America/Sao_Paulo`, SQLite, templates, arquivos estáticos, mídia, login e e-mail em console.
- `config/urls.py`: conecta o admin do Django, rotas do app `core` e arquivos de mídia em desenvolvimento.
- `core/models.py`: contém `Perfil`, `Lancha`, `Reserva`, `Lembrete`, `Notificacao`, `ImagemGaleria` e `LogSistema`. A reserva valida conflito de horário e capacidade da embarcação.
- `core/forms.py`: formulários Bootstrap para cadastro de cliente, perfil, lanchas, reservas e lembretes.
- `core/views.py`: páginas públicas, autenticação pós-cadastro, dashboard, reservas, agenda, API de disponibilidade, lembretes, clientes, lanchas e relatórios.
- `core/urls.py`: URLs nomeadas do sistema.
- `core/admin.py`: cadastro dos modelos no Django Admin com filtros e busca.
- `core/signals.py`: cria automaticamente perfil e grupo quando um usuário é criado.
- `core/management/commands/criar_dados_iniciais.py`: cria grupos, usuários, lanchas e uma reserva de exemplo.
- `templates/base.html`: layout principal com Bootstrap, menu responsivo, mensagens e rodapé.
- `templates/core/home.html`: página institucional pública com Home, Quem Somos, Sobre a Empresa, Frota, Serviços, Galeria, Contato, Localização e FAQ.
- `templates/core/*.html`: telas internas de dashboard, reservas, detalhe, agenda, lembretes, lanchas, clientes, relatórios e formulários.
- `templates/registration/*.html`: login, cadastro e recuperação de senha.
- `static/css/style.css`: identidade visual responsiva da Aqua Lanchas.
- `static/js/app.js`: calendário em modos dia, semana e mês, além de consulta assíncrona de disponibilidade.
- `requirements.txt`: dependências do projeto.

## Segurança

O sistema usa autenticação do Django, senhas criptografadas, CSRF nos formulários, ORM contra SQL Injection, validações de permissão por perfil e proteção nativa de sessão.
