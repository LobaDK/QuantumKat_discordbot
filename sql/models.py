from sqlalchemy import Column, Integer, String, ForeignKey

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)


class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, unique=True, index=True)


class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    server_id = Column(Integer, ForeignKey("servers.server_id"))
    user_message = Column(String)
    assistant_message = Column(String)
    shared_chat = Column(Integer)


class AuthenticatedServer(Base):
    __tablename__ = "authenticated_servers"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("servers.server_id"))
    authenticated_by_id = Column(Integer, ForeignKey("users.user_id"))
    requested_by_id = Column(Integer, ForeignKey("users.user_id"))
    is_authenticated = Column(Integer)
