from pydantic import BaseModel, Field
from model.user import User


class LoginSchema(BaseModel):
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., example="secure password")


class UserSchema(BaseModel):
    name: str
    email: str
    password: str


def present_user(user: User):
    """ 
    Returns a representation of the User following the schema defined in UserSchema.
    """
    return {
        "name": user.name,
        "email": user.email,
        "password": user.password
    }
