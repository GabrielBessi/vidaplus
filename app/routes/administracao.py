from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt
from app import db
from app.models import Administrador, Usuario, Paciente, Profissional, Consulta
from app.utils import valida_perfil_usuario, converte_data, mensagem_criacao_sucesso

api = Namespace("administracao", description="Operações relacionadas aos administradores")

cadastro_administrador_entrada = api.model("AdministradorInput", {
    "nome": fields.String(required=True),
    "email": fields.String(required=True),
    "senha": fields.String(required=True),
    "cpf": fields.String(required=False),
    "data_nascimento": fields.String(required=False, example="DD/MM/YYYY"),
    "endereco": fields.String(required=True),
    "telefone": fields.String(required=True, example="11 9XXXX-XXXX")
})

cadastro_administrador_saida = api.model("AdministradorOutput", {
    "id": fields.Integer,
    "nome": fields.String,
    "email": fields.String,
    "perfil": fields.String
})

atualizacao_administrador_entrada = api.model("AdminAtulizacao", {
    "nome": fields.String,
    "email": fields.String,
    "endereco": fields.String,
    "telefone": fields.String
})

@api.route("/cadastro/administrador")
class AdministradorCadastro(Resource):
    @jwt_required()
    @api.expect(cadastro_administrador_entrada)
    @api.response(201, "Novo administrador cadastrado.", cadastro_administrador_saida)
    @api.response(400, "Administrador já existente.")
    @api.response(401, "Apenas administradores podem acessar esta funcionalidade.")

    def post(self):
        identificacao = get_jwt()

        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "administrador")

        if validacao_usuario:
            return validacao_usuario
        
        else:
            payload = api.payload

            if Usuario.query.filter_by(email=payload["email"]).first():
                api.abort(400, "E-mail já cadastrado.")

            if Administrador.query.filter_by(cpf=payload["cpf"]).first():
                api.abort(400, "CPF já cadastrado.")

            usuario = Usuario(
                nome=payload["nome"],
                email=payload["email"],
                senha=payload["senha"],
                perfil="administrador"
            )

            db.session.add(usuario)
            db.session.commit()

            administrador = Administrador(
                id=usuario.id,
                cpf=payload["cpf"],
                data_nascimento=converte_data(payload["data_nascimento"]),
                endereco=payload["endereco"],
                telefone=payload["telefone"]
            )

            db.session.add(administrador)
            db.session.commit()
        
        return {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "perfil": usuario.perfil.value
        }  
    
@api.route("/lista_administradores")
class AdministradoresList(Resource):
    @api.doc(security="Bearer Auth")
    @jwt_required()
    @api.response(401, "Apenas administradores podem acessar esta funcionalidade.")
    @api.response(500, "Erro interno do servidor.")

    def get(self):
        """Retorna uma lista de administradores"""
        identificacao = get_jwt()
        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "administrador")
        
        if validacao_usuario:
            return validacao_usuario
        
        else:
            consultas_administradores = Administrador.query.all()
            resposta = []

            for a in consultas_administradores:
                resposta.append({
                    "id": a.id,
                    "nome": a.usuario.nome,
                    "email": a.usuario.email,
                    "cpf": a.cpf,
                    "data_nascimento": a.data_nascimento.strftime("%Y-%m-%d"),
                    "endereco": a.endereco,
                    "telefone": a.telefone
                })

        return resposta, 200

@api.route("/lista_administradores/<int:id>")
class AdministradorResource(Resource):
    @api.doc(security="Bearer Auth")
    @jwt_required()
    @api.response(401, "Apenas administradores podem acessar esta funcionalidade.")
    @api.response(404, "Administrador não encontrado.")
    @api.response(500, "Erro interno do servidor.")

    def get(self, id):
        """Retorna os dados de um administrador específico"""
        identificacao = get_jwt()
        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "administrador")
        
        if validacao_usuario:
            return validacao_usuario
        
        else:
            administrador = Administrador.query.get_or_404(id)

            resposta = {
                "id": administrador.id,
                "nome": administrador.usuario.nome,
                "email": administrador.usuario.email,
                "cpf": administrador.cpf,
                "data_nascimento": administrador.data_nascimento.strftime("%Y-%m-%d"),
                "endereco": administrador.endereco,
                "telefone": administrador.telefone
            }

        return resposta, 200

    @api.expect(atualizacao_administrador_entrada)
    @jwt_required()
    def put(self, id):
        """Atualiza informações de um administrador"""

        identificacao = get_jwt()
        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "administrador")

        if validacao_usuario:
            return validacao_usuario
        
        else:
            administrador = Administrador.query.get_or_404(id)

            payload = api.payload
            
            if "nome" in payload:
                administrador.usuario.nome = payload["nome"]

            if "email" in payload:
                if Usuario.query.filter(Usuario.email == payload["email"], Usuario.id != administrador.id).first():
                    return {"message": "E-mail já cadastrado."}, 400
                else:
                    administrador.usuario.email = payload["email"]
            
            if "endereco" in payload:
                administrador.endereco = payload["endereco"]

            if "telefone" in payload:
                administrador.telefone = payload["telefone"]

            db.session.commit()
    
        return {"message": f"Administrador {id} atualizado"}, 200   
    
@api.route("/lista_pacientes")
class AdministradorListaPacientes(Resource):
    @jwt_required()
    @api.response(401, "Apenas administradores podem acessar esta funcionalidade.")
    @api.response(500, "Erro interno do servidor.")

    def get(self):
        """Retorna uma lista de pacientes"""
        identificacao = get_jwt()
        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "administrador")
        
        if validacao_usuario:
            return validacao_usuario
        
        else:
            consulta_pacientes = Paciente.query.all()
            resposta = []

            for p in consulta_pacientes:
                resposta.append({
                    "id": p.id,
                    "nome": p.usuario.nome,
                    "email": p.usuario.email,
                    "cpf": p.cpf,
                    "data_nascimento": p.data_nascimento.strftime("%Y-%m-%d"),
                    "endereco": p.endereco,
                    "telefone": p.telefone
                })

        return resposta, 200
    
@api.route("/lista_pacientes/<int:id>")
class AdministradorPacienteResource(Resource):
    @jwt_required()
    @api.response(401, "Apenas administradores podem acessar esta funcionalidade.")
    @api.response(404, "Paciente não encontrado.")
    @api.response(500, "Erro interno do servidor.")

    def get(self, id):
        """Retorna os dados de um paciente específico"""
        identificacao = get_jwt()
        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "administrador")
        
        if validacao_usuario:
            return validacao_usuario
        
        else:
            paciente = Paciente.query.get_or_404(id)

            resposta = {
                "id": paciente.id,
                "nome": paciente.usuario.nome,
                "email": paciente.usuario.email,
                "cpf": paciente.cpf,
                "data_nascimento": paciente.data_nascimento.strftime("%Y-%m-%d"),
                "endereco": paciente.endereco,
                "telefone": paciente.telefone
            }

        return resposta, 200
    
@api.route("/lista_profissionais")
class AdministradorListaProfissionais(Resource):
    @jwt_required()
    @api.response(401, "Apenas administradores podem acessar esta funcionalidade.")
    @api.response(500, "Erro interno do servidor.")

    def get(self):
        """Retorna uma lista de profissionais de saúde"""
        identificacao = get_jwt()
        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "administrador")
        
        if validacao_usuario:
            return validacao_usuario
        
        else:
            consulta_profissionais = Profissional.query.all()
            resposta = []

            for p in consulta_profissionais:
                resposta.append({
                    "id": p.id,
                    "nome": p.usuario.nome,
                    "email": p.usuario.email,
                    "conselho": p.conselho,
                    "numero_conselho": p.numero_conselho,
                    "especialidade": p.especialidade
                })

        return resposta, 200

@api.route("/lista_profissionais/<int:id>")
class AdministradorProfissionalResource(Resource):
    @jwt_required()
    @api.response(401, "Apenas administradores podem acessar esta funcionalidade.")
    @api.response(404, "Profissional não encontrado.")
    @api.response(500, "Erro interno do servidor.")

    def get(self, id):
        """Retorna os dados de um profissional específico"""
        identificacao = get_jwt()
        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "administrador")
        
        if validacao_usuario:
            return validacao_usuario
        
        else:
            profissional = Profissional.query.get_or_404(id)

            resposta = {
                "id": profissional.id,
                "nome": profissional.usuario.nome,
                "email": profissional.usuario.email,
                "conselho": profissional.conselho,
                "numero_conselho": profissional.numero_conselho,
                "especialidade": profissional.especialidade
            }

        return resposta, 200

@api.route("/lista_consultas")
class AdministradorListaConsultas(Resource):
    @jwt_required()
    @api.response(401, "Apenas administradores podem acessar esta funcionalidade.")
    @api.response(500, "Erro interno do servidor.")

    def get(self):
        """Retorna uma lista de todas as consultas agendadas"""
        identificacao = get_jwt()
        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "administrador")
        
        if validacao_usuario:
            return validacao_usuario
        
        else:
            consulta_consultas = Consulta.query.all()
            resposta = []

            for c in consulta_consultas:
                resposta.append({
                    "id": c.id,
                    "paciente_id": c.paciente_id,
                    "profissional_id": c.profissional_id,
                    "data": c.data.strftime("%Y-%m-%d"),
                    "hora": c.hora.strftime("%H:%M:%S"),
                    "status": c.status.value,
                    "tipo": c.tipo
                })

        return resposta, 200
    
@api.route("/lista_consultas/<int:id>")
class AdministradorConsultaResource(Resource):
    @jwt_required()
    @api.response(401, "Apenas administradores podem acessar esta funcionalidade.")
    @api.response(404, "Consulta não encontrada.")
    @api.response(500, "Erro interno do servidor.")

    def get(self, id):
        """Retorna os dados de uma consulta específica"""
        identificacao = get_jwt()
        validacao_usuario = valida_perfil_usuario(identificacao, identificacao.get("perfil"), "administrador")
        
        if validacao_usuario:
            return validacao_usuario
        
        else:
            consulta = Consulta.query.get_or_404(id)

            resposta = {
                "id": consulta.id,
                "paciente_id": consulta.paciente_id,
                "profissional_id": consulta.profissional_id,
                "data": consulta.data.strftime("%Y-%m-%d"),
                "hora": consulta.hora.strftime("%H:%M:%S"),
                "status": consulta.status.value,
                "tipo": consulta.tipo
            }

        return resposta, 200