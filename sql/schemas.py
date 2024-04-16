from pydantic import BaseModel
from typing import Optional


class User:

    class UserBase(BaseModel):
        user_id: int

    class UserGet(UserBase):
        pass

    class UserDelete(UserBase):
        pass

    class UserSetTos(UserBase):
        agreed_to_tos: int

    class UserSetBan(UserBase):
        is_banned: int

    class UserSetUsername(UserBase):
        username: str

    class UserAdd(UserBase):
        username: str
        agreed_to_tos: Optional[int] = 0
        is_banned: Optional[int] = 0


class Server:

    class ServerBase(BaseModel):
        server_id: int

    class ServerAdd(ServerBase):
        server_name: str
        is_authorized: Optional[int] = 0

    class ServerGet(ServerBase):
        pass

    class ServerDelete(ServerBase):
        pass

    class ServerSetIsAuthorized(ServerBase):
        is_authorized: int


class Chat:
    class ChatBase(Server.ServerBase, User.UserBase):
        shared_chat: Optional[int] = 0

    class ChatGet(ChatBase):
        n: Optional[int] = None

        class Config:
            from_attributes = True

    class ChatAdd(ChatBase):
        user_message: str
        assistant_message: str

    class ChatDelete(ChatGet):
        pass
