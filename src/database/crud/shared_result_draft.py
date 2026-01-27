from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import SharedResultDraft
from src.database.schemas import SharedResultDraftCreate, SharedResultDraftUpdate


async def create_draft(session: AsyncSession, data: SharedResultDraftCreate) -> SharedResultDraft:
    obj = SharedResultDraft(**data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj

async def get_draft(session: AsyncSession, draft_id: int) -> SharedResultDraft | None:
    stmt = select(SharedResultDraft).where(SharedResultDraft.id == draft_id)
    return await session.scalar(stmt)

async def list_drafts(session: AsyncSession, user_id: int | None = None, is_submitted: bool | None = None, offset: int | None = None, limit: int | None = None) -> list[SharedResultDraft]:
    stmt = select(SharedResultDraft).order_by(SharedResultDraft.id.desc())
    if offset: stmt = stmt.offset(offset)
    if limit: stmt = stmt.limit(limit)
    if user_id is not None: stmt = stmt.where(SharedResultDraft.user_id == user_id)
    if is_submitted is not None: stmt = stmt.where(SharedResultDraft.is_submitted == is_submitted)
    res = await session.scalars(stmt)
    return list(res)


async def update_draft(session: AsyncSession, draft_id: int, patch: SharedResultDraftUpdate) -> SharedResultDraft:
    data = patch.model_dump(exclude_unset=True)
    draft = await get_draft(session, draft_id)
    for k, v in data.items(): setattr(draft, k, v)
    await session.commit()
    await session.refresh(draft)
    return draft


async def delete_draft(session: AsyncSession, draft: SharedResultDraft) -> None:
    await session.delete(draft)
    await session.commit()