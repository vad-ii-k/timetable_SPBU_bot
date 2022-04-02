import logging

from aiogram.types import CallbackQuery

from keyboards.inline.callback_data import user_status_callback
from keyboards.inline.student_navigaton_buttons import create_study_divisions_keyboard
from loader import dp
from states.choice_teacher import TeacherChoice
from utils.tt_api import get_study_divisions


@dp.callback_query_handler(user_status_callback.filter(name="student group"))
async def handling_group_of_student(call: CallbackQuery):
    await call.answer(cache_time=5)
    callback_data = call.data
    logging.info(f"call = {callback_data}")
    await call.message.edit_text("В разработке...")
    # await call.message.edit_text("Введите название группы:\n*<i>например, 20Б.09-мм</i>")


@dp.callback_query_handler(user_status_callback.filter(name="student navigation"))
async def handling_group_of_student(call: CallbackQuery):
    await call.answer(cache_time=5)
    callback_data = call.data
    logging.info(f"call = {callback_data}")

    await call.message.edit_text("Выберите направление: ")
    study_divisions = await get_study_divisions()
    await call.message.edit_reply_markup(reply_markup=await create_study_divisions_keyboard(study_divisions))


@dp.callback_query_handler(user_status_callback.filter(name="teacher"))
async def handling_group_of_student(call: CallbackQuery):
    await call.answer(cache_time=5)
    callback_data = call.data
    logging.info(f"call = {callback_data}")

    await call.message.edit_text("Введите Вашу фамилию:")

    await TeacherChoice.getting_choice.set()
