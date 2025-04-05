from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from datetime import datetime
from model import Base
from model.user import User

class Task(Base):
    __tablename__ = 'task'

    id = Column("pk_task", Integer, primary_key=True)
    name = Column(String(140), unique=True)
    description = Column(String(140))
    status = Column(String(100))
    creation_date = Column(DateTime, default=datetime.now)

    user = Column(Integer, ForeignKey("users.pk_user"))

    def __init__(self, name: str, description: str, status: str):
        self.name = name
        self.description = description
        self.status = status
        self.creation_date = datetime.now()
        # self.user = None

    def relate_user(self, user: User):
        """Relates the task to a user."""
        self.user = user
