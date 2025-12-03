from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app.models import Usuario
from app.services.security import verificar_senha

api = Namespace("auth", description="Autenticação e geração de JWT")

login_model = api.model("Login", {
    "email": fields.String(required=True, description="E-mail do usuário"),
    "senha": fields.String(required=True, description="Senha do usuário")
})

token_model = api.model("Token", {
    "access_token": fields.String(description="Token de acesso JWT")
})

@api.route("/login")
class Login(Resource):
    @api.expect(login_model, validate=True)
    @api.response(200, "Login bem-sucedido", token_model)
    @api.response(401, "E-mail ou senha inválidos")

    def post(self):
        payload = api.payload
        usuario = Usuario.query.filter_by(email=payload["email"]).first()

        if not usuario:
            return {"message": "E-mail ou senha inválidos."}, 401
        
        if not verificar_senha(payload["senha"], usuario.senha):
            return {"message": "E-mail ou senha inválidos."}, 401
        
        token = create_access_token(identity=str(usuario.id),
                                    additional_claims={"id": usuario.id, "perfil": usuario.perfil.value})

        return {"access_token": f"Bearer {token}"}, 200