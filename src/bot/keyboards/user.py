from pathlib import Path
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from src.database.models import SharedResultDraft
from src.helpers import missing_required_in_draft


def mark(flag: bool) -> str: return "✅" if flag else "❌"

DRAFT_FIELD_LABELS: dict[str, str] = {
    "drugs": "Препарат (или несколько)",
    "age": "Возраст (по желанию)",
    "gender": "Пол",
    "height": "Рост (см)",
    "starting_weight": "Начальный вес (кг)",
    "current_weight": "Текущий вес (кг)",
    "desired_weight": "Желаемый вес (по желанию)",
    "lost_weight": "Сколько всего сброшено кг",
    "time_period": "Период похудения",
    "course": "Курсы/дозировки",
    "photo": "Фото 'до/после' (опционально)",
    "commentary": "Комментарий (до 2000 символов, опционально)",
}

main_menu_button = InlineKeyboardButton(text='🔙 В главное меню', callback_data='user:main_menu')
main_menu = InlineKeyboardMarkup(inline_keyboard=[[main_menu_button]])

main_menuu_button = InlineKeyboardButton(text='🔙 В главное меню', callback_data='user:main_menuu')
main_menuu = InlineKeyboardMarkup(inline_keyboard=[[main_menuu_button]])

user_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📝 Поделиться результатом', callback_data="user:share_result:start")],
    [InlineKeyboardButton(text='✉️ Написать администрации', callback_data="user:message_admins:start")],
])

share_result_terms = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Согласен", callback_data="user:terms:yes"),
     InlineKeyboardButton(text="❌ Отказываюсь", callback_data="user:terms:no")],
    [main_menu_button],
])

share_result_anonymity = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👤 Анонимный", callback_data="user:share_result:anonymity:yes"),
     InlineKeyboardButton(text="🙋🏼‍♂️ Авторский 🙋🏼‍♀️", callback_data="user:share_result:anonymity:no")],
    [main_menu_button],
])

def draft_keyboard(**kwargs) -> InlineKeyboardMarkup:
    share_result_id = kwargs.get("id")
    drugs = kwargs.pop("drugs", None)
    age = kwargs.pop("age", None)
    gender = kwargs.pop("gender", None)
    height = kwargs.pop("height", None)
    starting_weight = kwargs.pop("starting_weight", None)
    current_weight = kwargs.pop("current_weight", None)
    desired_weight = kwargs.pop("desired_weight", None)
    lost_weight = kwargs.pop("lost_weight", None)
    time_period = kwargs.pop("time_period", None)
    course = kwargs.pop("course", None)
    photo_url = kwargs.pop("photo_url", None)
    photo = False
    if photo_url:
        draft_photos_dir = Path(photo_url)
        if draft_photos_dir.exists() and draft_photos_dir.is_dir(): photo = bool([path for path in draft_photos_dir.iterdir() if path.is_file() and path.suffix == ".jpg"])

    commentary = kwargs.pop("commentary", None)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{mark(drugs)} Препарат (или несколько) ‼️", callback_data=f"user:edit_draft:{share_result_id}:drugs")],
        [InlineKeyboardButton(text=f"{mark(age)} Возраст (по желанию)", callback_data=f"user:edit_draft:{share_result_id}:age")],
        [InlineKeyboardButton(text=f'{"✅" if isinstance(gender, str) and gender.lower() != "не указан" else "❌"} Пол ‼️', callback_data=f"user:edit_draft:{share_result_id}:gender")],
        [InlineKeyboardButton(text=f"{mark(height)} Рост (см) ‼️", callback_data=f"user:edit_draft:{share_result_id}:height")],
        [InlineKeyboardButton(text=f"{mark(starting_weight)} Начальный вес (кг) ‼️", callback_data=f"user:edit_draft:{share_result_id}:starting_weight")],
        [InlineKeyboardButton(text=f"{mark(current_weight)} Текущий вес (кг) ‼️", callback_data=f"user:edit_draft:{share_result_id}:current_weight")],
        [InlineKeyboardButton(text=f"{mark(desired_weight)} Желаемый вес (по желанию)", callback_data=f"user:edit_draft:{share_result_id}:desired_weight")],
        [InlineKeyboardButton(text=f"{mark(lost_weight)} Сколько всего сброшено кг ‼️", callback_data=f"user:edit_draft:{share_result_id}:lost_weight")],
        [InlineKeyboardButton(text=f"{mark(time_period)} Период похудения ‼️", callback_data=f"user:edit_draft:{share_result_id}:time_period")],
        [InlineKeyboardButton(text=f"{mark(course)} Курсы/дозировки ‼️", callback_data=f"user:edit_draft:{share_result_id}:course")],
        [InlineKeyboardButton(text=f"{mark(photo)} Фото 'до/после' (опционально)", callback_data=f"user:edit_draft:{share_result_id}:photo")],
        [InlineKeyboardButton(text=f"{mark(commentary)} Комментарий (до 2000 символов, опционально)", callback_data=f"user:edit_draft:{share_result_id}:commentary")],
        [InlineKeyboardButton(text="📝 Предпросмотр", callback_data=f"user:edit_draft:{share_result_id}:preview"),
         InlineKeyboardButton(text="🗑️ Удалить черновик", callback_data=f"user:delete_draft:{share_result_id}")],
        [main_menu_button]
    ])
def view_drafts(drafts: list[SharedResultDraft]) -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(text=f"Черновик #{draft.id}", callback_data=f"user:edit_draft:{draft.id}:view") for draft in drafts]
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="➕ Новый", callback_data=f"user:share_result:anonymity:view")]]+[buttons[i: i+2] for i in range(0, len(buttons), 2)]+[[main_menu_button]])

def preview_keyboard(draft: SharedResultDraft) -> InlineKeyboardMarkup:
    missing = missing_required_in_draft(draft)
    keyboard = [[InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"user:edit_draft:{draft.id}:view")]]
    if not missing: keyboard.append([InlineKeyboardButton(text="✅ Опубликовать", callback_data=f"user:post_draft:{draft.id}")])
    else: keyboard.extend([[InlineKeyboardButton(text=f"❌ {DRAFT_FIELD_LABELS[i]}", callback_data=f"user:edit_draft:{draft.id}:{i}")] for i in missing])
    keyboard.append([main_menu_button])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

choose_gender = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, keyboard=[
    [KeyboardButton(text="👨 Мужской"), KeyboardButton(text="👩 Женский")]
])

def to_draft(draft_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Править", callback_data=f"user:edit_draft:{draft_id}:view")]
    ])

support = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👨🏻‍💻 Поддержка", url="t.me/ShostakovIV")]
])

message_admin_phone = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, keyboard=[
    [KeyboardButton(text="📲 Поделиться номером", request_contact=True)],
])
