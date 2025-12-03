from flask import Flask
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)


    from .models import Usuario, Paciente, Profissional, Consulta, Prontuario, Telemedicina, LogAuditoria

    from .routes.pacientes import api as pacientes_ns
    from .routes.profissionais import api as profissionais_ns
    from .routes.telemedicina import api as telemedicina_ns
    from .routes.administracao import api as administracao_ns
    from .routes.usuarios import api as usuarios_ns
    from .routes.auth import api as auth_ns
    from .routes.consultas import api as consulta_ns
    from .routes.prontuarios import api as prontuario_ns

    authorizations = {
        "Bearer Auth": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "JWT no formato: **Bearer <token>**"
        }}       

    api = Api(
            app,
            version="1.0", 
            title="VidaPlus API",
            description="API para gerenciamento de pacientes, profissionais, telemedicina e administração.",
            doc="/docs",
            authorizations=authorizations,
            security="Bearer Auth")

    api.add_namespace(pacientes_ns)
    api.add_namespace(profissionais_ns)
    api.add_namespace(telemedicina_ns)
    api.add_namespace(administracao_ns)
    api.add_namespace(usuarios_ns)
    api.add_namespace(consulta_ns)
    api.add_namespace(prontuario_ns)
    api.add_namespace(auth_ns, path="/auth")

    return app

