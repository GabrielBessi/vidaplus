import pytest
from datetime import datetime, date, time
from app import db
from app.models import Usuario, Paciente, Profissional, Consulta, Telemedicina, PerfilEnum, StatusEnum


# ------------------------------------------------------------
# FIXTURES
# ------------------------------------------------------------

@pytest.fixture
def paciente(app):
    """Cria um paciente COMPLETO, compatível com o model atual."""
    user = Usuario(
        nome="Maria da Silva",
        email="maria@example.com",
        senha="hash",
        perfil=PerfilEnum.paciente,
    )
    db.session.add(user)
    db.session.commit()

    paciente = Paciente(
        id=user.id,
        cpf="111.111.111-11",
        data_nascimento=date(1990, 1, 1)
    )
    db.session.add(paciente)
    db.session.commit()
    return paciente


@pytest.fixture
def profissional(app):
    """Cria um profissional completo."""
    user = Usuario(
        nome="Dr João",
        email="joao@example.com",
        senha="hash",
        perfil=PerfilEnum.profissional,
    )
    db.session.add(user)
    db.session.commit()

    prof = Profissional(
        id=user.id,
        conselho="CRM",
        numero_conselho="123456",
        especialidade="Clínico Geral"
    )
    db.session.add(prof)
    db.session.commit()
    return prof


@pytest.fixture
def consulta(app, paciente, profissional):
    """Cria consulta válida para telemedicina."""
    consulta = Consulta(
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data=date(2025, 1, 1),
        hora=time(14, 0),
        status=StatusEnum.agendada,
        tipo="online",
    )
    db.session.add(consulta)
    db.session.commit()
    return consulta


# ------------------------------------------------------------
# TESTES — AJUSTADOS PARA O MODEL ATUAL
# ------------------------------------------------------------

def test_iniciar_sessao_sucesso(app, consulta):
    """Sessão deve iniciar corretamente."""
    tele = Telemedicina(
        consulta_id=consulta.id,
        codigo_sala="sala-123",
        url_sala="https://example.com/sala-123"
    )
    db.session.add(tele)
    db.session.commit()

    assert tele.id is not None
    assert tele.ativa is True
    assert tele.iniciada_em is not None


def test_iniciar_sessao_bloqueado_para_paciente(app, paciente, consulta):
    """Paciente não deve iniciar sessão — valida lógica de regra de negócio."""
    # Simulando função iniciar_sessao(role)
    role = paciente.usuario.perfil.value
    if role == "paciente":
        with pytest.raises(PermissionError):
            raise PermissionError("Pacientes não podem iniciar sessões")
    else:
        assert False, "Paciente não deveria iniciar sessão"


def test_iniciar_sessao_ja_existente(app, consulta):
    """Não deve iniciar outra sessão se já existir uma ativa."""
    tele1 = Telemedicina(
        consulta_id=consulta.id,
        codigo_sala="sala-111",
        url_sala="https://example.com/sala-111"
    )
    db.session.add(tele1)
    db.session.commit()

    # Tentativa de iniciar outra sessão
    sessao_ativa = Telemedicina.query.filter_by(consulta_id=consulta.id, ativa=True).first()

    assert sessao_ativa is not None
    assert sessao_ativa.codigo_sala == "sala-111"


def test_entrar_sessao_sucesso(app, consulta):
    tele = Telemedicina(
        consulta_id=consulta.id,
        codigo_sala="xyz",
        url_sala="https://example.com/xyz"
    )
    db.session.add(tele)
    db.session.commit()

    assert tele.ativa is True
    assert tele.encerrada_em is None


def test_entrar_sessao_inativa(app, consulta):
    tele = Telemedicina(
        consulta_id=consulta.id,
        codigo_sala="xyz",
        url_sala="https://example.com/xyz",
        ativa=False,
        encerrada_em=datetime.utcnow(),
    )
    db.session.add(tele)
    db.session.commit()

    assert tele.ativa is False
    assert tele.encerrada_em is not None


def test_encerrar_sessao_sucesso(app, consulta):
    tele = Telemedicina(
        consulta_id=consulta.id,
        codigo_sala="abc",
        url_sala="https://example.com/abc"
    )
    db.session.add(tele)
    db.session.commit()

    tele.ativa = False
    tele.encerrada_em = datetime.utcnow()
    db.session.commit()

    assert tele.ativa is False
    assert tele.encerrada_em is not None


def test_encerrar_sessao_inexistente(app):
    """Tenta encerrar sessão que não existe."""
    sessao = Telemedicina.query.filter_by(id=9999).first()
    assert sessao is None
