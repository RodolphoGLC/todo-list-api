from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from datetime import datetime
from typing import Union

from  model import Base

class Tarefa(Base):
    __tablename__ = 'tarefa'

    id = Column("pk_tarefa", Integer, primary_key=True)
    nome = Column(String(140), unique=True)
    descricao = Column(String(140))
    status = Column(String(100))
    data_criacao = Column(DateTime, default=datetime.now())
    # usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    # data_inicio (quando o status mudar de Todo para InProgress)
    # data_termino (quando o status mudar de InProgress para Done)

    # Se existir relacionamento faça como abaixo
    # comentarios = relationship("Comentario")

    def __init__(self, nome:str, descricao:str, status:str, data_criacao:Union[DateTime] ):
                 
        """
        Cria uma Tarefa

        Propriedades:
            nome: nome da tarefa.
            descrição: O que será feito na tarefa
            status: Status da tarefa (To Do, In Progress, Done, Deleted)
            data_criacao: data de quando a tarefa foi criada (será passada no back)
        """
        self.nome = nome
        self.descricao = descricao
        self.status = status
        self.data_criacao = data_criacao
