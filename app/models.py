from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    todos = relationship("Todo", back_populates="user")

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    details = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=func.now())  # 作成日時を現在時刻で自動設定
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Userとのリレーション
    user = relationship("User", back_populates="todos")
