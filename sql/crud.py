from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, or_

from . import models, schemas


async def check_user_exists(db: AsyncSession, user: schemas.User.UserGet):
    """
    Check if a user exists in the database.

    Args:
        db (AsyncSession): The database session.
        user (schemas.User.UserGet): The user object to check.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    async with db() as db:
        result = await db.execute(
            select(models.User).where(models.User.user_id == user.user_id)
        )
        return result.scalar_one_or_none() is not None


async def check_server_exists(db: AsyncSession, server: schemas.Server.ServerGet):
    """
    Check if a server exists in the database.

    Args:
        db (AsyncSession): The database session.
        server (schemas.Server.ServerGet): The server object to check.

    Returns:
        bool: True if the server exists, False otherwise.
    """
    async with db() as db:
        result = await db.execute(
            select(models.Server).where(models.Server.server_id == server.server_id)
        )
        return result.scalar_one_or_none() is not None


async def add_user(db: AsyncSession, user: schemas.User.UserAdd):
    """
    Adds a user to the database.

    Parameters:
      db (AsyncSession): The database session.
      user (schemas.User): The user object to be added.

    Returns:
    None
    """
    async with db() as db:
        db.add(models.User(**user.model_dump()))
        await db.commit()


async def edit_user_tos(db: AsyncSession, user: schemas.User.UserSetTos):
    """
    Edit the terms of service agreement for a user.

    Args:
        db (AsyncSession): The database session.
        user (schemas.SetUserTos): The user object with the new terms of service agreement.

    Returns:
        None
    """
    async with db() as db:
        result = await db.execute(
            select(models.User).where(models.User.user_id == user.user_id)
        )
        result = result.scalar_one_or_none()
        result.agreed_to_tos = user.agreed_to_tos
        await db.commit()


async def edit_user_ban(db: AsyncSession, user: schemas.User.UserSetBan):
    """
    Edit the ban status for a user.

    Args:
        db (AsyncSession): The database session.
        user (schemas.User.UserSetBan): The user object with the new ban status.

    Returns:
        None
    """
    async with db() as db:
        result = await db.execute(
            select(models.User).where(models.User.user_id == user.user_id)
        )
        result = result.scalar_one_or_none()
        if result.is_banned == user.is_banned:
            raise IntegrityError(
                "User is already banned" if user.is_banned else "User is not banned"
            )
        result.is_banned = user.is_banned
        await db.commit()


async def get_user(db: AsyncSession, user: schemas.User.UserGet):
    """
    Retrieve a user from the database.

    Args:
        db (AsyncSession): The database session.
        user_id (int): The ID of the user.

    Returns:
        models.User: The user object.
    """
    async with db() as db:
        result = await db.execute(
            select(models.User).where(models.User.user_id == user.user_id)
        )
        return result.scalar_one_or_none()


async def add_server(db: AsyncSession, server: schemas.ServerBase):
    """
    Add a new server to the database.

    Parameters:
      db (AsyncSession): The database session.
      server (schemas.Server): The server data to be added.

    Returns:
    None
    """
    async with db() as db:
        db.add(models.Server(**server.model_dump()))
        await db.commit()


async def add_chat(db: AsyncSession, chat: schemas.ChatAdd):
    """
    Adds a chat to the database.

    Parameters:
      db (AsyncSession): The database session.
      chat (schemas.ChatAdd): The chat data to be added.

    Returns:
    None
    """
    async with db() as db:
        db.add(models.Chat(**chat.model_dump()))
        await db.commit()


async def get_n_chats_for_user(db: AsyncSession, chat: schemas.ChatGet):
    """
    Retrieve the latest `n` chats for a specific user in a specific server.

    Args:
        db (AsyncSession): The database session.
        user_id (int): The ID of the user.
        server_id (int): The ID of the server.
        n (int): The number of chats to retrieve.

    Returns:
        List[models.Chat]: A list of `n` latest chats for the user in the server.
    """
    async with db() as db:
        result = await db.execute(
            select(models.Chat.user_message, models.Chat.assistant_message)
            .where(models.Chat.user_id == chat.user_id)
            .where(models.Chat.server_id == chat.server_id)
            .where(models.Chat.shared_chat == 0)
            .order_by(models.Chat.id.desc())
            .limit(chat.n)
        )
        return result.all()


async def get_n_shared_chats_for_server(db: AsyncSession, chat: schemas.ChatGet):
    """
    Retrieve the n most recent shared chats for a given server.

    Args:
        db (AsyncSession): The database session.
        server_id (int): The ID of the server.
        n (int): The number of shared chats to retrieve.

    Returns:
        List[models.Chat]: A list of shared chats.
    """
    async with db() as db:
        result = await db.execute(
            select(models.Chat.user_message, models.Chat.assistant_message)
            .where(models.Chat.server_id == chat.server_id)
            .where(models.Chat.shared_chat == 1)
            .order_by(models.Chat.id.desc())
            .limit(chat.n)
        )
        return result.all()


async def delete_n_chats_for_user(
    db: AsyncSession, user_id: int, server_id: int, n: int
):
    """
    Delete the last 'n' chats for a specific user in a specific server.

    Args:
        db (AsyncSession): The database session.
        user_id (int): The ID of the user.
        server_id (int): The ID of the server.
        n (int): The number of chats to delete.

    Returns:
        None
    """
    async with db() as db:
        chat = await db.execute(
            select(models.Chat)
            .where(models.Chat.user_id == user_id)
            .where(models.Chat.server_id == server_id)
            .where(models.Chat.shared_chat == 0)
            .order_by(models.Chat.id.desc())
            .limit(n)
        )
        for c in chat:
            await db.delete(c)


async def delete_n_shared_chats_for_server(db: AsyncSession, server_id: int, n: int):
    """
    Delete the last 'n' shared chats for a given server.

    Args:
        db (AsyncSession): The database session.
        server_id (int): The ID of the server.
        n (int): The number of shared chats to delete.

    Returns:
        None
    """
    async with db() as db:
        chat = await db.execute(
            select(models.Chat)
            .where(models.Chat.server_id == server_id)
            .where(models.Chat.shared_chat == 1)
            .order_by(models.Chat.id.desc())
            .limit(n)
        )
        for c in chat:
            await db.delete(c)


async def delete_all_chats_for_user(db: AsyncSession, user_id: int, server_id: int):
    """
    Delete all chats for a specific user in a specific server.

    Args:
        db (AsyncSession): The database session.
        user_id (int): The ID of the user.
        server_id (int): The ID of the server.

    Returns:
        None
    """
    async with db() as db:
        chat = await db.execute(
            select(models.Chat)
            .where(models.Chat.user_id == user_id)
            .where(models.Chat.server_id == server_id)
            .where(models.Chat.shared_chat == 0)
        )
        for c in chat:
            await db.delete(c)


async def delete_all_shared_chats_for_server(db: AsyncSession, server_id: int):
    """
    Deletes all shared chats for a given server.

    Args:
        db (AsyncSession): The database session.
        server_id (int): The ID of the server.

    Returns:
        None
    """
    async with db() as db:
        chat = await db.execute(
            select(models.Chat)
            .where(models.Chat.server_id == server_id)
            .where(models.Chat.shared_chat == 1)
        )
        for c in chat:
            await db.delete(c)


async def get_authenticated_servers(db: AsyncSession):
    """
    Retrieves all authenticated servers from the database.

    Args:
        db (AsyncSession): The database session.

    Returns:
        List[models.AuthenticatedServer]: A list of authenticated servers.
    """
    async with db() as db:
        result = await db.execute(
            select(models.AuthenticatedServer.server_id).where(
                models.AuthenticatedServer.is_authenticated == 1
            )
        )
        return result.all()


async def get_authenticated_server_by_id_or_name(
    db: AsyncSession, server_id_or_name: int | str
):
    """
    Retrieves an authenticated server from the database by ID or name.

    Args:
        db (AsyncSession): The database session.
        server_id_or_name (int | str): The ID or name of the server.

    Returns:
        models.AuthenticatedServer: The authenticated server.
    """
    async with db() as db:
        result = await db.execute(
            select(models.AuthenticatedServer).where(
                or_(
                    models.AuthenticatedServer.server_id == server_id_or_name,
                    models.AuthenticatedServer.server_name.like(
                        f"%{server_id_or_name}%"
                    ),
                )
            )
        )
        return result.scalar_one_or_none()


async def get_denied_servers(db: AsyncSession):
    """
    Retrieves a list of denied servers from the database.

    Args:
        db (AsyncSession): The database session.

    Returns:
        List[models.AuthenticatedServer]: A list of denied servers.
    """
    async with db() as db:
        result = await db.execute(
            select(models.AuthenticatedServer.server_id).where(
                models.AuthenticatedServer.is_authenticated == 0
            )
        )
        return result.all()


async def add_authenticated_server(
    db: AsyncSession, server: schemas.AuthenticatedServerAdd
):
    """
    Adds an authenticated server to the database.

    Parameters:
      db (AsyncSession): The database session.
      server (schemas.AuthenticatedServerAdd): The authenticated server data to be added.

    Returns:
    None
    """
    async with db() as db:
        db.add(models.AuthenticatedServer(**server.model_dump()))
        await db.commit()


async def deny_authenticated_server(
    db: AsyncSession, server: schemas.AuthenticatedServerDeny
):
    """
    Denies an authenticated server.

    Args:
        db (AsyncSession): The database session.
        server (schemas.AuthenticatedServerDeny): The server to be denied.

    Returns:
        None
    """
    async with db() as db:
        db.add(models.AuthenticatedServer(**server.model_dump()))
        await db.commit()


async def remove_authenticated_server(db: AsyncSession, server_id: int):
    """
    Removes an authenticated server from the database.

    Args:
        db (AsyncSession): The database session.
        server_id (int): The ID of the server to be removed.

    Returns:
        None
    """
    async with db() as db:
        result = await db.execute(
            select(models.AuthenticatedServer).where(
                models.AuthenticatedServer.server_id == server_id
            )
        )
        server = result.scalar_one_or_none()
        await db.delete(server)
