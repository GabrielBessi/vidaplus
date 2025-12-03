from flask_restx import Namespace, Resource, fields
from app import db
from app.models import Usuario, Paciente, Profissional
from app.services.security import gerar_hash_senha
from app.utils import converte_data, mensagem_criacao_sucesso
from app.audit import registrar_auditoria

api = Namespace('usuarios', description="Gerenciamento de usuários")

usuario_input_default = api.model("UsuarioInput", {
    "nome": fields.String(required=True),
    "email": fields.String(required=True),
    "senha": fields.String(required=True),
    "cpf": fields.String(required=False),
    "data_nascimento": fields.String(required=False, example="DD/MM/YYYY"),
    "endereco": fields.String(required=True),
    "telefone": fields.String(required=True)
})

usuario_input_profissional = api.model("UsuarioInputProfissional", {
    "nome": fields.String(required=True),
    "email": fields.String(required=True),
    "senha": fields.String(required=True),
    "conselho": fields.String(required=True),
    "numero_conselho": fields.String(required=True),
    "especialidade": fields.String(required=True)
})

usuario_output_default = api.model("UsuarioOutput", {
    "id": fields.Integer,
    "nome": fields.String,
    "email": fields.String,
    "perfil": fields.String
})

@api.route('/cadastro/profissional')
class UsuarioCreateProfissional(Resource):
    @api.expect(usuario_input_profissional)
    @api.marshal_with(usuario_output_default, code=201)

    def post(self):
        data = api.payload

        if Usuario.query.filter_by(email=data["email"]).first():
            api.abort(400, "E-mail já cadastrado.")

        usuario = Usuario(
            nome=data["nome"],
            email=data["email"],
            senha=gerar_hash_senha(data["senha"]), #criptografa a senha
            perfil="profissional"
        )

        db.session.add(usuario)
        db.session.commit()

        profissional = Profissional(
            id=usuario.id,
            conselho=data["conselho"],
            numero_conselho=data["numero_conselho"],
            especialidade=data["especialidade"]
        )
        db.session.add(profissional)
        db.session.commit()

        registrar_auditoria (
            usuario_id=usuario.id,
            acao = "NOVO_PROFISSIONAL",
            detalhes= f"Funcionario criado: {usuario.id}"
        )        

        return mensagem_criacao_sucesso("Profissional", usuario)


@api.route('/cadastro')
class UsuarioCreate(Resource):
    @api.expect(usuario_input_default)
    @api.marshal_with(usuario_output_default, code=201)

    def post(self):
        data = api.payload
        perfil_usuario = data["perfil"]

        if Usuario.query.filter_by(email=data["email"]).first():
            api.abort(400, "E-mail já cadastrado.")

        usuario = Usuario(
            nome=data["nome"],
            email=data["email"],
            senha=gerar_hash_senha(data["senha"]), #criptografa a senha
            perfil="paciente"
        )

        db.session.add(usuario)
        db.session.commit()

        paciente = Paciente(
                id=usuario.id,
                cpf=data["cpf"],
                data_nascimento=converte_data(data["data_nascimento"]),
                endereco=data["endereco"],
                telefone=data["telefone"]
            )
        
        db.session.add(paciente)
        db.session.commit()
        
        registrar_auditoria (
            usuario_id=usuario.id,
            acao = "NOVO_PACIENTE",
            detalhes= f"Paciente criado: {usuario.id}"
        )

        return mensagem_criacao_sucesso(perfil_usuario, usuario)

