from flask_restx import Namespace, Resource
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt
from app import db
from app.models import Consulta, Telemedicina, Usuario
from app.utils import valida_perfil_usuario
from datetime import datetime

api = Namespace("telemedicina", description="Serviços relacionados à telemedicina")

@api.route("/iniciar/<int:consulta_id>")
class TelemedicinaService(Resource):
    @jwt_required()
    @api.response(500, "Erro no servidor.")

    def post(self, consulta_id):
        identificacao = get_jwt()

        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "profissional")

        if validacao_usuario:
            return {"message": "Apenas profissionais podem iniciar a sessão"}, 401
        
        else:
            id_usuario = identificacao["id"]
            usuario = Usuario.query.get(id_usuario)

            if not usuario.profissional:
                return {"message": "Não tem permissão para iniciar esta sessão"}, 403
            
            consulta = Consulta.query.get_or_404(consulta_id)
            
            if consulta.profissional_id != usuario.profissional.id:
                return {"message": "Não tem permissão para iniciar esta sessão"}, 403

            if consulta.telemedicina:
                return {"erro": "Sessão já criada", "sessao": consulta.telemedicina[0].url_sala}, 400
            
        import uuid
        codigo_sala = str(uuid.uuid4())
        url = f"https://meet.jit.si/{codigo_sala}" #url fake apenas para exemplo

        sessao = Telemedicina (
            consulta_id = consulta_id,
            codigo_sala = codigo_sala,
            url_sala = url
        )

        db.session.add(sessao)
        db.session.commit()

        return {"mensagem": "Sessão iniciada",
                "url_sala": url,
                "codigo_sala": codigo_sala}
    
@api.route("/entrar/<int:consulta_id>")
class TelemedicinaPacienteService(Resource):
    @jwt_required()
    @api.response(401, "Apenas paciente autorizado pode entrar na sala.")
    @api.response(400, "Sessão não iniciada.")
    @api.response(403, "Você não pertence a esta consulta")

    def get(self, consulta_id):
        identificacao = get_jwt()

        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "paciente")

        if validacao_usuario:
            return 401
        
        else:
            usuario_id = identificacao["id"]
            consulta = Consulta.query.get_or_404(consulta_id)
            sessao = consulta.telemedicina[0]

            if not sessao or not sessao.ativa:
                return {"message": "Já existe uma sessão ativa"}, 400
            
            if consulta.paciente.id != usuario_id and consulta.profissional.usuario.id != usuario_id:
                return {"message": "Não tem permissão para essa sessão"}, 403
            
            return {"url_sala": sessao.url_sala,
                    "consulta_id": consulta_id}, 200
        
@api.route("/encerrar/<int:consulta_id>")
class TelemedicinaProfissionalService(Resource):
    @jwt_required()
    @api.response(401, "Apenas profissionais podem encerrar sessão.")
    @api.response(404, "Não foi encontrado sessão em aberto.")
    @api.response(200, "Sessão encerrada com sucesso.")

    def post(self, consulta_id):
        identificacao = get_jwt()
        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "profissional")

        if validacao_usuario:
            return 401
        
        else:
            consulta = Consulta.query.get_or_404(consulta_id)
            sessao = consulta.telemedicina[0]

            if not sessao:
                return {"message": "Sessão não encontrada."}, 404
            
            sessao.ativa = False
            sessao.encerrada_em = datetime.now()

            db.session.commit()

            return {
                "ativa": sessao.ativa,
                "encerrada_em": sessao.encerrada_em.isoformat()
            }, 200