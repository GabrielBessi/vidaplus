# VidaPlus API

API para gerenciamento de pacientes, profissionais, telemedicina e administração de uma clínica médica.

link de acesso: https://vidaplus.onrender.com/docs

---

## Tecnologias

- Python 3.11+
- Flask
- Flask-RESTX
- Flask-Migrate
- Flask-JWT-Extended
- SQLAlchemy
- MySQL / MariaDB
- Alembic
- Git

---

## Estrutura do projeto
    projeto_final_clinica/
    │
    ├─ app/
    │ ├─ init.py # Criação da app e configuração
    │ ├─ models.py # Models do banco de dados
    │ ├─ config.py # Configurações da aplicação
    | |- audit.py # Envia dados para tabela de auditoria
    | |-tests/ # Teste unitários
    | |- services/ #segurança de autenticação do sistema
    │ |─ routes/ # Endpoints da API
    │
    ├─ migrations/ # Migrations do Alembic
    ├─ venv/ # Ambiente virtual
    ├─ requirements.txt # Dependências do projeto
    └─ run.py # Script para rodar a aplicação

# Para testes locais

## Pré-requisitos

- Python 3.11+
- MySQL
- Git
- Virtualenv

---

## Instalação

```bash
    git clone https://github.com/GabrielBessi/vidaplus.git
    cd projeto_final_clinica 
    python -m venv venv

    # Windows
        .\venv\Scripts\Activate.ps1

    # Linux / macOS
        source venv/bin/activate

    pip install -r requirements.txt

    # Windows PowerShell
    $env:FLASK_APP = "app:create_app"
    $env:FLASK_ENV = "development"

    #Iniciando banco
    flask db init
    flask db migrate -m "Criacao das tabelas iniciais"
    flask db upgrade

    python run.py

    #Rota do swagger
    http://127.0.0.1:5000/docs

```

# endpoints:

    - Pacientes

    - Profissionais

    - Telemedicina

    - Administração

    - Usuários

    - Consultas

    - Prontuários

    - Autenticação (JWT)

# Usuário administrador inicial
Já está cadastrado como default um usuário administrador para logar com as credenciais abaixo:

    Nome: Administrador
    E-mail: adm1@gmail.com
    Senha: admin123@
    Perfil: administrador

# Endpoints e seus uso:
### Pacientes
````
    Método	   Rota	               Função
    GET	    /pacientes/	  buscar dados do paciente logado
    PUT	    /pacientes/	  atualizar apenas o paciente logado

    Necessário estar autenticado com o login do paciente.
````
### Profissionais
````
    Método	     Rota                   Função
    GET	    /profissionais/	  buscar dados do profissional logado
    PUT	    /profissionais/	  atualizar apenas o profissional logado

    Necessário estar autenticado com o login do profissional.
````
### Telemedicina
````
    Método	            Rota	                                               Função
    GET	    /telemedicina/entrar/{consulta_id}	        O paciente consegue entrar na chamada através do id da consulta
    POST    /telemedicina/encerrar/{consulta_id}	    O profissional consegue encerrar um sessão iniciada
    POST    /telemedicina/iniciar/{consulta_id}	        O profissional consegue iniciar uma nova sessão

    O profissional só consegue iniciar uma chamada se tiver uma consulta agendada com o mesmo.

    Necessário estar autenticado com o login do paciente para entrar na chamada.
    Necessário estar autenticado com o login do profissional para iniciar ou encerrar uma chamada.
````
### Administração
````
    Método	                Rota	                                               Função
    POST	    /administracao/cadastro/administrador	        O administrador pode cadastrar outros administradores
    GET         /administracao/lista_administradores	        Lista todos os administradores
    PUT         /administracao/lista_administradores/{id}       Atualiza um único administrador
    GET         /administracao/lista_administradores/{id}       Lista um único administrador
    GET         /administracao/lista_consultas                  Lista todas as consultas
    GET         /administracao/lista_consultas/{id}             Lista uma única consulta
    GET         /administracao/lista_pacientes                  Lista todos os pacientes
    GET         /administracao/lista_pacientes/{id}             Lista um único paciente
    GET         /administracao/lista_profissionais              Lista todos os profissionais
    GET         /administracao/lista_profissionais/{id}         Lista um único profissional

   Necessário estar autenticado com o login de um administrador.
````
### Usuarios
````
    Método	     Rota                             Função
    POST	    /usuarios/cadastro	      Cadastra um novo paciente
    POST	    /usuario/profissional	  Cadastra um novo profissional

    Não é necessário estar autenticado.
````
### Consultas
````
    Método	     Rota                             Função
    GET	     /consultas/                Lista as consultas de um paciente
    POST	 /consultas/	            Marca uma nova consulta
    PUT      /consultas/{id_consulta}   Atualiza uma consulta

    É necessário estar autenticado com o login do paciente.
````
### Prontuarios
````
    Método	     Rota                                         Função
    POST	 /prontuarios/                           Cria um novo protuário
    GET	     /prontuarios/paciente/{consulta_id}     Lista prontuários de um único paciente
    GET      /prontuarios/{id}                       Lista um único prontuário

    Somento o profissional pode criar um novo prontuário.

    É necessário estar autenticado com o login do profissional.
    É necessário estar autenticado com o login do paciente.
````
### Auth
````
    Método	     Rota           Função
    POST	 /auth/login      Logar no usuário

    Através do login será disponibilizado o token que deverá ser utilizado no swagger para autenticar
    e acessar as rotas.
````