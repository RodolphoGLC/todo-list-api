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

info = Info(title="Task List API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

home_tag = Tag(name="Documentation",
               description="Documentation selection: Swagger, Redoc, or RapiDoc")
tarefa_tag = Tag(
    name="Tarefa", description="Adding, viewing, and removing tasks from the database")


@app.get('/', tags=[home_tag])
def home():
    """Redirects to /openapi, a page that allows the choice of documentation style."""
    return redirect('/openapi')

# Get Tarefas


@app.get('/tarefas', tags=[tarefa_tag])
def get_tarefas():
    """
    Get a list of tasks

    Returns a list of all registered tasks
    """
    logger.debug("Fetching tasks")

    session = Session()
    tarefas = session.query(Tarefa).all()

    if not tarefas:
        logger.debug("No tasks found.")
        session.close()
        return {"tarefas": []}, 200
    else:
        logger.debug(f"{len(tarefas)} tasks found")
        session.close()
        return {"tarefas": apresenta_tarefas(tarefas)}, 200
    
@app.get('/tarefa/id', tags=[tarefa_tag])
def get_tarefas():
    """
    Get a list of tasks
    
    Returns a list of all registered tasks
    """
    logger.debug("Fetching tasks")

    session = Session()
    tarefas = session.query(Tarefa).all()

    if not tarefas:
        logger.debug("No tasks found.")
        session.close()
        return {"tarefas": []}, 200
    else:
        logger.debug(f"{len(tarefas)} tasks found")
        session.close()
        return {"tarefas": apresenta_tarefas(tarefas)}, 200


# Post Tarefa
@app.post('/tarefa', tags=[tarefa_tag],
          responses={"200": TarefaViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_tarefa(form: TarefaSchema):
    """
    Adds a new task to the database

    Returns a representation of the tasks and associated comments.
    """

    tarefa = Tarefa(
        nome=form.nome,
        descricao=form.descricao,
        status=form.status,
        data_criacao=datetime.now()
    )

    logger.debug(f"Adding task with name: '{tarefa.nome}'")

    try:
        session = Session()

        session.add(tarefa)

        session.commit()

        logger.debug(f"Added task with name: '{tarefa.nome}'")

        return apresenta_tarefa(tarefa), 200

    except IntegrityError as e:
        error_msg = "Task with the same name already saved in the database :/"
        logger.warning(
            f"Error adding task '{tarefa.nome}', {error_msg}")
        return {"message": error_msg}, 409

    except Exception as e:
        error_msg = "Could not save new item :/"
        logger.warning(
            f"Error adding task '{tarefa.nome}', {error_msg}")
        return {"message": error_msg}, 400

    finally:
        session.close()


@app.delete('/tarefa', tags=[tarefa_tag], responses={"200": TarefaViewSchema, "404": ErrorSchema})
def delete_tarefa(query: TarefaDeleteSchema):
    """Deletes a task by ID"""
    id = query.id

    logger.warning(f"Error deleting task {id}")

    session = Session()
    tarefa = session.query(Tarefa).filter(
        Tarefa.id == id).first()  # Find the task

    if not tarefa:
        error_msg = "Task not found :/"
        logger.warning(f"Error deleting task {id}, {error_msg}")
        return {"message": error_msg}, 404

    logger.info(f"Task found: {tarefa.nome}")

    # Delete the task
    session.delete(tarefa)
    session.commit()
    session.close()

    logger.debug(f"Task {id} deleted successfully")
    return {"message": f"Task '{tarefa.nome}' deleted successfully"}, 200


# @app.put('/tarefa', tags=[tarefa_tag], responses={"200": TarefaViewSchema, "404": ErrorSchema})
# def update_tarefa_status(tarefa_id: int, form: TarefaUpdateSchema):
#     """Updates the status of a task by ID"""
#     session = Session()
#     try:
#         tarefa = session.query(Tarefa).filter_by(id=tarefa_id).first()

#         if not tarefa:
#             error_msg = "Task not found :/"
#             logger.warning(f"Error updating status of task {tarefa_id}, {error_msg}")
#             return {"message": error_msg}, 404

#         tarefa.status = form.status
#         session.commit()  # Removed the argument `tarefa`
#         logger.debug(f"Status of task {tarefa_id} updated to {form.status}")

#         return apresenta_tarefa(tarefa), 200
#     except Exception as e:
#         session.rollback()  # Ensures the transaction is reverted in case of an error
#         logger.error(f"Error updating task {tarefa_id}: {str(e)}")
#         return {"message": "Internal server error"}, 500
#     finally:
#         session.close()  # Properly closes the session


# Get Task by Name (Optional)
# @app.get('/tarefa/<string:nome>', tags=[tarefa_tag], responses={"200": TarefaViewSchema, "404": ErrorSchema})
# def get_tarefa_by_name(nome: str):
#     """Searches for a task by name"""
#     session = Session()
#     tarefa = session.query(Tarefa).filter(
#         Tarefa.nome.ilike(f"%{nome}%")).first()

#     if not tarefa:
#         error_msg = "Task not found :/"
#         logger.warning(f"Error searching for task with name '{nome}', {error_msg}")
#         return {"message": error_msg}, 404

#     logger.debug(f"Task found: {tarefa.nome}")
#     return apresenta_tarefa(tarefa), 200


# Get Total Tasks by Status
@app.get('/tarefas/status', tags=[tarefa_tag], responses={"200": TarefasPorStatusResponse, "500": ErrorSchema})
def get_tarefas_por_status():
    """Returns the total count of tasks by status"""
    session = Session()

    try:
        # Query all tasks
        resultados: list[Tarefa] = session.query(Tarefa).all()

        # Ensuring that all statuses appear in the dictionary (even if there are 0 tasks)
        status_possiveis = ["Ready", "Doing", "Done"]
        resposta = {status: sum(
            1 for tarefa in resultados if tarefa.status == status) for status in status_possiveis}

        logger.debug(f"Task count by status: {resposta}")

        return resposta, 200

    except Exception as e:
        logger.error(f"Error fetching tasks by status: {str(e)}")
        return {"message": "Internal error processing the request"}, 500

    finally:
        session.close()  # Close the session to avoid open connections
