from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from app import db
from app.models import Consulta, Profissional
from app.utils import valida_perfil_usuario, valida_data_hora
from app.audit import registrar_auditoria

api = Namespace("consultas", description="Operações relacionadas a consultas médicas")

consulta_input = api.model("ConsultaCreate", {
    "profissional_id": fields.Integer(required=True, description="ID do profissional de saúde"),
    "data": fields.String(required=True, description="Data e hora da consulta", example="2024-12-31"),
    "hora": fields.String(required=True, description="Hora da consulta", example="14:30"),
    "tipo": fields.String(required=True, description="Tipo da consulta: presencial ou online")
})

consulta_output = api.model("ConsultaOut", {
    "id": fields.Integer,
    "paciente_id": fields.Integer,
    "profissional_id": fields.Integer,
    "data": fields.String,
    "hora": fields.String,
    "status": fields.String,
    "tipo": fields.String
})

consulta_update_model = api.model("ConsultaUpdate", {
    "data": fields.String(description="Data da consulta", example="2024-12-31"),
    "hora": fields.String(description="Hora da consulta", example="14:30"),
    "tipo": fields.String(description="Tipo da consulta: presencial ou online")
})

@api.route("/")
class ConsultaCollection(Resource):
    @jwt_required()
    @api.marshal_list_with(consulta_output)
    def get(self):
        identificacao = get_jwt()
        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "paciente")

        if validacao_usuario:
            return validacao_usuario
        
        else:
            id_paciente = identificacao["id"]
            consultas = Consulta.query.filter_by(paciente_id=id_paciente).all()

            return consultas, 200


    @jwt_required()
    @api.expect(consulta_input, validate=True)
    @api.marshal_with(consulta_output)
    def post(self):
        identificacao = get_jwt()
        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "paciente")

        if validacao_usuario:
            return validacao_usuario
        
        else:
            payload = request.json
            profissional_id = payload["profissional_id"]
            data = payload["data"]
            hora = payload["hora"]
            tipo = payload["tipo"]

            valida_data_hora(data)

            profissional = Profissional.query.get(profissional_id)
            if not profissional:
                api.abort(404, "Profissional não encontrado.")

            nova_consulta = Consulta(
                paciente_id=identificacao["id"],
                profissional_id=profissional_id,
                data=data,
                hora=hora,
                tipo=tipo,
                status="agendada"
            )

            db.session.add(nova_consulta)
            db.session.commit()

            registrar_auditoria(
                usuario_id=identificacao["id"],
                acao="NOVA_CONSULTA",
                detalhes=f"Consulta criada para o paciente {identificacao['id']}"
            )

            return nova_consulta, 201


@api.route("/<int:id_consulta>")
class ConsultaUpdate(Resource):
    @jwt_required()
    @api.expect(consulta_update_model)
    @api.marshal_with(consulta_output)

    def put(self, id_consulta):
        identificacao = get_jwt()
        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "paciente")

        if validacao_usuario:
            return validacao_usuario
        
        else:
            consulta = Consulta.query.get_or_404(id_consulta)

            payload = request.json

            if "data" in payload:
                consulta.data = payload["data"]

            if "hora" in payload:
                consulta.hora = payload["hora"]

            if "tipo" in payload:
                consulta.tipo = payload["tipo"]

            db.session.commit()

            registrar_auditoria(
                usuario_id=identificacao["id"],
                acao="ATUALIZAR_CONSULTA",
                detalhes=f"Consulta {id_consulta} atualizada"
            )

            return consulta, 200

