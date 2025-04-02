from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional
from model import Base
from model.usuario import Usuario

class Tarefa(Base):
    __tablename__ = 'tarefa'

    id = Column("pk_tarefa", Integer, primary_key=True)
    nome = Column(String(140), unique=True)
    descricao = Column(String(140))
    status = Column(String(100))
    data_criacao = Column(DateTime, default=datetime.now)

    # Adicionando corretamente a ForeignKey para Usuario
    usuario = Column(Integer, ForeignKey("usuarios.pk_usuario"))

    def __init__(self, nome: str, descricao: str, status: str):
        self.nome = nome
        self.descricao = descricao
        self.status = status
        self.data_criacao = datetime.now()
        # self.usuario = None

    def relate_user(self, user: Usuario):
        """Relaciona a tarefa a um usuário."""
        self.usuario = user
