from sqlalchemy.orm import Session
from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect

from model import Session, Task, User
from logger import logger
from schemas import *
from flask_cors import CORS

info = Info(title="Task List API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

home_tag = Tag(name="Documentation",
               description="Documentation selection: Swagger, Redoc, or RapiDoc")

task_tag = Tag(
    name="Task", description="Operations related to tasks: add, view, update, and remove.")

user_tag = Tag(
    name="User", description="User operations: create account and authenticate.")


@app.get('/', tags=[home_tag])
def home():
    """Redirects to /openapi, a page that allows choosing the documentation style."""
    return redirect('/openapi')


@app.get('/tasks', tags=[task_tag], responses={"200": TaskListSchema, "409": ErrorSchema, "400": ErrorSchema})
def get_tasks(query: TaskIdSchema):
    """
    Get all tasks of a user

    Returns a list of all tasks associated with the given user ID.
    - **Query parameter**:
        - `id`: User ID
    - **Responses**:
        - `200`: List of tasks
        - `409`: Conflict retrieving tasks
        - `400`: Bad request
    """
    session = Session()
    tasks = session.query(Task).filter(Task.user == query.id).all()

    if not tasks:
        logger.debug("No tasks found.")
        session.close()
        return present_tasks([]), 200
    else:
        logger.debug(f"{len(tasks)} tasks found")
        session.close()
        return present_tasks(tasks), 200


@app.post('/task', tags=[task_tag],
          responses={"200": TaskViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_task(form: TaskSchema):
    """
    Add a new task

    Creates a new task and links it to a user by email.
    - **Request body**:
        - `name`: Name of the task
        - `description`: Task details
        - `status`: Task status (Ready, Doing, Done)
        - `userEmail`: Email of the user
    - **Responses**:
        - `200`: Task created successfully
        - `409`: Task already exists
        - `404`: User not found
        - `400`: Failed to save task
    """
    existing_task = None
    existing_user = None

    try:
        session = Session()
        existing_task = session.query(Task).filter(
            Task.name == form.name).one_or_none()
        existing_user = session.query(User).filter(
            User.email == form.userEmail).one_or_none()

        if existing_task:
            error_msg = f"Task with the name '{form.name}' already exists in the database."
            logger.warning(error_msg)
            return {"message": error_msg}, 409

        task = Task(
            name=form.name,
            description=form.description,
            status=form.status,
        )

        if existing_user:
            task.user = existing_user.id
        else:
            error_msg = "User not found."
            logger.warning(error_msg)
            return {"message": error_msg}, 404

        logger.debug(f"Adding task with name: '{task.name}'")

        session.add(task)
        session.commit()

        logger.debug(f"Added task with name: '{task.name}'")
        return present_task(task), 200

    except Exception as e:
        error_msg = "Could not save the new task :/"
        logger.warning(f"Error adding task: {error_msg}, Exception: {str(e)}")
        return {"message": error_msg}, 400


@app.delete('/task', tags=[task_tag], responses={"200": TaskViewSchema, "404": ErrorSchema})
def delete_task(query: TaskIdSchema):
    """
    Delete a task by ID

    Removes a task based on its ID.
    - **Query parameter**:
        - `id`: Task ID
    - **Responses**:
        - `200`: Task deleted successfully
        - `404`: Task not found
    """
    id = query.id

    session = Session()
    task = session.query(Task).filter(Task.id == id).first()

    if not task:
        error_msg = "Task not found :/"
        logger.warning(f"Error deleting task {id}, {error_msg}")
        return {"error": error_msg}, 404

    session.delete(task)
    session.commit()
    session.close()

    logger.debug(f"Task {id} deleted successfully")
    return {"message": f"Task '{task.name}' deleted successfully"}, 200


@app.get('/tasks/status', tags=[task_tag], responses={"200": TasksByStatusResponse, "500": ErrorSchema})
def get_tasks_by_status(query: TaskIdSchema):
    """
    Get task counts by status

    Returns the number of tasks grouped by status for a specific user.
    - **Query parameter**:
        - `id`: User ID
    - **Responses**:
        - `200`: Task counts grouped by status
        - `500`: Internal server error
    """
    session = Session()

    try:
        results = session.query(Task).filter(Task.user == query.id).all()

        logger.debug(results)

        possible_status = ["Ready", "Doing", "Done"]
        response = {status: sum(
            1 for task in results if task.status == status) for status in possible_status}

        logger.debug(f"Task count by status: {response}")

        return response, 200

    except Exception as e:
        logger.error(f"Error fetching tasks by status: {str(e)}")
        return {"message": "Internal error processing the request"}, 500

    finally:
        session.close()


@app.put('/task', tags=[task_tag], responses={"200": TaskViewSchema, "404": ErrorSchema})
def update_task_status(form: TaskUpdateSchema):
    """
    Update a task's status

    Updates the status field of a task by its ID.
    - **Request body**:
        - `id`: Task ID
        - `status`: New status value
    - **Responses**:
        - `200`: Task updated successfully
        - `404`: Task not found
    """
    session = Session()
    id = form.id

    try:
        task = session.query(Task).filter(Task.id == id).first()

        if not task:
            error_msg = "Task not found :/"
            logger.warning(f"Error updating task status {id}, {error_msg}")
            return {"message": error_msg}, 404

        task.status = form.status
        session.commit()

        logger.debug(f"Task {id} status updated to {form.status}")
        return present_task(task), 200

    except Exception as e:
        session.rollback()
        logger.error(f"Error updating task {id}: {str(e)}")
        return {"message": "Internal server error"}, 500

    finally:
        session.close()


@app.post('/user', tags=[user_tag], responses={"200": UserSchema, "404": ErrorSchema})
def post_user(form: UserSchema):
    """
    Create a new user

    Adds a user to the system.
    - **Request body**:
        - `name`: Name of the user
        - `email`: Email address
        - `password`: User password
    - **Responses**:
        - `200`: User created successfully
        - `409`: User already exists
        - `400`: Failed to create user
    """
    existing_user = None

    try:
        session = Session()
        existing_user = session.query(User).filter(
            User.email == form.email).one_or_none()

        if existing_user:
            error_msg = f"User with email '{form.email}' already exists in the database"
            logger.warning(error_msg)
            return {"message": error_msg}, 409

        user = User(
            name=form.name,
            email=form.email,
            password=form.password,
        )

        logger.debug(f"Adding user with email: '{user.email}'")

        session.add(user)
        session.commit()

        return present_user(user), 200

    except Exception as e:
        error_msg = "Could not save this user :/"
        logger.warning(
            f"Error creating user: {error_msg}, Exception: {str(e)}")
        return {"message": error_msg}, 400


@app.post('/user/login', tags=[user_tag])
def login_user(form: LoginSchema):
    """
    User login

    Authenticates a user with email and password.
    - **Request body**:
        - `email`: User's email
        - `password`: User's password
    - **Responses**:
        - `200`: User authenticated successfully
        - `404`: Invalid credentials
        - `500`: Server error
    """
    session = Session()

    try:
        user = session.query(User).filter(
            User.email == form.email).one_or_none()

        if user and user.password == form.password:
            logger.debug("User found")
            return {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name
                }
            }, 200
        else:
            logger.debug("User not found")
            return {"message": "User not found"}, 404
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        return {"error": "Internal server error"}, 500
    finally:
        session.close()
