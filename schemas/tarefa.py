from pydantic import BaseModel
from typing import Optional, List
from model.tarefa import Tarefa

class TarefaSchema(BaseModel):
    descricao: str
    nome: str
    status: str


class TaredaAdicaoSchema(BaseModel):
    """ 
        Define como uma nova tarefa a ser inserida deve ser representada
    """
    nome: str = "Tarefa ABC"
    descricao: str = "Descrição da tarefa ABC"


class TarefaBuscaSchema(BaseModel):
    """ 
        Define que a busca deverá ser feita a partir do nome da tarefa
    """
    nome: str = "Tarefa ABC"


class TarefaDeleteSchema(BaseModel):
    """ 
        Define que a busca deverá ser feita a partir do nome da tarefa
    """
    id: int


class ListagemTarefasSchema(BaseModel):
    """ 
        Define como será o retorno da lista de tarefas.
    """
    tarefas: List[TarefaSchema]


class TarefaViewSchema(BaseModel):
    """ 
        Define como um Tarefa será retornada.
    """
    id: int = 1
    nome: str = "Tarefa ABC"
    descricao: str = "Descrição da Tarefa ABC"
    status: str = "To Do"


class TarefaDelSchema(BaseModel):
    """ 
        Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    mesage: str
    nome: str


class TarefaUpdateSchema(BaseModel):
    """ 
        Define como deve ser a estrutura do dado para alterar o status
    """
    id: int
    status: str


class TarefasPorStatusResponse(BaseModel):
    """ Contagem de tarefas por status """
    Ready: int
    Doing: int
    Done: int


def apresenta_tarefa(tarefa: Tarefa):
    """ 
        Retorna uma representação do Tarefa seguindo o schema definido em
        TarefaViewSchema.
    """
    return {
        "id": tarefa.id,
        "nome": tarefa.nome,
        "descricao": tarefa.descricao,
        "status": tarefa.status,
    }


def apresenta_tarefas(tarefas: List[Tarefa]):
    """ 
        Retorna uma representação do Tarefa seguindo o schema definido
        em TarefaViewSchema.
    """
    result = []
    for tarefa in tarefas:
        result.append({
            "id": tarefa.id,
            "nome": tarefa.nome,
            "descricao": tarefa.descricao,
            "status": tarefa.status,
        })

    return {"Tarefas": result}
