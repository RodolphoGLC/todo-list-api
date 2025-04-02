from sqlalchemy import Column, Integer, String, ForeignKey
from  model import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column("pk_usuario", Integer, primary_key=True)
    nome = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    senha = Column(String(255))

    # Remover depois
    tarefas = Column(Integer, ForeignKey("tarefa.pk_tarefa"))

    def __init__(self, nome:str, email:str, senha:str ):
                 
        """
        Cria uma Usuário
        """
        self.nome = nome
        self.email = email
        self.senha = senha
