import asyncio
import logging

import aioredis
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n

from tgbot.config import app_config, bot
from tgbot.handlers.admin import admin_router
from tgbot.handlers.commands import router as commands_router, set_commands
from tgbot.handlers.search_educator import router as search_educator_router
from tgbot.handlers.search_group import router as search_group_router
from tgbot.handlers.settings import router as settings_router
from tgbot.handlers.start_menu import router as start_menu_router
from tgbot.handlers.student_navigation import router as student_navigation_router
from tgbot.middlewares.config import ConfigMessageMiddleware, ConfigCallbackMiddleware, LanguageI18nMiddleware
from tgbot.services import broadcaster
from tgbot.services.db_api.db_models import create_db

logger = logging.getLogger(__name__)


async def on_startup(_bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "🆙 The bot has been launched!")


def register_global_middlewares(dispatcher: Dispatcher, i18n: I18n):
    dispatcher.message.middleware(ConfigMessageMiddleware(app_config))
    dispatcher.callback_query.middleware(ConfigCallbackMiddleware(app_config))
    dispatcher.update.outer_middleware(LanguageI18nMiddleware(i18n))


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    root_logger = logging.getLogger("gino")
    if root_logger.level == logging.NOTSET:
        root_logger.setLevel(logging.WARN)
    logger.info("Starting bot...")

    await create_db()

    await set_commands(bot)

    if app_config.tg_bot.use_redis:
        redis = aioredis.Redis(
            host=app_config.redis.host,
            port=app_config.redis.port,
            password=app_config.redis.password,
            db=1
        )
        storage = RedisStorage(redis)
    else:
        storage = MemoryStorage()
    dispatcher = Dispatcher(storage=storage)

    for router in [
        commands_router,
        admin_router,
        start_menu_router,
        search_group_router,
        student_navigation_router,
        search_educator_router,
        settings_router,
    ]:
        dispatcher.include_router(router)

    i18n = I18n(path="tgbot/locales", default_locale="ru", domain="messages")
    register_global_middlewares(dispatcher, i18n)

    await on_startup(bot, app_config.tg_bot.admin_ids)
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("The bot has been disabled!")
