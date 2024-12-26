""" Auxiliary functions for event handling """

import asyncio
import re
from contextlib import suppress

from aiogram.enums import ContentType
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from tgbot.config import bot
from tgbot.keyboards.inline import create_schedule_keyboard, create_schedule_subscription_keyboard
from tgbot.misc.cb_data import ScheduleCallbackFactory
from tgbot.services.db_api.db_commands import database
from tgbot.services.schedule.getting_shedule import get_image_week_schedule, get_text_week_schedule


async def send_schedule(state: FSMContext, subscription: bool, tg_user_id: int) -> None:
    """
    Function for sending a message with a schedule after selecting a group or teacher
    :param state:
    :param subscription: if true, an extra message is sent with a question about subscribing to the schedule
    :param tg_user_id: telegram user id
    """
    user = await database.get_user(tg_user_id=tg_user_id)
    settings = await database.get_settings(user)
    data = await state.get_data()
    tt_id, user_type = int(data.get("tt_id")), data.get("user_type")
    is_picture = settings.schedule_view_is_picture
    reply_markup = await create_schedule_keyboard(
        is_photo=is_picture, callback_data=ScheduleCallbackFactory(tt_id=tt_id, user_type=user_type)
    )
    if is_picture:
        schedule_text, photo = await get_image_week_schedule(tt_id, user_type, week_counter=0)
        await bot.send_document(chat_id=tg_user_id, document=photo, caption=schedule_text, reply_markup=reply_markup)
        schedule_name = re.findall(r">(.*)<", schedule_text)[0]
    else:
        schedule_text, schedule_name = await get_text_week_schedule(tt_id, user_type, week_counter=0)
        await bot.send_message(chat_id=tg_user_id, text=schedule_text, reply_markup=reply_markup)
    await state.update_data({"schedule_name": schedule_name})

    current_main_schedule = await database.get_main_schedule(user.user_id)
    if subscription and (current_main_schedule is None or schedule_name != current_main_schedule.name):
        await send_subscription_question(tg_user_id)


async def schedule_keyboard_helper(
    callback: CallbackQuery,
    callback_data: ScheduleCallbackFactory,
    text: str,
    photo: BufferedInputFile | None = None,
) -> None:
    """
    Sends a message with a schedule depending on the type of content
    :param callback:
    :param callback_data:
    :param text:
    :param photo:
    """
    is_photo = photo is not None
    reply_markup = await create_schedule_keyboard(is_photo=is_photo, callback_data=callback_data)
    if is_photo:
        await callback.message.answer_document(document=photo, caption=text, reply_markup=reply_markup)
    else:
        await callback.message.answer(text=text, reply_markup=reply_markup)


async def change_message_to_loading(message: Message) -> None:
    """
    Changes the message to bootable
    :param message:
    """
    if message.content_type == ContentType.DOCUMENT:
        await message.edit_caption(caption=_("🕒 <i>Загрузка...</i>"))
    else:
        await message.edit_text("⏳")


async def delete_message(message: Message, sleep_time: int = 0) -> None:
    """
    Delayed deletion of a message ignoring errors
    :param message:
    :param sleep_time: number of seconds after which the message will be deleted
    """
    await asyncio.sleep(sleep_time)
    with suppress(TelegramAPIError, TelegramBadRequest):
        await message.delete()


async def send_subscription_question(tg_user_id: int) -> None:
    """
    Sending a message with a subscription question
    :param tg_user_id: telegram user id
    """
    answer_sub = await bot.send_message(
        chat_id=tg_user_id,
        text=_(
            "ℹ️ Для быстрого доступа 💨 к расписанию командой /my_schedule "
            "и возможности настроить уведомления 🔔 о предстоящих занятиях необходимо подписаться на расписание\n"
            "⚙️ Хотите сделать это расписание своим основным?"
        ),
        reply_markup=await create_schedule_subscription_keyboard(),
    )
    asyncio.create_task(delete_message(answer_sub, 60))
