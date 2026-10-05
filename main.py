import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import BOT_TOKEN
from bot.database.db import init_db, close_db, restore_games
from bot.services.game_service import ACTIVE_GAMES
from bot.handlers import start, menu as menu_handler, players, game, statistics, restart, admin, activation


async def set_bot_commands(bot: Bot):
    # Именно эти три пункта будут отображаться в кнопке «Меню» Telegram.
    await bot.set_my_commands([
        BotCommand(command="newgame", description="🎮 Новая игра"),
        BotCommand(command="stats", description="📊 Статистика"),
        BotCommand(command="overall", description="🏆 Общая статистика"),
    ])


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set. Put it into .env")

    await init_db()
    await restore_games(ACTIVE_GAMES)

    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_routers(
        start.router,
        menu_handler.router,
        players.router,
        game.router,
        statistics.router,
        restart.router,
        admin.router,
        activation.router
    )
    try:
        await set_bot_commands(bot)
        await dp.start_polling(bot)
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
