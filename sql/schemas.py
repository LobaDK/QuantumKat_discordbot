from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class User:

    class _Base(BaseModel):
        user_id: int

    class Get(_Base):
        pass

    class Delete(_Base):
        pass

    class SetTos(_Base):
        agreed_to_tos: bool

    class SetBan(_Base):
        is_banned: bool

    class SetUsername(_Base):
        username: str

    class Add(_Base):
        username: str
        agreed_to_tos: Optional[bool] = False
        is_banned: Optional[bool] = False


class Server:

    class _Base(BaseModel):
        server_id: int

    class Add(_Base):
        server_name: str
        is_authorized: Optional[bool] = False
        is_banned: Optional[bool] = False

    class Get(_Base):
        pass

    class GetByIdOrName(BaseModel):
        server_id_or_name: int | str

    class Delete(_Base):
        pass

    class SetIsAuthorized(_Base):
        is_authorized: bool

    class SetBan(_Base):
        is_banned: bool


class Chat:
    class _Base(Server._Base, User._Base):
        shared_chat: Optional[bool] = False

    class Get(_Base):
        n: Optional[int] = Field(None, ge=1, le=10)

        class Config:
            from_attributes = True

    class Add(_Base):
        user_message: str
        assistant_message: str

    class Delete(Get):
        pass


class Bot:
    class _Base(BaseModel):
        is_reboot_scheduled: bool
        reboot_time: datetime

    class unsetReboot(_Base):
        pass

    class SetReboot(unsetReboot):
        message_location: tuple[int, int, int]
