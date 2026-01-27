from pathlib import Path
from aiogram import Router
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, FSInputFile, Message

from config import ELIXIR_CHAT_ID, ELIXIR_THREAD_ID, ADMIN_CHAT_ID
from src.database import get_session
from src.database.crud import update_user
from src.database.crud.shared_result_draft import update_draft, get_draft
from src.database.schemas import SharedResultDraftUpdate, UserUpdate
from src.bot.states import admin_states
from src.bot.keyboards import admin_keyboards, user_keyboards

admin_router = Router(name="admin")
admin_router.message.filter(lambda message: message.chat.type == ChatType.GROUP and message.chat.id == ADMIN_CHAT_ID)
admin_router.callback_query.filter(lambda call: call.message.chat.type == ChatType.GROUP and call.data.startswith("admin") and call.message.chat.id == ADMIN_CHAT_ID)

@admin_router.message(admin_states.DraftSubmission.correction, lambda message: message.text.strip())
async def handle_admin_correction(message: Message, state: FSMContext):
    state_data = await state.get_data()
    user_id = int(state_data["user_id"])
    draft_id = int(state_data["draft_id"])
    await message.bot.send_message(user_id, f"<b>Сообщение от администрации.</b>\nВаш черновик #{draft_id} <u>нуждается в правке перед публикацией</u>\n\n{message.html_text.strip()}", reply_markup=user_keyboards.to_draft(draft_id))

@admin_router.callback_query()
async def handle_admin_call(call: CallbackQuery, state: FSMContext):
    data = call.data.removeprefix("admin:").split(":")
    if data[0].isdigit():
        draft_id = int(data[0])
        user_id = int(data[1])
        async with get_session() as session: draft = await get_draft(session, draft_id)
        if data[2] == "post_draft":
            text = str(draft.final())
            draft_photos_dir = Path(draft.photo_url) if draft.photo_url else None
            message_ids = []
            if draft_photos_dir and draft_photos_dir.exists() and draft_photos_dir.is_dir():
                photos = [p for p in draft_photos_dir.iterdir() if p.is_file() and p.suffix.lower() == ".jpg"]
                if photos:
                    photos.sort()
                    media = [InputMediaPhoto(media=FSInputFile(p), caption=text if i == 0 else None) for i, p in enumerate(photos)]
                    x = await call.bot.send_media_group(media=media, chat_id=ELIXIR_CHAT_ID, message_thread_id=ELIXIR_THREAD_ID)
                    message_ids = [m.message_id for m in x[1:]]
                    x = x[0]
                else: x = await call.bot.send_message(chat_id=ELIXIR_CHAT_ID, text=text, message_thread_id=ELIXIR_THREAD_ID)
            else: x = await call.bot.send_message(chat_id=ELIXIR_CHAT_ID, text=text, message_thread_id=ELIXIR_THREAD_ID)
            async with get_session() as session: await update_draft(session, draft_id, SharedResultDraftUpdate(is_submitted=True))
            await call.message.edit_text(f"📣 Отзыв #{draft_id} <b>успешно опубликован админом {call.from_user.mention_html()}</b>", reply_markup=admin_keyboards.posted_draft(draft_id, x.message_id, x.get_url(include_thread_id=True), message_ids=message_ids))

        elif data[2] == "correction":
            await state.set_state(admin_states.DraftSubmission.correction)
            await state.set_data({"user_id": user_id, "draft_id": draft_id})
            await call.message.edit_text("Ответьте на это сообщение, <b>чтобы написать автору отзыва</b> с указанием нужных правок", reply_markup=admin_keyboards.back_to_draft(draft))

        elif data[2] == "back_to_draft":
            async with get_session() as session: draft = await get_draft(session, draft_id)
            if not draft.is_submitted:
                draft_photos_dir = Path(draft.photo_url) if draft.photo_url else None
                if draft_photos_dir and draft_photos_dir.exists() and draft_photos_dir.is_dir():
                    photos = [p for p in draft_photos_dir.iterdir() if p.is_file() and p.suffix.lower() == ".jpg"]
                    if photos:
                        photos.sort()
                        media = [InputMediaPhoto(media=FSInputFile(p), caption=draft.preview() if i == 0 else None) for i, p in enumerate(photos)]
                        await call.message.answer_media_group(media=media)

                    else: await call.message.answer(draft.preview())
                else: await call.message.answer(draft.preview())
                await call.message.answer("<b>Подтвердите публикацию</b> в ветке чата @peptide_rus кнопками ниже ⬇️", reply_markup=admin_keyboards.post_draft(draft))
            else: await call.message.edit_text(f"Отзыв #{draft_id} был уже опубликован")

    elif data[0] == "block_user":
        user_id = int(data[1])
        async with get_session() as session: user = await update_user(session, user_id, UserUpdate(blocked=True))
        await call.message.answer(f"🔐 Пользователь с ID <code>{user_id}</code> <b>успешно заблокирован админом {call.from_user.mention_html()}</b>\n<i>Пожалуйста, не удаляйте это сообщение из чата</i>", reply_markup=admin_keyboards.unblock_user(user_id))

    elif data[0] == "unblock_user":
        user_id = int(data[1])
        async with get_session() as session: user = await update_user(session, user_id, UserUpdate(blocked=False))
        await call.message.answer(f"🔓 Пользователь с ID <code>{user_id}</code> <b>успешно разблокирован админом {call.from_user.mention_html()}</b>\n<i>Пожалуйста, не удаляйте это сообщение из чата</i>")

    elif data[0] == "delete_review":
        draft_id = int(data[1])
        message_id = int(data[2])
        message_ids = [message_id]
        if len(data) == 4: message_ids += [int(i) for i in data[3].split("_")]
        await call.bot.delete_messages(ELIXIR_CHAT_ID, message_ids)
        async with get_session() as session: await update_draft(session, draft_id, SharedResultDraftUpdate(is_submitted=False))
        await call.message.edit_text(f"🗑️ Отзыв #{draft_id} <b>успешно удален из чата админом {call.from_user.mention_html()}</b>", reply_markup=admin_keyboards.recover_review(draft_id))

    elif data[0] == "recover_review":
        draft_id = int(data[1])
        async with get_session() as session: draft = await get_draft(session, draft_id)
        text = str(draft.final())
        draft_photos_dir = Path(draft.photo_url) if draft.photo_url else None
        message_ids = []
        if draft_photos_dir and draft_photos_dir.exists() and draft_photos_dir.is_dir():
            photos = [p for p in draft_photos_dir.iterdir() if p.is_file() and p.suffix.lower() == ".jpg"]
            if photos:
                photos.sort()
                media = [InputMediaPhoto(media=FSInputFile(p), caption=text if i == 0 else None) for i, p in enumerate(photos)]
                x = await call.bot.send_media_group(media=media, chat_id=ELIXIR_CHAT_ID, message_thread_id=ELIXIR_THREAD_ID)
                message_ids = [m.message_id for m in x[1:]]
                x = x[0]
            else: x = await call.bot.send_message(chat_id=ELIXIR_CHAT_ID, text=text, message_thread_id=ELIXIR_THREAD_ID)
        else: x = await call.bot.send_message(chat_id=ELIXIR_CHAT_ID, text=text, message_thread_id=ELIXIR_THREAD_ID)
        async with get_session() as session: await update_draft(session, draft_id, SharedResultDraftUpdate(is_submitted=True))
        await call.message.edit_text(f"♻️ Отзыв #{draft_id} <b>успешно возвращен в чат админом {call.from_user.mention_html()}</b>", reply_markup=admin_keyboards.posted_draft(draft_id, x.message_id, x.get_url(include_thread_id=True), message_ids=message_ids))
