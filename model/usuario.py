from sqlalchemy import Column, Integer, String
from  model import Base
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    senha = Column(String(255))

    def __init__(self, nome:str, email:str, senha:str ):
                 
        """
        Cria uma Usuário
        """
        self.nome = nome
        self.email = email
        self.senha = senha
