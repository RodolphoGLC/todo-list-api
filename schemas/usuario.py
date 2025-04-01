from pydantic import BaseModel

from model.usuario import Usuario

class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str

class LoginSchema(BaseModel):
    email: str
    senha: str

def apresenta_usuario(usuario: Usuario):
    """ 
        Retorna uma representação do Usuario seguindo o schema definido em UsuarioSchema.
    """
    return {
        "nome": usuario.nome,
        "email": usuario.email,
        "senha": usuario.senha
    }