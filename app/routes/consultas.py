from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from app import db
from app.models import Consulta, Profissional
from app.utils import valida_perfil_usuario, valida_data_hora
from audit import registrar_auditoria

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
class ConsultaCreate(Resource):
    @api.expect(consulta_input, validate=True)
    @api.response(201, "Consulta criada com sucesso", consulta_output)
    @api.response(400, "Dados inválidos")
    @api.response(401, "Não autorizado")
    @api.response(404, "Profissional não encontrado")
    @jwt_required()

    @api.marshal_list_with(consulta_output)

    def post(self):

        identificacao = get_jwt()

        valida_perfil_usuario(identificacao, identificacao.get("perfil"), "paciente")
    
        payload = request.json
        profissional_id = payload["profissional_id"]
        data = payload["data"]
        hora = payload["hora"]
        tipo = payload["tipo"]

        if not profissional_id or not data or not hora or not tipo:
            return {"message": "Os campos profissional_id, data_hora e tipo são obrigatórios."}, 400
        
        valida_data_hora(data)
        
        profissional = Profissional.query.get(profissional_id)
        if not profissional:
            return {"message": "Profissional não encontrado."}, 404
        
        paciente_id = identificacao["id"]

        nova_consulta = Consulta(
            paciente_id=paciente_id,
            profissional_id=profissional_id,
            data=data,
            hora=hora,
            tipo=tipo,
            status="agendada"
        )

        db.session.add(nova_consulta)   
        db.session.commit()

        registrar_auditoria (
            usuario_id=paciente_id,
            acao = "NOVA_CONSULTA",
            detalhes= f"Consulta criada para o paciente: {paciente_id}"
        )

        return nova_consulta, 201
        
@api.route("/")
class ConsultaResource(Resource):
    @jwt_required()    
    @api.marshal_list_with(consulta_output)

    def get(self):
        identificacao = get_jwt()

        valida_perfil_usuario(identificacao, identificacao.get("perfil"), "paciente")
        id_paciente = identificacao["id"]
        consulta_paciente = Consulta.query.filter_by(paciente_id=id_paciente)
        resposta = []

        for c in consulta_paciente:
            resposta.append({
                "id": c.id,
                "paciente_id": c.paciente.id,
                "profissional_id": c.profissional.id,
                "data": c.data,
                "hora": c.hora,
                "status": c.status,
                "tipo": c.tipo
            })

        return resposta, 200

    @api.expect(consulta_update_model, validate=True)
    def put(self):
        identificacao = get_jwt()
        id_paciente = identificacao["id"]

        valida_perfil_usuario(identificacao, identificacao.get("perfil"), "paciente")


        consulta = Consulta.query.get_or_404(id_paciente)
        payload = request.json

        if "data" in payload:
            consulta.data = payload["data"]

        if "hora" in payload:
            consulta.hora = payload["hora"]

        if "tipo" in payload:
            consulta.tipo = payload["tipo"]

        db.session.commit()

        registrar_auditoria (
            usuario_id=id_paciente,
            acao = "ATUALIZAR_CONSULTA",
            detalhes= f"Consulta atualizada para o paciente: {id_paciente}"
        )        

        return {"message": f"Paciente {id_paciente} atualizado"}, 200



