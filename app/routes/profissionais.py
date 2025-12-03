from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt
from app.models import Profissional
from app import db
from app.utils import valida_perfil_usuario
from audit import registrar_auditoria

api = Namespace("profissionais", description="Operações relacionadas aos profissionais de saúde")

consulta_profissional_output = api.model("ConsultaProfissionalOut", {
    "id": fields.Integer,
    "nome": fields.String,
    "email": fields.String,
    "conselho": fields.String,
    "numero_conselho": fields.String,
    "especialidade": fields.String
})

@api.route("/")
class ProfissionalResource(Resource):
    @api.response(200, "Profissional retornado com sucesso", consulta_profissional_output)
    @api.response(401, "Você não tem permissão para este acesso.")
    @api.response(404, "Não foi possível encontrar o profissional de saúde solicitado.")
    @api.response(500, "Erro interno do servidor.")
    @jwt_required()

    def get(self):
        identificacao = get_jwt()

        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "profissional")

        if validacao_usuario:
            return validacao_usuario
        
        else:
            id_profissional = identificacao["id"]
            profissional = Profissional.query.get_or_404(id_profissional)

            return {
                "id": profissional.id,
                "nome": profissional.usuario.nome,
                "email": profissional.usuario.email,
                "conselho": profissional.conselho,
                "numero_conselho": profissional.numero_conselho,
                "especialidade": profissional.especialidade
            }, 200
        
    def put(self):
        identificacao = get_jwt()

        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "profissional")

        if validacao_usuario:
            return validacao_usuario
        
        else:
            id_profissional = identificacao["id"]
            profissional = Profissional.query.get_or_404(id_profissional)
            payload = api.payload

            if "conselho" in payload:
                profissional.conselho = payload["conselho"]

            if "numero_conselho" in payload:
                profissional.numero_conselho = payload["numero_conselho"]

            if "especialidade" in payload:
                profissional.especialidade = payload["especialidade"]

            db.session.commit()

            registrar_auditoria (
                usuario_id=id_profissional,
                acao = "ATUALIZAR_PROFISSIONAL",
                detalhes= f"Profissional atualizado: {id_profissional}"
            )            

            return {
                "id": profissional.id,
                "nome": profissional.usuario.nome,
                "email": profissional.usuario.email,
                "conselho": profissional.conselho,
                "numero_conselho": profissional.numero_conselho,
                "especialidade": profissional.especialidade
            }, 200
