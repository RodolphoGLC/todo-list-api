from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from model import Session, Tarefa
from logger import logger
from schemas import *
from flask_cors import CORS

info = Info(title="Lista Tarefas API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

home_tag = Tag(name="Documentação",
               description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
tarefa_tag = Tag(
    name="Tarefa", description="Adição, visualização e remoção de tarefas à base")


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')

# Get Tarefas


@app.get('/tarefas', tags=[tarefa_tag])
def get_tarefas():
    """
    Retornar uma lista com todas as tarefas cadastradas
    """
    logger.debug("Obtendo as tarefas")

    session = Session()
    tarefas = session.query(Tarefa).all()

    if not tarefas:
        logger.debug("Nenhuma tarefa encontrada.")
        return {"tarefas": []}, 200
    else:
        logger.debug(f"{len(tarefas)} tarefas encontradas")
        return {"tarefas": apresenta_tarefas(tarefas)}, 200


# Post Tarefa
@app.post('/tarefa', tags=[tarefa_tag],
          responses={"200": TarefaViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_tarefa(form: TarefaSchema):
    """Adiciona um novo Tarefa à base de dados

    Retorna uma representação dos tarefas e comentários associados.
    """
    tarefa = Tarefa(
        nome=form.nome,
        descricao=form.descricao,
        status=form.status,
        data_criacao=datetime.now()
    )

    logger.debug(f"Adicionando tarefa com o nome: '{tarefa.nome}'")

    try:
        session = Session()

        session.add(tarefa)

        session.commit()

        logger.debug(f"Adicionado tarefa de nome: '{tarefa.nome}'")

        return apresenta_tarefa(tarefa), 200

    except IntegrityError as e:
        error_msg = "Tarefa de mesmo nome já salvo na base :/"
        logger.warning(
            f"Erro ao adicionar tarefa '{tarefa.nome}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(
            f"Erro ao adicionar tarefa '{tarefa.nome}', {error_msg}")
        return {"mesage": error_msg}, 400

# Delete Tarefa
@app.delete('/tarefa/delete/{tarefa_id}', tags=[tarefa_tag], responses={"200": TarefaViewSchema, "404": ErrorSchema})
def delete_tarefa():
    """Deleta uma tarefa pelo ID"""
    session = Session()
    tarefa = session.query(Tarefa).filter_by(id=tarefa_id).first()

    if not tarefa:
        error_msg = "Tarefa não encontrada :/"
        logger.warning(f"Erro ao deletar tarefa {tarefa_id}, {error_msg}")
        return {"message": error_msg}, 404

    session.delete(tarefa)
    session.commit()
    logger.debug(f"Tarefa {tarefa_id} deletada com sucesso")

    return {"message": "Tarefa deletada com sucesso"}, 200


# Update Tarefa (Alterar Status)
@app.put('/tarefa/<int:tarefa_id>', tags=[tarefa_tag], responses={"200": TarefaViewSchema, "404": ErrorSchema})
def update_tarefa_status(tarefa_id: int, form: TarefaUpdateSchema):
    """Atualiza o status de uma tarefa pelo ID"""
    session = Session()
    tarefa = session.query(Tarefa).filter_by(id=tarefa_id).first()

    if not tarefa:
        error_msg = "Tarefa não encontrada :/"
        logger.warning(
            f"Erro ao atualizar status da tarefa {tarefa_id}, {error_msg}")
        return {"message": error_msg}, 404

    tarefa.status = form.status
    session.commit()
    logger.debug(f"Status da tarefa {tarefa_id} atualizado para {form.status}")

    return apresenta_tarefa(tarefa), 200


# Get Tarefas By Name (Opcional)
# @app.get('/tarefa/<string:nome>', tags=[tarefa_tag], responses={"200": TarefaViewSchema, "404": ErrorSchema})
# def get_tarefa_by_name(nome: str):
#     """Busca uma tarefa pelo nome"""
#     session = Session()
#     tarefa = session.query(Tarefa).filter(
#         Tarefa.nome.ilike(f"%{nome}%")).first()

#     if not tarefa:
#         error_msg = "Tarefa não encontrada :/"
#         logger.warning(f"Erro ao buscar tarefa com nome '{nome}', {error_msg}")
#         return {"message": error_msg}, 404

#     logger.debug(f"Tarefa encontrada: {tarefa.nome}")
#     return apresenta_tarefa(tarefa), 200


# Get Total de Tarefas por Status
@app.get('/tarefas/status', tags=[tarefa_tag], responses={"200": TarefasPorStatusResponse, "500": ErrorSchema})
def get_tarefas_por_status():
    """Retorna a contagem total de tarefas por status"""
    session = Session()

    try:
        # Consulta agrupando pelo status
        resultados = session.query(Tarefa.status, func.count(
            Tarefa.id)).group_by(Tarefa.status).all()

        # Estruturando a resposta como um dicionário
        contagem_por_status = {status: count for status, count in resultados}

        # Garantindo que todos os status apareçam no dicionário (mesmo que tenham 0 tarefas)
        status_possiveis = ["To Do", "In Progress", "Done", "Archived"]
        resposta_final = {status: contagem_por_status.get(
            status, 0) for status in status_possiveis}

        logger.debug(f"Contagem de tarefas por status: {resposta_final}")

        return TarefasPorStatusResponse(**resposta_final), 200

    except Exception as e:
        logger.error(f"Erro ao buscar tarefas por status: {str(e)}")
        return {"message": "Erro interno ao processar a solicitação"}, 500

    finally:
        session.close()  # Fecha a sessão para evitar conexões abertas
