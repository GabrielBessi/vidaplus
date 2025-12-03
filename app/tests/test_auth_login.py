import pytest
from flask_jwt_extended import decode_token
from app.models import Usuario
from app import create_app, db

@pytest.fixture
def app():
    app = create_app(testing=True)

    # Banco apenas em memória
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test-secret"
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def usuario_valido(app):
    """Cria um usuário válido no banco."""
    from app.services.security import gerar_hash_senha
    from app.models import PerfilEnum

    user = Usuario(
        nome="Teste",
        email="teste@example.com",
        senha=gerar_hash_senha("senha123"),
        perfil=PerfilEnum.paciente
    )
    db.session.add(user)
    db.session.commit()
    return user


# ---------------------------------------------------------
#  TESTES
# ---------------------------------------------------------

def test_login_sucesso(client, usuario_valido):
    """Deve retornar token ao fornecer credenciais corretas."""
    resp = client.post("/auth/login", json={
        "email": "teste@example.com",
        "senha": "senha123" 
    })

    assert resp.status_code == 200
    data = resp.get_json()

    assert "access_token" in data
    token = data["access_token"].replace("Bearer ", "")

    decoded = decode_token(token)
    assert decoded["sub"] == str(usuario_valido.id)
    assert decoded["perfil"] == usuario_valido.perfil.value


def test_login_usuario_inexistente(client):
    """Não deve logar com usuário que não existe."""
    resp = client.post("/auth/login", json={
        "email": "naoexiste@example.com",
        "senha": "senha123"
    })

    assert resp.status_code == 401
    assert resp.get_json()["message"] == "E-mail ou senha inválidos."


def test_login_senha_errada(client, usuario_valido):
    """Não deve logar quando a senha está incorreta."""
    resp = client.post("/auth/login", json={
        "email": "teste@example.com",
        "senha": "senhaerrada"
    })

    assert resp.status_code == 401
    assert resp.get_json()["message"] == "E-mail ou senha inválidos."


def test_login_payload_invalido(client):
    """O payload inválido deve gerar erro de validação do Flask-RESTX."""
    resp = client.post("/auth/login", json={
        "email": "email@email.com"
        # senha faltando
    })

    assert resp.status_code == 400
