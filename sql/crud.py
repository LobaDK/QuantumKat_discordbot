from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from . import models, schemas


async def check_user_exists(db: AsyncSession, user_id: int):
    """
    Check if a user exists in the database.

    Args:
        db (AsyncSession): The database session.
        user_id (int): The ID of the user to check.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    async with db() as db:
        result = await db.execute(
            select(models.User).where(models.User.user_id == user_id)
        )
        return result.scalar_one_or_none() is not None


async def check_server_exists(db: AsyncSession, server_id: int):
    """
    Check if a server exists in the database.

    Args:
        db (AsyncSession): The database session.
        server_id (int): The ID of the server to check.

    Returns:
        bool: True if the server exists, False otherwise.
    """
    async with db() as db:
        result = await db.execute(
            select(models.Server).where(models.Server.server_id == server_id)
        )
        return result.scalar_one_or_none() is not None


async def add_user(db: AsyncSession, user: schemas.UserBase):
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
    if not await check_user_exists(db, chat.user_id):
        await add_user(db, schemas.UserBase(user_id=chat.user_id))
    async with db() as db:
        db.add(models.Chat(**chat.model_dump()))
        await db.commit()


async def get_n_chats_for_user(db: AsyncSession, user_id: int, server_id: int, n: int):
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
            select(models.Chat)
            .where(models.Chat.user_id == user_id)
            .where(models.Chat.server_id == server_id)
            .where(models.Chat.shared_chat is False)
            .order_by(models.Chat.id.desc())
            .limit(n)
        )
        return result.all()


async def get_n_shared_chats_for_server(db: AsyncSession, server_id: int, n: int):
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
            select(models.Chat)
            .where(models.Chat.server_id == server_id)
            .where(models.Chat.shared_chat is True)
            .order_by(models.Chat.id.desc())
            .limit(n)
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
            .where(models.Chat.shared_chat is False)
            .order_by(models.Chat.id.desc())
            .limit(n)
        )
        for c in chat:
            db.delete(c)
        await db.commit()


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
            .where(models.Chat.shared_chat is True)
            .order_by(models.Chat.id.desc())
            .limit(n)
        )
        for c in chat:
            db.delete(c)
        await db.commit()


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
            .where(models.Chat.shared_chat is False)
        )
        for c in chat:
            db.delete(c)
        await db.commit()


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
            .where(models.Chat.shared_chat is True)
        )
        for c in chat:
            db.delete(c)
        await db.commit()


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
            select(models.AuthenticatedServer).where(
                models.AuthenticatedServer.is_authenticated is True
            )
        )
        return result.all()


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
            select(models.AuthenticatedServer).where(
                models.AuthenticatedServer.is_authenticated is False
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
    if not await check_server_exists(db, server.server_id):
        await add_server(db, schemas.ServerBase(server_id=server.server_id))
    if not await check_user_exists(db, server.authenticated_by_id):
        await add_user(db, schemas.UserBase(user_id=server.authenticated_by_id))
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
    if not await check_server_exists(db, server.server_id):
        await add_server(db, schemas.ServerBase(server_id=server.server_id))
    if not await check_user_exists(db, server.server_id):
        await add_user(db, schemas.UserBase(user_id=server.server_id))
    async with db() as db:
        db.add(models.AuthenticatedServer(**server.model_dump()))


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
        server = await db.execute(
            select(models.AuthenticatedServer).where(
                models.AuthenticatedServer.server_id == server_id
            )
        )
        db.delete(server)
        await db.commit()
