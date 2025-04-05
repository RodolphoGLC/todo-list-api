from sqlalchemy import Column, Integer, String, ForeignKey
from model import Base

class User(Base):
    __tablename__ = "users"

    id = Column("pk_user", Integer, primary_key=True)
    name = Column(String(140))
    email = Column(String(140), unique=True, index=True)
    password = Column(String(140))

    # To be removed later
    tasks = Column(Integer, ForeignKey("task.pk_task"))

    def __init__(self, name: str, email: str, password: str):
        """
        Creates a User
        """
        self.name = name
        self.email = email
        self.password = password
