from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    agreed_to_tos = Column(Integer, nullable=False, default=0)
    is_banned = Column(Integer, nullable=False, default=0)

    # Relationships
    chats = relationship("Chat", back_populates="user")


class Server(Base):
    __tablename__ = "servers"

    server_id = Column(Integer, primary_key=True, index=True)
    server_name = Column(String, nullable=False)
    is_authorized = Column(Integer, nullable=False, default=0)

    # Relationships
    chats = relationship("Chat", back_populates="server")


class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    server_id = Column(Integer, ForeignKey("servers.server_id"))
    user_message = Column(String, nullable=False)
    assistant_message = Column(String, nullable=False)
    shared_chat = Column(Integer, nullable=False, default=0)

    # Relationships
    user = relationship("User", back_populates="chats")
    server = relationship("Server", back_populates="chats")
