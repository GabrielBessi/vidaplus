from app import db
from app.models import LogAuditoria
from datetime import datetime

def registrar_auditoria(usuario_id, acao, detalhes=None):
    log = LogAuditoria(
        usuario_id = usuario_id,
        acao = acao,
        detalhes = detalhes,
        data_hora = datetime.now()
    )

    db.session.add(log)
    db.session.commit()