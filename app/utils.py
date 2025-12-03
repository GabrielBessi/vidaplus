from datetime import datetime

def converte_data(data: str) -> datetime:
   data = datetime.strptime(data, "%d/%m/%Y")
   data_formatada = data.strftime("%Y-%m-%d")

   return data_formatada

def valida_perfil_usuario (identificacao, identificacao_perfil, tipo_perfil):
   match tipo_perfil:
      case "paciente":
         if not identificacao or identificacao_perfil != tipo_perfil:
            return {"message": "Apenas pacientes podem acessar esta funcionalidade."}, 401
      case "administrador":
         if not identificacao or identificacao_perfil != tipo_perfil:
            return {"message": "Apenas administradores podem acessar esta funcionalidade."}, 401
      case "profissional":
         if not identificacao or identificacao_perfil != tipo_perfil:
            return {"message": "Apenas profissionais podem acessar esta funcionalidade."}, 401

def valida_data_hora(data_hora_str):
   try:
       data_hora = datetime.fromisoformat(data_hora_str)
       return data_hora
   except Exception:
       return {"message": "Formato de data_hora inválido. Use ISO 8601. Ex: 2024-12-31T14:30:00"}, 400
   
def mensagem_criacao_sucesso(entidade, dados):
   return {
       "mensagem": f"{entidade} criado com sucesso.",
       "dados": dados
   }, 201