from decimal import Decimal
from pathlib import Path
from aiogram.types import FSInputFile, InputMediaPhoto, Message
from src.database.models import SharedResultDraft

APPOINTED_VALUES = ("врач", "сам(а) себе", "ботом")


async def send_draft_photos_if_exist(message: Message, draft: SharedResultDraft):
    if draft.photo_url:
        review_photos_dir = Path(draft.photo_url)
        photos = [path for path in review_photos_dir.iterdir() if path.is_file() and path.suffix == ".jpg"]
        photos.sort()
        media = [InputMediaPhoto(media=FSInputFile(path), caption=f"Фотографии черновика #{draft.id}") for path in photos]
        if media: await message.answer_media_group(media)

_REQUIRED = (
    "user_id",
    "drugs",
    "appointed",
    "gender",
    "height",
    "starting_weight",
    "current_weight",
    "lost_weight",
    "time_period",
    "course",
    "author",
)

def missing_required_in_draft(draft) -> list[str]:
    missing: list[str] = []
    for name in _REQUIRED:
        val = getattr(draft, name, None)

        if val is None:
            missing.append(name.removesuffix("_url"))
            continue

        if isinstance(val, str) and (val == "Не указан" or not val.strip()):
            missing.append(name.removesuffix("_url"))
            continue

        if name == "appointed" and val not in APPOINTED_VALUES:
            missing.append(name)
            continue

        if isinstance(val, Decimal) and val == 0:
            missing.append(name)
            continue

    return missing
