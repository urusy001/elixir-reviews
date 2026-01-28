from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.database.models import SharedResultDraft


def post_draft(draft: SharedResultDraft):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📣 Опубликовать", callback_data=f"admin:{draft.id}:{draft.user_id}:post_draft"),
         InlineKeyboardButton(text="✏️ На правку", callback_data=f"admin:{draft.id}:{draft.user_id}:correction")],
        [InlineKeyboardButton(text="🔐 Заблокировать пользователя", callback_data=f"admin:block_user:{draft.user_id}")],
    ])

def back_to_draft(draft: SharedResultDraft):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"admin:{draft.id}:{draft.user_id}:back_to_draft")],
    ])

def unblock_user(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"🔓 Разблокировать пользователя", callback_data=f"admin:unblock_user:{user_id}")]])

def posted_draft(draft_id: int, message_id: int, url: str, message_ids: list[int] | None = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 К отзыву", url=url)],
        [InlineKeyboardButton(text="🗑️ Удалить из чата", callback_data=f"admin:delete_review:{draft_id}:{message_id}{(':'+('_'.join([str(i) for i in message_ids]))) if message_ids else ''}")],
    ])

def recover_review(draft_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="♻️ Вернуть отзыв", callback_data=f"admin:recover_review:{draft_id}")]])

def messaged_admins(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔐 Заблокировать пользователя", callback_data=f"admin:block_user:{user_id}")]])