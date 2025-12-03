from app import db
from models import LogAuditoria

def registrar_auditoria(usuario_id, acao, detalhes=None):
    log = LogAuditoria(
        usuario_id = usuario_id,
        acao = acao,
        detalhes = detalhes
    )

    db.session.add(log)
    db.session.commit()