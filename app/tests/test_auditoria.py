import pytest
from app.audit import registrar_auditoria
from app.models import LogAuditoria
from datetime import datetime

def test_registrar_auditoria_salva_log_no_banco(app, db_session):
    """Deve registrar auditoria corretamente no banco."""
    
    usuario_id = 10
    acao = "TESTE_AUDITORIA"
    detalhes = "Log gerado para teste"

    registrar_auditoria(usuario_id, acao, detalhes)

    log = LogAuditoria.query.first()

    assert log is not None
    assert log.usuario_id == usuario_id
    assert log.acao == acao
    assert log.detalhes == detalhes
    assert isinstance(log.data_hora, datetime)


def test_registrar_auditoria_sem_detalhes(app, db_session):
    """Deve registrar auditoria mesmo sem detalhes."""
    
    usuario_id = 20
    acao = "ACAO_SEM_DETALHES"

    registrar_auditoria(usuario_id, acao)

    log = LogAuditoria.query.first()

    assert log is not None
    assert log.usuario_id == usuario_id
    assert log.acao == acao
    assert log.detalhes is None


def test_registrar_varias_auditorias(app, db_session):
    """Deve registrar múltiplas entradas de auditoria."""
    
    registrar_auditoria(1, "ACAO_1")
    registrar_auditoria(2, "ACAO_2")
    registrar_auditoria(3, "ACAO_3")

    logs = LogAuditoria.query.all()

    assert len(logs) == 3
    assert logs[0].usuario_id == 1
    assert logs[1].usuario_id == 2
    assert logs[2].usuario_id == 3
