from werkzeug.security import generate_password_hash, check_password_hash

def gerar_hash_senha(senha: str) -> str:
    return generate_password_hash(senha)

def verificar_senha(senha: str, hash_senha: str) -> bool:
    return check_password_hash(hash_senha, senha)