from pathlib import Path
from typing import get_args
from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile, ReplyKeyboardRemove
from aiogram_media_group import media_group_handler

from config import PHOTOS_DIR, ADMIN_CHAT_ID, OWNER_TG_IDS
from src.bot.keyboards import user_keyboards, admin_keyboards
from src.bot.texts import user_texts
from src.bot.states import user_states
from src.database import get_session
from src.database.crud import get_user, create_user, update_user, create_draft, list_drafts, delete_draft, update_draft, get_draft
from src.database.schemas import SharedResultDraftCreate, SharedResultDraftRead, UserCreate, SharedResultDraftUpdate, Gender, UserUpdate
from src.helpers import send_draft_photos_if_exist

async def user_blocked_filter(obj: Message | CallbackQuery):
    user_id = obj.from_user.id
    message = getattr(obj, "message", obj)
    if not isinstance(message, Message) or not message.chat.type == ChatType.PRIVATE: return False
    async with get_session() as session:
        user = await get_user(session, user_id)
        if not user: user = await create_user(session, UserCreate(id=user_id))

    if user.blocked:
        await obj.bot.send_message(user_id, user_texts.blocked.replace('*', obj.from_user.mention_html()), reply_markup=user_keyboards.support)
        return False

    return True

ADMIN_MESSAGES: dict[int, int] = {}

user_router = Router(name="user")
user_router.message.filter(user_blocked_filter)
user_router.callback_query.filter(user_blocked_filter, lambda call: call.data.startswith("user"))

@user_router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    async with get_session() as session:
        user = await get_user(session, user_id)
        if not user: await create_user(session, UserCreate(id=user_id))

    x = await message.answer('delete_keyboard', reply_markup=ReplyKeyboardRemove())
    await x.delete()
    await message.answer(user_texts.greetings.replace('*', message.chat.full_name), reply_markup=user_keyboards.user_menu)
    await message.delete()
    await state.clear()

@user_router.message(Command('unblock'), lambda message: message.from_user.id in OWNER_TG_IDS)
async def handle_unblock(message: Message):
    user_id = message.text.removeprefix("/unblock ").strip()
    if not user_id or not user_id.isdigit(): await message.answer(f"Ошибка команды: <code>/unblock айди_телеграм</code>")
    else:
        user_id = int(user_id)
        async with get_session() as session:
            user = await get_user(session, user_id)
            if not user: user = await create_user(session, UserCreate(id=user_id))
            user = await update_user(session, user.id, UserUpdate(blocked=False))
        await message.bot.send_message(ADMIN_CHAT_ID, f"🔓 Пользователь с ID {user.id} <b>успешно разблокирован админом {message.from_user.mention_html()}</b>")

@user_router.message(Command('block'), lambda message: message.from_user.id in OWNER_TG_IDS)
async def handle_unblock(message: Message):
    user_id = message.text.removeprefix("/block ").strip()
    if not user_id or not user_id.isdigit(): await message.answer(f"Ошибка команды: <code>/block айди_телеграм</code>")
    else:
        user_id = int(user_id)
        async with get_session() as session:
            user = await get_user(session, user_id)
            if not user: user = await create_user(session, UserCreate(id=user_id))
            user = await update_user(session, user.id, UserUpdate(blocked=True))

        await message.bot.send_message(ADMIN_CHAT_ID, f"🔐 Пользователь с ID {user.id} <b>успешно заблокирован админом {message.from_user.mention_html()}</b>")

@user_router.message(user_states.MessageAdmin.phone, lambda message: message.contact or message.text.strip())
async def handle_phone_message(message: Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
        if phone[0] != "+": phone = f"+{phone}"
        await state.update_data(phone=phone)
        x = await message.answer('/delete_keyboard', reply_markup=ReplyKeyboardRemove())
        await x.delete()
        await message.answer("💬 Отлично, теперь отправьте сообщение, и оно будет направлено администрации в ту же секунду 👨🏻‍💻", reply_markup=user_keyboards.main_menuu)

    else:
        state_data = await state.get_data()
        phone = state_data.get("phone", f"<b>\nНомер не указан, отправителю не нужна обратная связь</b>, но все же можете отправить человеку сообщение <i>от имени бота</i> следующим образом:\n<code>/send_message {message.from_user.id} сообщение</code>")
        await message.bot.send_message(ADMIN_CHAT_ID, f"📩 <b>Новое сообщение для администрации!!\n\n{message.from_user.full_name} пишет:</b>\n{message.html_text}\n\n<b>Доступная информация по отправителю</b>\n{('@'+message.from_user.username) if message.from_user.username else 'Нет никнейма'}\nID: <code>{message.from_user.id}</code>\n{phone}", reply_markup=admin_keyboards.messaged_admins(message.from_user.id))
        ADMIN_MESSAGES[message.from_user.id] = 1 if message.from_user.id not in ADMIN_MESSAGES else ADMIN_MESSAGES[message.from_user.id] + 1
        x = await message.answer('/delete_keyboard', reply_markup=ReplyKeyboardRemove())
        await x.delete()
        await message.answer(f"🎉 Ваше сообщение <b>было успешно отправлено</b>", reply_markup=user_keyboards.main_menuu)

@user_router.message(user_states.EditDraft.photo, F.photo)
async def handle_single_photo(message: Message, state: FSMContext):
    state_data = await state.get_data()
    review_photos_dir: Path = state_data["review_photos_dir"]
    draft_id: int = state_data["draft_id"]

    file_id = message.photo[-1].file_id
    file = await message.bot.get_file(file_id)
    await message.bot.download_file(file.file_path, destination=review_photos_dir / f"{file_id}.jpg")
    async with get_session() as session: draft = await get_draft(session, draft_id)
    if draft.user_id != message.from_user.id: return await message.answer(f"Ошибка: Черновик #{draft.id} <b>не в вашем владении!</b>")

    await send_draft_photos_if_exist(message, draft)
    await message.answer(f"Значение для <b>фото 'до/после' (опционально) черновика #{draft_id}</b> успешно изменено на 1")
    return await message.answer(str(draft), reply_markup=user_keyboards.draft_keyboard(**SharedResultDraftRead.model_validate(draft).model_dump()))

@user_router.message(F.media_group_id, user_states.EditDraft.photo)
@media_group_handler
async def album_handler(messages: list[Message], state: FSMContext):
    photos = [m.photo[-1].file_id for m in messages if m.photo]
    if len(photos) == 0: return await messages[-1].answer("Ошибка. В медиа не было найдено фотографий")
    elif len(photos) > 3: photos = photos[:3]
    state_data = await state.get_data()
    review_photos_dir = state_data["review_photos_dir"]
    draft_id = state_data["draft_id"]
    for photo in photos:
        file = await messages[-1].bot.get_file(photo)
        await messages[-1].bot.download_file(file.file_path, review_photos_dir / f"{file.file_id}.jpg")

    async with get_session() as session: draft = await get_draft(session, draft_id)
    if draft.user_id != messages[-1].from_user.id: return await messages[-1].answer(f"Ошибка: Черновик #{draft.id} <b>не в вашем владении!</b>")
    await send_draft_photos_if_exist(messages[-1], draft)
    await messages[-1].answer(f"Значение для <b>фото 'до/после' (опционально) черновика #{draft_id}</b> успешно изменено на {len(photos)}")
    return await messages[-1].answer(str(draft), reply_markup=user_keyboards.draft_keyboard(**SharedResultDraftRead.model_validate(draft).model_dump()))

@user_router.message(StateFilter(user_states.EditDraft))
async def handle_edit_draft(message: Message, state: FSMContext):
    state_data = await state.get_data()
    print(await state.get_state(), state_data)
    what = state_data["what"]
    what_kword = state_data["what_kword"]
    draft_id = state_data["draft_id"]
    if what == 'age':
        if not message.text.isdigit(): return await message.answer(user_texts.send_whole_num)
        else:
            new_value = int(message.text.strip())
            draft_update = SharedResultDraftUpdate(age=new_value)
            async with get_session() as session: draft = await update_draft(session, draft_id, draft_update)

    elif 'weight' in what or what == 'height':
        if not message.text.replace(',', '.').replace('.', '').isdigit(): return await message.answer(user_texts.send_num_weight)
        else:
            new_value = round(float(message.text.strip().replace(',', '.')), 2)
            draft_update = SharedResultDraftUpdate(**{what: new_value})
            async with get_session() as session: draft = await update_draft(session, draft_id, draft_update)

    elif what == 'gender':
        if message.text.strip() not in get_args(Gender): return await message.answer(user_texts.wrong_gender, reply_markup=user_keyboards.choose_gender)
        else:
            new_value = message.text.strip()
            draft_update = SharedResultDraftUpdate(**{what: new_value})
            async with get_session() as session: draft = await update_draft(session, draft_id, draft_update)

    elif state == user_states.EditDraft.photo:
        if not message.photo: return await message.answer("Ошибка. <b>Отправьте фотографии (до 3х штук)</b>")
        else:
            review_photos_dir = state_data["review_photos_dir"]
            file_id = message.photo[-1].file_id
            file = await message.bot.get_file(file_id)
            await message.bot.download_file(file.file_path, destination=review_photos_dir / f"{file_id}.jpg")
            await message.answer("Фотография для черновика <b>успешно сохранена</b>")
            new_value = 1

    else:
        new_value = message.text.strip()
        draft_update = SharedResultDraftUpdate(**{what: new_value})
        async with get_session() as session: draft = await update_draft(session, draft_id, draft_update)

    await state.clear()
    await send_draft_photos_if_exist(message, draft)
    await message.answer(f"Значение для <b>{what_kword.lower()} черновика #{draft_id} </b>успешно обновлено на <u>{new_value}</u>")
    return await message.answer(str(draft), reply_markup=user_keyboards.draft_keyboard(**SharedResultDraftRead.model_validate(draft).model_dump()))

@user_router.callback_query()
async def handle_user_call(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    async with get_session() as session: user = await get_user(session, user_id)
    await state.get_data()
    data = call.data.removeprefix("user:").split(":")
    if data[0] == "share_result":
        if data[1] == "start":
            if not user.accepted_terms: await call.message.edit_text(user_texts.share_result_terms, reply_markup=user_keyboards.share_result_terms)
            else:
                async with get_session() as session: user_drafts = await list_drafts(session, user_id)
                if not user_drafts: await call.message.edit_text(user_texts.share_result_anonymity.replace('*', call.from_user.username or call.from_user.full_name), reply_markup=user_keyboards.share_result_anonymity)
                else: await call.message.edit_text(user_texts.view_drafts, reply_markup=user_keyboards.view_drafts(user_drafts))

        elif data[1] == "anonymity":
            print(data)
            draft_create = SharedResultDraftCreate(user_id=user_id)
            if data[2] == "view": return call.message.edit_text(user_texts.share_result_anonymity.replace('*', call.from_user.full_name), reply_markup=user_keyboards.share_result_anonymity)
            elif data[2] == "no": draft_create.author = f"@{call.from_user.username}" or call.from_user.full_name
            async with get_session() as session: draft = await create_draft(session, draft_create)
            if draft.user_id != call.from_user.id: return await call.message.edit_text(f"Ошибка: Черновик #{draft.id} <b>не в вашем владении!</b>")
            else: await call.message.edit_text(str(draft), reply_markup=user_keyboards.draft_keyboard(**SharedResultDraftRead.model_validate(draft).model_dump()))

    elif data[0] == "terms":
        if data[1] == "yes":
            async with get_session() as session: await update_user(session, user_id, UserUpdate(accepted_terms=True))
            await call.message.edit_text(user_texts.share_result_anonymity.replace('*', call.from_user.full_name), reply_markup=user_keyboards.share_result_anonymity)


    elif data[0] == "edit_draft":
        if data[1].isdigit():
            draft_id = int(data[1])
            async with get_session() as session: draft = await get_draft(session, draft_id)
            if draft.user_id != call.from_user.id: return await call.message.edit_text(f"Ошибка: Черновик #{draft.id} <b>не в вашем владении!</b>")
            if not draft: await call.message.edit_text(user_texts.old_draft, reply_markup=user_keyboards.main_menu)
            else:
                if data[2] == "view":
                    if draft.photo_url:
                        review_photos_dir = Path(draft.photo_url)
                        media = [InputMediaPhoto(media=FSInputFile(path), caption=f"Фотографии черновика #{draft_id}") for path in review_photos_dir.iterdir() if path.is_file() and path.suffix == ".jpg"]
                        if media: await call.message.answer_media_group(media)
                        await call.message.answer(str(draft), reply_markup=user_keyboards.draft_keyboard(**SharedResultDraftRead.model_validate(draft).model_dump()))

                    else: await call.message.edit_text(str(draft), reply_markup=user_keyboards.draft_keyboard(**SharedResultDraftRead.model_validate(draft).model_dump()))
                elif data[2] in list(SharedResultDraftRead.model_fields.keys()):
                    if getattr(draft, data[2], None):
                        async with get_session() as session: draft = await update_draft(session, draft_id, SharedResultDraftUpdate(**{data[2]: None if data[2] != "gender" else "Не указан"}))
                        if draft.user_id != call.from_user.id: return await call.message.edit_text(f"Ошибка: Черновик #{draft.id} <b>не в вашем владении!</b>")
                        try: await call.message.edit_reply_markup(reply_markup=user_keyboards.draft_keyboard(**SharedResultDraftRead.model_validate(draft).model_dump()))
                        except: pass

                    keyboard = call.message.reply_markup.inline_keyboard
                    what: str = None
                    for row in keyboard:
                        for button in row:
                            if ':'.join(data) in button.callback_data:
                                what = button.text.replace("❌ ", '').replace("✅ ", "")
                                break

                    new_state = getattr(user_states.EditDraft, data[2], None)
                    await call.message.answer(f'<b>Старое значение убрано для {what.lower()}</b>. Введите новое\n\nВозврат в главное меню — /start', reply_markup=user_keyboards.choose_gender if data[2] =='gender' else None)
                    await state.set_state(new_state)
                    await state.update_data(what=data[2], draft_id=draft_id, what_kword=what)

                elif data[2] == "photo":
                    user_photos_dir = PHOTOS_DIR / f"{user_id}"
                    user_photos_dir.mkdir(exist_ok=True)
                    review_photos_dir = user_photos_dir / f"{draft_id}"
                    review_photos_dir.mkdir(exist_ok=True)
                    for p in review_photos_dir.iterdir(): p.unlink()
                    try: await call.message.edit_reply_markup(reply_markup=user_keyboards.draft_keyboard(**SharedResultDraftRead.model_validate(draft).model_dump()))
                    except: pass
                    await call.message.answer(f"<b>Прошлые фотографии</b> черновика #{draft_id} удалены. Отправьте новые (до 3х штук)\n\nГлавное меню — /start")
                    await state.set_state(user_states.EditDraft.photo)
                    await state.set_data({"review_photos_dir": review_photos_dir, "draft_id": draft_id})
                    async with get_session() as session: await update_draft(session, draft_id, SharedResultDraftUpdate(photo_url=f"{review_photos_dir.absolute()}"))

                elif data[2] == "preview":
                    draft_photos_dir = Path(draft.photo_url) if draft.photo_url else None
                    if draft_photos_dir and draft_photos_dir.exists() and draft_photos_dir.is_dir():
                        photos = [p for p in draft_photos_dir.iterdir() if p.is_file() and p.suffix.lower() == ".jpg"]
                        if photos:
                            photos.sort()  # optional: stable order
                            media = [InputMediaPhoto(media=FSInputFile(p), caption=draft.preview() if i == 0 else None) for i, p in enumerate(photos)]
                            await call.message.answer_media_group(media=media)
                            await call.message.delete()
                        else: await call.message.edit_text(draft.preview())
                    else: await call.message.edit_text(draft.preview())
                    keyboard = user_keyboards.preview_keyboard(draft)
                    text = user_texts.mandatory_filled if len(keyboard.inline_keyboard) == 3 else user_texts.mandatory_unfilled
                    await call.message.answer(text, reply_markup=keyboard)

    elif data[0] == "delete_draft":
        if data[1].isdigit():
            draft_id = int(data[1])
            async with get_session() as session:
                draft = await get_draft(session, draft_id)
                if not draft: await call.message.answer(user_texts.old_draft, reply_markup=user_keyboards.main_menu)
                elif draft.user_id != call.from_user.id: return await call.message.edit_text(f"Ошибка: Черновик #{draft.id} <b>не в вашем владении!</b>")
                else:
                    await delete_draft(session, draft)
                    await call.message.answer(f"Черновик {draft.id} успешно удален")
                    return await handle_start(call.message, state)

    elif data[0] == "post_draft":
        draft_id = int(data[1])
        async with get_session() as session: draft = await get_draft(session, draft_id)
        if draft.user_id != call.from_user.id: return await call.message.edit_text(f"Ошибка: Черновик #{draft.id} <b>не в вашем владении!</b>")
        draft_photos_dir = Path(draft.photo_url) if draft.photo_url else None
        if draft_photos_dir and draft_photos_dir.exists() and draft_photos_dir.is_dir():
            photos = [p for p in draft_photos_dir.iterdir() if p.is_file() and p.suffix.lower() == ".jpg"]
            if photos:
                photos.sort()
                media = [InputMediaPhoto(media=FSInputFile(p), caption=draft.preview() if i == 0 else None) for i, p in enumerate(photos)]
                await call.bot.send_media_group(chat_id=ADMIN_CHAT_ID, media=media)

            else: await call.bot.send_message(chat_id=ADMIN_CHAT_ID, text=draft.preview())
        else: await call.bot.send_message(chat_id=ADMIN_CHAT_ID, text=draft.preview())
        await call.bot.send_message(chat_id=ADMIN_CHAT_ID, text="<b>Подтвердите публикацию</b> в ветке чата @peptide_rus кнопками ниже ⬇️", reply_markup=admin_keyboards.post_draft(draft))
        await call.message.answer(f"Черновик #{draft_id} <b>отправлен администрации на публикацию</b>", reply_markup=user_keyboards.main_menuu)

    elif data[0] == "main_menu": await handle_start(call.message, state)
    elif data[0] == "main_menuu":
        async with get_session() as session:
            user = await get_user(session, user_id)
            if not user: await create_user(session, UserCreate(id=user_id))

        await call.message.answer(user_texts.greetings.replace('*', call.message.chat.full_name), reply_markup=user_keyboards.user_menu)
        await state.clear()

    elif data[0] == "message_admins":
        if data[1] == "start":
            if user_id not in ADMIN_MESSAGES or ADMIN_MESSAGES[user_id] < 3:
                await call.message.answer(user_texts.message_admins_start, reply_markup=user_keyboards.message_admin_phone)
                await state.set_state(user_states.MessageAdmin.phone)

            else: await call.message.edit_text("<b>🙃 Сожалеем, в час можно отправить до 3х сообщений</b>", reply_markup=user_keyboards.main_menuu)

    return None
