from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.services.game_service import get_game
from bot.services.statistics import details
from bot.texts.messages import STATS
from bot.services.message_service import (
    delete_last_menu_message,
    save_menu_message,
)
from bot.services.activation_service import is_activated

router = Router()


# Совместимость со старой inline-кнопкой.
@router.callback_query(F.data == "statistics")
async def stats(c: CallbackQuery, state):
    if not is_activated(c.from_user.id):
        await c.answer(
            "🔐 Сначала активируйте бота через /start.",
            show_alert=True,
        )
        return

    await delete_last_menu_message(
        c.message,
        state
    )

    game = get_game(c.message.chat.id)

    if not game:
        await c.answer(
            "Статистика текущей игры недоступна.",
            show_alert=True,
        )
        return

    sent = await c.message.answer(
        STATS.format(
            stats=details(game.players)
        )
    )

    await save_menu_message(
        sent,
        state
    )

    await c.answer()