from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from model import Session, Tarefa, Usuario
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
usuario_tag = Tag(
    name="Usuário", description="Endpoints de usuário e autenticação")


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
    # logger.debug("Fetching tasks")

    session = Session()
    tarefas = session.query(Tarefa).all()

    if not tarefas:
        logger.debug("No tasks found.")
        session.close()
        return {'list': apresenta_tarefas([])}, 200
    else:
        logger.debug(f"{len(tarefas)} tasks found")
        session.close()
        return {"list": apresenta_tarefas(tarefas)}, 200


@app.post('/tarefa', tags=[tarefa_tag],
          responses={"200": TarefaViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_tarefa(form: TarefaSchema):
    """
    Adds a new task to the database

    Returns a representation of the tasks.
    """
    existing_task = None
    existing_user = None

    try:
        session = Session()
        existing_task = session.query(Tarefa).filter(Tarefa.nome == form.nome).one_or_none()
        existing_user = session.query(Usuario).filter(Usuario.email == form.emailUsuario).one_or_none()

        if existing_task:
            error_msg = f"Task with the name '{form.nome}' already exists in the database."
            logger.warning(error_msg)
            return {"message": error_msg}, 409

        tarefa = Tarefa(
            nome=form.nome,
            descricao=form.descricao,
            status=form.status,
        )

        if existing_user:
            tarefa.usuario = existing_user.id
        else:
            error_msg = "User Not Found."
            logger.warning(error_msg)
            return {"message": error_msg}, 404

        logger.debug(f"Adding task with name: '{tarefa.nome}'")

        session.add(tarefa)
        session.commit()

        logger.debug(f"Added task with name: '{tarefa.nome}'")
        return apresenta_tarefa(tarefa), 200

    except Exception as e:
        error_msg = "Could not save new item :/"
        logger.warning(f"Error adding task: {error_msg}, Exception: {str(e)}")
        return {"message": error_msg}, 400


@app.delete('/tarefa', tags=[tarefa_tag], responses={"200": TarefaViewSchema, "404": ErrorSchema})
def delete_tarefa(query: TarefaDeleteSchema):
    """Deletes a task by ID"""
    id = query.id

    session = Session()
    tarefa = session.query(Tarefa).filter(Tarefa.id == id).first()

    if not tarefa:
        error_msg = "Task not found :/"
        logger.warning(f"Error deleting task {id}, {error_msg}")
        return {"error": error_msg}, 404

    session.delete(tarefa)
    session.commit()
    session.close()

    logger.debug(f"Task {id} deleted successfully")
    return {"message": f"Task '{tarefa.nome}' deleted successfully"}, 200


@app.get('/tarefas/status', tags=[tarefa_tag], responses={"200": TarefasPorStatusResponse, "500": ErrorSchema})
def get_tarefas_por_status():
    """Returns the total count of tasks by status"""
    session = Session()

    try:
        resultados: list[Tarefa] = session.query(Tarefa).all()

        status_possiveis = ["Ready", "Doing", "Done"]
        resposta = {status: sum(
            1 for tarefa in resultados if tarefa.status == status) for status in status_possiveis}

        logger.debug(f"Task count by status: {resposta}")

        return resposta, 200

    except Exception as e:
        logger.error(f"Error fetching tasks by status: {str(e)}")
        return {"message": "Internal error processing the request"}, 500

    finally:
        session.close()


@app.put('/tarefa', tags=[tarefa_tag], responses={"200": TarefaViewSchema, "404": ErrorSchema})
def update_tarefa_status(form: TarefaUpdateSchema):
    """Atualiza o status de uma tarefa pelo ID"""

    session = Session()

    id = form.id

    try:
        tarefa = session.query(Tarefa).filter(Tarefa.id == id).first()

        if not tarefa:
            error_msg = "Tarefa não encontrada :/"
            logger.warning(
                f"Erro ao atualizar status da tarefa {id}, {error_msg}")
            return {"message": error_msg}, 404

        tarefa.status = form.status
        session.commit()

        logger.debug(
            f"Status da tarefa {id} atualizado para {form.status}")

        return apresenta_tarefa(tarefa), 200

    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao atualizar tarefa {id}: {str(e)}")
        return {"message": "Erro interno no servidor"}, 500

    finally:
        session.close()


@app.post('/usuario', tags=[usuario_tag], responses={"200": UsuarioSchema, "404": ErrorSchema})
def post_usuario(form: UsuarioSchema):
    """Cria um usuário no sistema"""

    existing_user = None

    try:
        session = Session()
        existing_user = session.query(Usuario).filter(Usuario.email == form.email).one_or_none()

        if existing_user:
            error_msg = f"User with this email '{form.email}' already exist in the database"
            logger.warning(error_msg)
            return {"message": error_msg}, 409

        usuario = Usuario(
            nome = form.nome,
            email = form.email,
            senha = form.senha,
        )

        logger.debug(f"Adding user with email: '{usuario.email}'")

        session.add(usuario)
        session.commit()

        return apresenta_usuario(usuario), 200
    
    except Exception as e:
        error_msg = "Could not save this user :/"
        logger.warning(f"Error create user: {error_msg}, Exception: {str(e)}")
        return {"message": error_msg}, 400

@app.post('/usuario/login', tags=[usuario_tag])
def login_usuario(form: LoginSchema):
    session = Session()

    try:
        usuario = session.query(Usuario).filter(Usuario.email == form.email).one_or_none()

        if usuario and usuario.senha == form.senha:
            logger.debug("User Found")
            return {
                "user": {
                    "id": usuario.id,
                    "email": usuario.email,
                    "nome": usuario.nome
                }
            }, 200
        else:
            logger.debug("User Not Found")
            return {"user": None}, 404
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}", exc_info=True)
        return {"error": "Erro interno no servidor"}, 500
    finally:
        session.close()

