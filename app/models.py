from app import db
from sqlalchemy import Enum
import enum
from datetime import datetime

class PerfilEnum(enum.Enum):
    paciente = "paciente"
    profissional = "profissional"
    administrador = "administrador"

class StatusEnum(enum.Enum):
    agendada = "agendada"
    concluida = "concluida"
    cancelada = "cancelada"

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    perfil = db.Column(Enum(PerfilEnum, name="perfil_enum"), nullable=False)

class Administrador(db.Model):
    __tablename__ = 'administradores'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), primary_key=True)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    endereco = db.Column(db.Text)
    telefone = db.Column(db.String(20))

    usuario = db.relationship("Usuario", backref=db.backref("administrador", uselist=False))


class Paciente(db.Model):
    __tablename__ = 'pacientes'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), primary_key=True)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    endereco = db.Column(db.Text)
    telefone = db.Column(db.String(20))

    usuario = db.relationship("Usuario", backref=db.backref("paciente", uselist=False))

class Profissional(db.Model):
    __tablename__ = 'profissionais'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), primary_key=True)
    conselho = db.Column(db.String(50), nullable=False)
    numero_conselho = db.Column(db.String(50), nullable=False)
    especialidade = db.Column(db.String(50))

    usuario = db.relationship("Usuario", backref=db.backref("profissional", uselist=False))

class Consulta(db.Model):
    __tablename__ = 'consultas'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("pacientes.id"), nullable=False)
    profissional_id = db.Column(db.Integer, db.ForeignKey("profissionais.id"), nullable=False)
    data = db.Column(db.Date, nullable=True)
    hora = db.Column(db.Time, nullable=True)
    status = db.Column(Enum(StatusEnum), default="agendada", nullable=False)
    tipo = db.Column(Enum("presencial", "online", name="tipo_consulta_enum"), nullable=False)

    paciente = db.relationship("Paciente", backref="consultas")
    profissional = db.relationship("Profissional", backref="consultas")

class Prontuario(db.Model):
    __tablename__ = 'prontuarios'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    consulta_id = db.Column(db.Integer, db.ForeignKey("consultas.id"), nullable=False)
    anotacoes = db.Column(db.Text)
    prescricao = db.Column(db.Text)
    data_registro = db.Column(db.DateTime, nullable=False)

    consulta = db.relationship("Consulta", backref="prontuario")

class Telemedicina(db.Model):
    __tablename__ = "telemedicinas"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    consulta_id = db.Column(db.Integer, db.ForeignKey("consultas.id"), nullable=False)

    codigo_sala = db.Column(db.String(255), unique=True, nullable=False)
    url_sala = db.Column(db.String(500), nullable=False)

    iniciada_em = db.Column(db.DateTime, default=datetime.utcnow)
    encerrada_em = db.Column(db.DateTime, nullable=True)

    ativa = db.Column(db.Boolean, default=True)

    consulta = db.relationship("Consulta", backref="telemedicina", uselist=False)

class LogAuditoria(db.Model):
    __tablename__ = "logs_auditoria"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    acao = db.Column(db.String(255))
    detalhes = db.Column(db.Text)
    data_hora = db.Column(db.DateTime, nullable=False)

    usuario = db.relationship("Usuario", backref="logs_auditoria")
