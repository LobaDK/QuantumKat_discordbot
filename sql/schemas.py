from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    user_id: int


class ServerBase(BaseModel):
    server_id: int


class ChatBase(ServerBase, UserBase):
    pass


class UserAdd(UserBase):
    username: Optional[str] = None
    agreed_to_tos: Optional[int] = 0
    is_banned: Optional[int] = 0


class SetUserTos(UserBase):
    agreed_to_tos: int


class ServerAdd(ServerBase):
    server_name: str


class ChatGet(ChatBase):
    n: int

    class Config:
        from_attributes = True


class ChatAdd(ChatBase):
    user_message: str
    assistant_message: str
    shared_chat: int


class AuthenticatedServerGet(ServerBase):
    is_authenticated: bool

    class Config:
        from_attributes = True


class AuthenticatedServerAdd(AuthenticatedServerGet):
    authenticated_by_id: int
    requested_by_id: int
    is_authenticated: bool


class AuthenticatedServerDeny(AuthenticatedServerAdd):
    pass
