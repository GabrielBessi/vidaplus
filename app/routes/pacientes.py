from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt
from flask import request
from app import db
from app.models import Paciente, Usuario
from app.audit import registrar_auditoria
from app.utils import valida_perfil_usuario

api = Namespace("pacientes", description="Operações relacionadas a pacientes")

paciente_model = api.model("Paciente", {
    "id": fields.Integer(readonly=True),
    "nome": fields.String,
    "email": fields.String,
    "cpf": fields.String,
    "data_nascimento": fields.String,
    "endereco": fields.String,
    "telefone": fields.String
})

paciente_update_model = api.model("PacienteUpdate", {
    "nome": fields.String,
    "email": fields.String,
    "endereco": fields.String,
    "telefone": fields.String
})


@api.route("/")
class PacienteResource(Resource):

    @jwt_required()
    @api.marshal_with(paciente_model, code=200)
    @api.response(401, "Você não tem permissão.")
    @api.response(404, "Paciente não encontrado.")
    def get(self):
        identificacao = get_jwt()
        validacao = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "paciente")

        if validacao:
            return {"message": "Não autorizado"}, 401

        id_paciente = identificacao["id"]
        paciente = Paciente.query.get_or_404(id_paciente)

        return {
            "id": paciente.id,
            "nome": paciente.usuario.nome,
            "email": paciente.usuario.email,
            "cpf": paciente.cpf,
            "data_nascimento": paciente.data_nascimento.strftime("%Y-%m-%d") if paciente.data_nascimento else None,
            "endereco": paciente.endereco,
            "telefone": paciente.telefone
        }, 200


    @jwt_required()
    @api.expect(paciente_update_model)
    @api.response(200, "Paciente atualizado.")
    def put(self):
        identificacao = get_jwt()
        validacao = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "paciente")

        if validacao:
            return {"message": "Não autorizado"}, 401

        id_paciente = identificacao["id"]
        paciente = Paciente.query.get_or_404(id_paciente)

        data = request.json or {}

        if "nome" in data:
            paciente.usuario.nome = data["nome"]

        if "email" in data:
            existe = Usuario.query.filter(
                Usuario.email == data["email"],
                Usuario.id != paciente.usuario.id
            ).first()
            if existe:
                return {"message": "E-mail já cadastrado."}, 400
            paciente.usuario.email = data["email"]

        if "endereco" in data:
            paciente.endereco = data["endereco"]

        if "telefone" in data:
            paciente.telefone = data["telefone"]

        db.session.commit()

        registrar_auditoria(
            usuario_id=id_paciente,
            acao="PACIENTE_ATUALIZADO",
            detalhes=f"Paciente atualizado: {id_paciente}"
        )

        return {"message": f"Paciente {id_paciente} atualizado"}, 200
