from flask_restx import Namespace, Resource, fields
from flask import request
from app import db
from app.models import Paciente, Usuario
from app.audit import registrar_auditoria

api = Namespace("pacientes", description="Operações relacionadas a pacientes")

paciente_model = api.model("Paciente", {
    "id": fields.Integer(readonly=True),
    "nome": fields.String(required=True),
    "email": fields.String(required=True),
    "cpf": fields.String(required=True),
    "data_nascimento": fields.String(required=True, example="DD/MM/YYYY"),
    "endereco": fields.String,
    "telefone": fields.String
})

paciente_update_model = api.model("PacienteUpdate", {
    "nome": fields.String,
    "email": fields.String,
    "endereco": fields.String,
    "telefone": fields.String
})

@api.route("/<int:id>")
class PacienteResource(Resource):
    @api.marshal_with(paciente_model)

    def get(self, id):
        paciente = Paciente.query.get_or_404(id)

        return {
            "id": paciente.id,
            "nome": paciente.usuario.nome,
            "email": paciente.usuario.email,
            "cpf": paciente.cpf,
            "data_nascimento": paciente.data_nascimento.strftime("%Y-%m-%d"),
            "endereco": paciente.endereco,
            "telefone": paciente.telefone
        }, 200
    
    @api.expect(paciente_update_model, validate=True)
    def put(self, id):
        paciente = Paciente.query.get_or_404(id)
        data = request.json

        if "nome" in data:
           paciente.usuario.nome = data["nome"]

        if "email" in data:
            if Usuario.query.filter(Usuario.email == data["email"], Usuario.id != paciente.id).first():
                return {"message": "E-mail já cadastrado."}, 400
            
        if "endereco" in data:
            paciente.endereco = data["endereco"]

        if "telefone" in data:
            paciente.telefone = data["telefone"]

        db.session.commit()

        registrar_auditoria (
            usuario_id=id,
            acao = "PACIENTE_ATUALIZADO",
            detalhes= f"Paciente atualizado: {id}"
        )    

        return {"message": f"Paciente {id} atualizado"}, 200
    