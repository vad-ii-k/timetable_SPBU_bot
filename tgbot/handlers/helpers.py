import asyncio
from contextlib import suppress

from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _

from tgbot.cb_data import ScheduleCallbackFactory
from tgbot.config import bot
from tgbot.keyboards.inline import create_schedule_keyboard, create_schedule_subscription_keyboard
from tgbot.services.db_api.db_commands import database
from tgbot.services.schedule.getting_shedule import get_week_schedule


async def send_schedule(state: FSMContext, subscription: bool, tg_user_id: int) -> None:
    user = await database.get_user(tg_user_id=tg_user_id)
    settings = await database.get_settings(user)
    is_picture: bool = settings.schedule_view_is_picture
    data = await state.get_data()
    tt_id, user_type = int(data.get('tt_id')), data.get('user_type')
    schedule_text, schedule_name = await get_week_schedule(tt_id, user_type, week_counter=0)
    await bot.send_message(
        chat_id=tg_user_id,
        text=schedule_text,
        reply_markup=await create_schedule_keyboard(
            is_photo=is_picture, callback_data=ScheduleCallbackFactory(tt_id=tt_id, user_type=user_type)
        )
    )
    await state.update_data({'schedule_name': schedule_name})
    if subscription:
        await send_subscription_question(tg_user_id)


async def schedule_keyboard_helper(callback: CallbackQuery, text: str, callback_data: ScheduleCallbackFactory) -> None:
    is_picture = callback.message.content_type == "photo"
    # if is_picture:
    #     answer_msg = await callback.message.edit_media(
    #         media=InputMedia(media=InputFile("utils/image_converter/output.png"))
    #     )
    #     await answer_msg.edit_caption(caption=text)
    # else:

    await callback.message.answer(
        text=text,
        reply_markup=await create_schedule_keyboard(is_photo=is_picture, callback_data=callback_data)
    )


async def change_message_to_loading(message: Message) -> bool:
    message_content_type_is_photo = message.content_type == "photo"
    if message_content_type_is_photo:
        await message.edit_caption(_("🕒 <i>Загрузка...</i>"))
    else:
        await message.edit_text("⏳")
    return message_content_type_is_photo


async def _delete_message(message: Message, sleep_time: int = 0) -> None:
    await asyncio.sleep(sleep_time)
    with suppress(TelegramAPIError):
        await message.delete()


async def send_subscription_question(tg_user_id: int) -> None:
    answer_sub = await bot.send_message(
        chat_id=tg_user_id,
        text=_("⚙️ Хотите сделать это расписание своим основным?"),
        reply_markup=await create_schedule_subscription_keyboard()
    )
    asyncio.create_task(_delete_message(answer_sub, 30))
