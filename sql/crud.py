from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, delete

from . import models, schemas
from decorators import timeit


@timeit
async def get_current_revision(db: AsyncSession):
    """
    Get the current revision of the database.

    Args:
        db (AsyncSession): The database session.

    Returns:
        str: The current revision of the database.
    """
    async with db() as db:
        result = await db.execute(select(models.AlembicVersion.version_num))
        return result.scalar_one_or_none()


@timeit
async def check_user_exists(db: AsyncSession, user: schemas.User.Get):
    """
    Check if a user exists in the database.

    Args:
        db (AsyncSession): The database session.
        user (schemas.User.Get): The user object to check.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    async with db() as db:
        result = await db.execute(
            select(models.User).where(models.User.user_id == user.user_id)
        )
        return result.scalar_one_or_none() is not None


@timeit
async def check_server_exists(db: AsyncSession, server: schemas.Server.Get):
    """
    Check if a server exists in the database.

    Args:
        db (AsyncSession): The database session.
        server (schemas.Server.Get): The server object to check.

    Returns:
        bool: True if the server exists, False otherwise.
    """
    async with db() as db:
        result = await db.execute(
            select(models.Server).where(models.Server.server_id == server.server_id)
        )
        return result.scalar_one_or_none() is not None


@timeit
async def add_user(db: AsyncSession, user: schemas.User.Add):
    """
    Adds a user to the database.

    Parameters:
      db (AsyncSession): The database session.
      user (schemas.User.Add): The user object to be added.

    Returns:
    None
    """
    async with db() as db:
        db.add(models.User(**user.model_dump()))
        await db.commit()


@timeit
async def edit_user_tos(db: AsyncSession, user: schemas.User.SetTos):
    """
    Edit the terms of service agreement for a user.

    Args:
        db (AsyncSession): The database session.
        user (schemas.User.SetTos): The user object with the new terms of service agreement.

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


@timeit
async def edit_user_ban(db: AsyncSession, user: schemas.User.SetBan):
    """
    Edit the ban status for a user.

    Args:
        db (AsyncSession): The database session.
        user (schemas.User.SetBan): The user object with the new ban status.

    Returns:
        None
    """
    async with db() as db:
        result = await db.execute(
            select(models.User).where(models.User.user_id == user.user_id)
        )
        result = result.scalar_one_or_none()
        result.is_banned = user.is_banned
        await db.commit()


@timeit
async def get_user(db: AsyncSession, user: schemas.User.Get):
    """
    Retrieve a user from the database.

    Args:
        db (AsyncSession): The database session.
        user (schemas.User.Get): The user object to retrieve.

    Returns:
        models.User: The user object.
    """
    async with db() as db:
        result = await db.execute(
            select(models.User).where(models.User.user_id == user.user_id)
        )
        return result.scalar_one_or_none()


@timeit
async def delete_all_user_data(db: AsyncSession, user: schemas.User.Delete):
    """
    Delete all data for a user from the database.

    Args:
        db (AsyncSession): The database session.
        user (schemas.User.Delete): The user object to delete.

    Returns:
        None
    """
    async with db() as db:
        await db.execute(delete(models.Chat).where(models.Chat.user_id == user.user_id))
        await db.execute(delete(models.User).where(models.User.user_id == user.user_id))
        await db.commit()


@timeit
async def add_server(db: AsyncSession, server: schemas.Server.Add):
    """
    Add a new server to the database.

    Parameters:
      db (AsyncSession): The database session.
      server (schemas.Server.Add): The server data to be added.

    Returns:
    None
    """
    async with db() as db:
        db.add(models.Server(**server.model_dump()))
        await db.commit()


@timeit
async def get_server(db: AsyncSession, server: schemas.Server.Get):
    """
    Retrieve a server from the database.

    Args:
        db (AsyncSession): The database session.
        server (schemas.Server.Get): The server object to retrieve.

    Returns:
        models.Server: The server object.
    """
    async with db() as db:
        result = await db.execute(
            select(models.Server).where(models.Server.server_id == server.server_id)
        )
        return result.scalar_one_or_none()


@timeit
async def add_chat(db: AsyncSession, chat: schemas.Chat.Add):
    """
    Adds a chat to the database.

    Parameters:
      db (AsyncSession): The database session.
      chat (schemas.Chat.Add): The chat data to be added.

    Returns:
    None
    """
    async with db() as db:
        db.add(models.Chat(**chat.model_dump()))
        await db.commit()


@timeit
async def get_chats_for_user(db: AsyncSession, chat: schemas.Chat.Get):
    """


    Args:
        db (AsyncSession): The database session.
        chat (schemas.Chat.Get): The chat data to be retrieved.

    Returns:
        List[models.Chat]: A list of chats.
    """
    async with db() as db:
        if chat.n is None:
            chat.n = 10
        result = await db.execute(
            select(models.Chat.user_message, models.Chat.assistant_message)
            .where(models.Chat.user_id == chat.user_id)
            .where(models.Chat.shared_chat == 0)
            .order_by(models.Chat.id.desc())
            .limit(chat.n)
        )
        return result.all()


@timeit
async def get_shared_chats_for_server(db: AsyncSession, chat: schemas.Chat.Get):
    """
    Retrieve the n most recent shared chats for a given server.

    Args:
        db (AsyncSession): The database session.
        chat (schemas.Chat.Get): The chat data to be retrieved.

    Returns:
        List[models.Chat]: A list of shared chats.
    """
    async with db() as db:
        if chat.n is None:
            chat.n = 10
        result = await db.execute(
            select(models.Chat.user_message, models.Chat.assistant_message)
            .where(models.Chat.server_id == chat.server_id)
            .where(models.Chat.shared_chat == 1)
            .order_by(models.Chat.id.desc())
            .limit(chat.n)
        )
        return result.all()


@timeit
async def delete_chat(db: AsyncSession, chat: schemas.Chat.Delete):
    """
    Delete a chat from the database.

    Args:
        db (AsyncSession): The database session.
        chat (schemas.Chat.Delete): The chat data to be deleted.

    Returns:
        None
    """
    async with db() as db:
        if chat.n is None:
            result = await db.execute(
                select(models.Chat)
                .where(models.Chat.user_id == chat.user_id)
                .where(models.Chat.server_id == chat.server_id)
                .where(models.Chat.shared_chat == 0)
                .order_by(models.Chat.id.desc())
            )
        else:
            result = await db.execute(
                select(models.Chat)
                .where(models.Chat.user_id == chat.user_id)
                .where(models.Chat.server_id == chat.server_id)
                .where(models.Chat.shared_chat == 0)
                .order_by(models.Chat.id.desc())
                .limit(chat.n)
            )
        result = result.all()
        for chat in result:
            db.delete(chat)
        await db.commit()


@timeit
async def delete_shared_chat(db: AsyncSession, chat: schemas.Chat.Delete):
    """
    Delete a shared chat from the database.

    Args:
        db (AsyncSession): The database session.
        chat (schemas.Chat.Delete): The chat data to be deleted.

    Returns:
        None
    """
    async with db() as db:
        if chat.n is None:
            result = await db.execute(
                select(models.Chat)
                .where(models.Chat.server_id == chat.server_id)
                .where(models.Chat.shared_chat == 1)
                .order_by(models.Chat.id.desc())
            )
        else:
            result = await db.execute(
                select(models.Chat)
                .where(models.Chat.server_id == chat.server_id)
                .where(models.Chat.shared_chat == 1)
                .order_by(models.Chat.id.desc())
                .limit(chat.n)
            )
        result = result.all()
        for chat in result:
            db.delete(chat)
        await db.commit()


@timeit
async def get_authenticated_servers(db: AsyncSession):
    """
    Retrieves all authenticated servers from the database.

    Args:
        db (AsyncSession): The database session.

    Returns:
        List[models.Server]: A list of authenticated servers.
    """
    async with db() as db:
        result = await db.execute(
            select(models.Server.server_id).where(models.Server.is_authorized == 1)
        )
        return result.all()


@timeit
async def get_authenticated_server_by_id_or_name(
    db: AsyncSession, server: schemas.Server.GetByIdOrName
):
    """
    Retrieves an authenticated server from the database by ID or name.

    Args:
        db (AsyncSession): The database session.
        server (schemas.Server.GetByIdOrName): The server ID or name to search for.

    Returns:
        models.Server: The authenticated server.
    """
    async with db() as db:
        result = await db.execute(
            select(models.Server).where(
                or_(
                    models.Server.server_id == server.server_id_or_name,
                    models.Server.server_name.like(f"%{server.server_id_or_name}%"),
                )
            )
        )
        return result.scalar_one_or_none()


@timeit
async def get_banned_servers(db: AsyncSession):
    """
    Retrieves all banned servers from the database.

    Args:
        db (AsyncSession): The database session.

    Returns:
        List[models.Server]: A list of banned servers.
    """
    async with db() as db:
        result = await db.execute(
            select(models.Server.server_id).where(models.Server.is_banned == 1)
        )
        return result.all()


@timeit
async def set_server_is_authorized(
    db: AsyncSession, server: schemas.Server.SetIsAuthorized
):
    """
    Set the is_authorized status for a server.

    Args:
        db (AsyncSession): The database session.
        server (schemas.Server.SetIsAuthorized): The server object with the new is_authorized status.

    Returns:
        None
    """
    async with db() as db:
        result = await db.execute(
            select(models.Server).where(models.Server.server_id == server.server_id)
        )
        result = result.scalar_one_or_none()
        result.is_authorized = server.is_authorized
        await db.commit()


@timeit
async def edit_server_ban(db: AsyncSession, server: schemas.Server.SetBan):
    """
    Edit the ban status for a server.

    Args:
        db (AsyncSession): The database session.
        server (schemas.Server.SetBan): The server object with the new ban status.

    Returns:
        None
    """
    async with db() as db:
        result = await db.execute(
            select(models.Server).where(models.Server.server_id == server.server_id)
        )
        result = result.scalar_one_or_none()
        result.is_banned = server.is_banned
        await db.commit()
