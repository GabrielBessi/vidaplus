import pytest
from datetime import datetime, date
from app import create_app, db
from app.models import Usuario, Paciente, Profissional, Consulta, PerfilEnum
from app.services.security import gerar_hash_senha


# --- APP ---
@pytest.fixture
def app():
    app = create_app(testing=True)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


# --- CLIENT ---
@pytest.fixture
def client(app):
    return app.test_client()


# --- DB SESSION ---
@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session
        db.session.rollback()


# --- PACIENTE ---
@pytest.fixture
def paciente(app):
    user = Usuario(
        nome="Maria da Silva",
        email="maria@example.com",
        senha=gerar_hash_senha("123456"),  # FIX: senha correta
        perfil=PerfilEnum.paciente
    )
    db.session.add(user)
    db.session.commit()

    pac = Paciente(
        id=user.id,
        cpf="123.456.789-00",
        data_nascimento=datetime(1990, 1, 1),
        endereco="Rua Teste, 123",
        telefone="11999999999"
    )

    db.session.add(pac)
    db.session.commit()

    return pac


# --- PROFISSIONAL ---
@pytest.fixture
def profissional(app):
    user = Usuario(
        nome="Profissional Teste",
        email="prof@example.com",
        senha=gerar_hash_senha("123456"),
        perfil=PerfilEnum.profissional
    )
    db.session.add(user)
    db.session.commit()

    # FIX: o id do profissional é o mesmo do usuário
    prof = Profissional(id=user.id)
    db.session.add(prof)
    db.session.commit()

    return prof


# --- OUTRO PACIENTE ---
@pytest.fixture
def outro_paciente(db_session):
    usuario = Usuario(
        nome="Outro Paciente",
        email="outro@example.com",
        senha=gerar_hash_senha("123456"),
        perfil=PerfilEnum.paciente
    )
    db.session.add(usuario)
    db_session.flush()

    paciente = Paciente(
        id=usuario.id,
        cpf="222.222.222-22",
        data_nascimento=date(1990, 1, 1),
        endereco="Rua Teste 2",
        telefone="2222-2222"
    )
    db_session.add(paciente)
    db_session.commit()

    return paciente


# --- CONSULTA ---
@pytest.fixture
def consulta(app, paciente, profissional):
    cons = Consulta(
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data=datetime.now(),
        motivo="Dor de cabeça"
    )
    db.session.add(cons)
    db.session.commit()
    return cons


# --- TOKEN PACIENTE ---
@pytest.fixture
def token_paciente(client, paciente):
    login_data = {
        "email": paciente.usuario.email,
        "senha": "123456"
    }
    resp = client.post("/login", json=login_data)
    return resp.json["token"]


# --- TOKEN PROFISSIONAL ---
@pytest.fixture
def token_profissional(client, profissional):
    login_data = {
        "email": profissional.usuario.email,
        "senha": "123456"
    }
    resp = client.post("/login", json=login_data)
    return resp.json["token"]
