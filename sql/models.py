from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)

    # Relationships
    chats = relationship("Chat", back_populates="user")
    authenticated_servers = relationship("AuthenticatedServer", back_populates="user")


class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    server_id = Column(Integer, ForeignKey("servers.server_id"))
    user_message = Column(String)
    assistant_message = Column(String)
    shared_chat = Column(Integer)

    # Relationships
    user = relationship("User", back_populates="chats")


class AuthenticatedServer(Base):
    __tablename__ = "authenticated_servers"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("servers.server_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))

    # Relationships
    user = relationship("User", back_populates="authenticated_servers")
