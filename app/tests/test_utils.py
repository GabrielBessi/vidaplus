import pytest
from datetime import datetime
from app.utils import (
    converte_data,
    valida_perfil_usuario,
    valida_data_hora,
    mensagem_criacao_sucesso
)

# -----------------------------
# TESTES PARA converte_data()
# -----------------------------
def test_converte_data_valida():
    resultado = converte_data("25/12/2024")
    assert resultado == "2024-12-25"


def test_converte_data_invalida():
    with pytest.raises(ValueError):
        converte_data("2024-12-25")  # formato errado

# -----------------------------
# TESTES PARA valida_perfil_usuario()
# -----------------------------
def test_valida_perfil_usuario_paciente_ok():
    identificacao = {"id": 1, "perfil": "paciente"}
    resp = valida_perfil_usuario(identificacao, "paciente", "paciente")
    assert resp is None  # permitido


def test_valida_perfil_usuario_paciente_negado():
    identificacao = {"id": 1, "perfil": "profissional"}
    resp = valida_perfil_usuario(identificacao, "profissional", "paciente")
    assert resp[1] == 401
    assert "Apenas pacientes" in resp[0]["message"]


def test_valida_perfil_usuario_none():
    resp = valida_perfil_usuario(None, None, "paciente")
    assert resp[1] == 401
    assert "Apenas pacientes" in resp[0]["message"]


def test_valida_perfil_usuario_profissional_ok():
    identificacao = {"id": 2, "perfil": "profissional"}
    resp = valida_perfil_usuario(identificacao, "profissional", "profissional")
    assert resp is None


def test_valida_perfil_usuario_administrador_negado():
    identificacao = {"id": 3, "perfil": "paciente"}
    resp = valida_perfil_usuario(identificacao, "paciente", "administrador")
    assert resp[1] == 401
    assert "Apenas administradores" in resp[0]["message"]


# -----------------------------
# TESTES PARA valida_data_hora()
# -----------------------------
def test_valida_data_hora_valida():
    data_str = "2024-12-31T14:30:00"
    resultado = valida_data_hora(data_str)
    assert isinstance(resultado, datetime)
    assert resultado.year == 2024
    assert resultado.month == 12
    assert resultado.day == 31


def test_valida_data_hora_invalida():
    resultado = valida_data_hora("31-12-2024 14:30")
    assert resultado[1] == 400
    assert "Formato de data_hora inválido" in resultado[0]["message"]


# -----------------------------
# TESTES PARA mensagem_criacao_sucesso()
# -----------------------------
def test_mensagem_criacao_sucesso():
    entidade = "Paciente"
    dados = {"id": 1, "nome": "Maria"}

    resp, status = mensagem_criacao_sucesso(entidade, dados)

    assert status == 201
    assert resp["mensagem"] == "Paciente criado com sucesso."
    assert resp["dados"] == dados
