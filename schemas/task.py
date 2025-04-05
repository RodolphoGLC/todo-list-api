from pydantic import BaseModel, Field
from typing import List
from model.task import Task


class TaskSchema(BaseModel):
    name: str = Field(..., example="Write documentation")
    description: str = Field(...,
                             example="Write full Swagger docs for the API")
    status: str = Field(..., example="Ready")
    userEmail: str = Field(..., example="user@example.com")


class TaskIdSchema(BaseModel):
    id: int = Field(..., example=1)


class TaskUpdateSchema(BaseModel):
    id: int = Field(..., example=1)
    status: str = Field(..., example="Done")


class TaskListSchema(BaseModel):
    """ 
    Defines how the list of tasks will be returned
    """
    tasks: List[TaskSchema]


class TaskViewSchema(BaseModel):
    """ 
    Defines how a Task will be returned
    """
    id: int
    name: str
    description: str
    status: str


class TasksByStatusResponse(BaseModel):
    """ 
    Task count by status 
    """
    Ready: int
    Doing: int
    Done: int


def present_task(task: Task):
    """ 
    Returns a representation of a Task following the TaskViewSchema
    """
    return {
        "id": task.id,
        "name": task.name,
        "description": task.description,
        "status": task.status
    }


def present_tasks(tasks: List[Task]):
    """ 
    Returns a list of Task representations following the TaskViewSchema
    """
    result = []
    for task in tasks:
        result.append({
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "status": task.status,
            "creation_date": task.creation_date,
            "user": task.user
        })

    return {"tasks": result}
