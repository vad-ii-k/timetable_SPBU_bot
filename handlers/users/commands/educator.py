from aiogram.types import Message

from loader import dp
from states.choice_teacher import TeacherChoice


@dp.message_handler(commands='educator', state="*")
async def bot_educator_command(message: Message):
    await message.answer("🔎 Введите фамилию преподавателя для поиска:")
    await TeacherChoice.getting_choice.set()
