# src/crud/users.py
from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import User
from src.database.schemas import UserCreate, UserUpdate


async def create_user(session: AsyncSession, data: UserCreate) -> User:
    obj = User(**data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def get_user(session: AsyncSession, user_id: int) -> Optional[User]:
    stmt = select(User).where(User.id == user_id)
    return await session.scalar(stmt)


async def get_user_with_results(session: AsyncSession, user_id: int) -> Optional[User]:
    stmt = (select(User).where(User.id == user_id).options(selectinload(User.results)))
    return await session.scalar(stmt)


async def list_users(session: AsyncSession, offset: int | None = None, limit: int | None = None) -> list[User]:
    stmt = select(User)
    if offset: stmt = stmt.offset(offset)
    if limit: stmt = stmt.limit(limit)
    res = await session.scalars(stmt)
    return list(res)

async def update_user(session: AsyncSession, user_id: int, patch: UserUpdate) -> User:
    user = await get_user(session, user_id)
    data = patch.model_dump(exclude_none=True)
    for k, v in data.items(): setattr(user, k, v)
    await session.commit()
    await session.refresh(user)
    return user


async def delete_user(session: AsyncSession, user: User) -> None:
    await session.delete(user)
    await session.commit()