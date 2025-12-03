from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from app import db
from app.models import Consulta, Prontuario
from app.utils import valida_perfil_usuario
from datetime import datetime
from app.audit import registrar_auditoria

api = Namespace("prontuarios", description="Operações relacionadas a prontuários médicos")

prontuario_input = api.model("ProntuarioCreate", {
  "id": fields.Integer(readonly=True),
  "consulta_id": fields.Integer(required=True),
  "anotacoes": fields.String(required=True),
  "prescricao": fields.String(required=True)
})

prontuario_output = api.model("ProntuarioOut", {
    "anotacoes": fields.String,
    "prescricao": fields.String,
    "data_registro": fields.String
})

@api.route("/")
class ProntuariosCreate(Resource):
    @jwt_required()
    @api.expect(prontuario_input, validate=True)
    @api.response(201, "Prontuário criado com sucesso", prontuario_output)
    @api.response(404, "Consulta não encontrada", prontuario_output)
    @api.response(401, "Você não tem permissão para criar um prontuário para esta consulta.")
    @api.response(400, "Esta consulta já possui prontuário")
    @api.response(500, "Erro interno do servidor.")	

    def post(self):
        identificacao = get_jwt()

        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "profissional")

        if validacao_usuario:
            return validacao_usuario
        
        else:
            data = request.json
            id_profissional = identificacao["id"]
            consulta_id = data["consulta_id"]
            anotacoes = data["anotacoes"]
            prescricao = data["prescricao"]

            consulta = Consulta.query.get(consulta_id)

            if not consulta:
                return 404
            
            if consulta.profissional_id != id_profissional:
                return 401
            
            if consulta.prontuario:
                return 400
            
            prontuario = Prontuario(
                consulta_id=consulta_id,
                anotacoes=anotacoes,
                prescricao=prescricao,
                data_registro=datetime.now()
            )

            db.session.add(prontuario)
            db.session.commit()

            registrar_auditoria (
                usuario_id=id_profissional,
                acao = "CRIAR_PRONTUARIO",
                detalhes= f"Prontuário criado para consulta {prontuario.consulta_id}"
            )

            return 201
        
@api.route("/<int:id>")
class ProntuarioResource(Resource):
    @jwt_required()
    @api.response(401, "Você não tem permissão visualizar este prontuário.")
    @api.response(404, "Prontuário não encontrado.")
    @api.response(403, "Você não tem permissão para acessar este prontuário.")
    @api.response(204, "Esta consulta não possui prontuário.")

    def get(self, id):
        identificacao = get_jwt()
        id_profissional = identificacao["id"]
        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "profissional")

        if validacao_usuario:
            return 401
        
        else:
            consulta = Consulta.query.get(id)

            if not consulta:
                return 404
            
            if consulta.profissional_id != id_profissional:
                return 403
            
            if not consulta.prontuario:
                return 204

            pront = consulta.prontuario

            return {
                "id": pront.id,
                "consulta_id": pront.consulta_id,
                "anotacoes": pront.anotacoes,
                "prescricao": pront.prescricao,
                "data_registro": pront.data_registro.strftime("%Y-%m-%d %H:%M:%S")
            }, 200
        
@api.route("/paciente/<int:consulta_id>")
class ProntuarioPacienteResource(Resource):
    @jwt_required()
    @api.response(401, "Você não tem permissão visualizar este prontuário.")
    @api.response(404, "Prontuário não encontrado.")
    @api.response(403, "Você não tem permissão para acessar este prontuário.")
    @api.response(204, "Esta consulta não possui prontuário.")

    def get(self, consulta_id):
        identificacao = get_jwt()
        id_paciente = identificacao["id"]
        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "paciente")

        if validacao_usuario:
            return 401
        
        else:
            consulta = Consulta.query.get(consulta_id)

            if not consulta:
                return 404
            
            if consulta.paciente_id != id_paciente:
                return 403
            
            if not consulta.prontuario:
                return 204

            pront = consulta.prontuario

            return {
                "id": pront.id,
                "consulta_id": pront.consulta_id,
                "anotacoes": pront.anotacoes,
                "prescricao": pront.prescricao,
                "data_registro": pront.data_registro.strftime("%Y-%m-%d %H:%M:%S")
            }, 200