from pydantic import BaseModel


class UserBase(BaseModel):
    user_id: int


class ServerBase(BaseModel):
    server_id: int


class ChatBase(ServerBase, UserBase):
    pass


class UserAdd(UserBase):
    username: str


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
