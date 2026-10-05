from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.states.game_states import GameStates
from bot.keyboards.difficulty import game_modes
from bot.services.game_service import get_game
from bot.services.statistics import details, overall_ranking
from bot.database.db import get_overall_statistics
from bot.texts.messages import (
    CHOOSE_DIFFICULTY,
    STATS,
    OVERALL_STATS,
)
from bot.services.message_service import (
    delete_last_menu_message,
    save_menu_message,
)
from bot.services.activation_service import is_activated

router = Router()


# ============================================================
# ПРОВЕРКА АКТИВАЦИИ
# ============================================================

def check_activation(user_id: int) -> bool:
    return is_activated(user_id)


async def activation_required(message: Message):
    await message.answer(
        "🔐 Доступ закрыт.\n\n"
        "Сначала активируйте бота через /start."
    )


# ============================================================
# НОВАЯ ИГРА
# ============================================================

@router.message(Command("newgame"))
async def new_game(
    message: Message,
    state: FSMContext
):
    if not check_activation(message.from_user.id):
        await activation_required(message)
        return

    await delete_last_menu_message(message, state)

    await state.clear()
    await state.set_state(
        GameStates.choosing_difficulty
    )

    sent = await message.answer(
        CHOOSE_DIFFICULTY,
        reply_markup=game_modes(),
    )

    await save_menu_message(sent, state)


# ============================================================
# СТАТИСТИКА ТЕКУЩЕЙ ИГРЫ
# ============================================================

@router.message(Command("stats"))
async def current_statistics(
    message: Message,
    state: FSMContext
):
    if not check_activation(message.from_user.id):
        await activation_required(message)
        return

    await delete_last_menu_message(message, state)

    game = get_game(message.chat.id)

    if not game:
        sent = await message.answer(
            "📊 Сейчас нет активной игры."
        )
        await save_menu_message(sent, state)
        return

    sent = await message.answer(
        STATS.format(
            stats=details(game.players)
        )
    )

    await save_menu_message(sent, state)


# ============================================================
# ОБЩАЯ СТАТИСТИКА
# ============================================================

@router.message(Command("overall"))
async def overall_statistics(
    message: Message,
    state: FSMContext
):
    if not check_activation(message.from_user.id):
        await activation_required(message)
        return

    await delete_last_menu_message(message, state)

    stats = await get_overall_statistics()

    sent = await message.answer(
        OVERALL_STATS.format(
            stats=overall_ranking(stats)
        )
    )

    await save_menu_message(sent, state)


# ============================================================
# СТАРЫЙ CALLBACK "НАЧАТЬ ИГРУ"
# ============================================================

@router.callback_query(F.data == "start_game")
async def start_game_callback(
    c: CallbackQuery,
    state: FSMContext
):
    if not check_activation(c.from_user.id):
        await c.answer(
            "🔐 Сначала активируйте бота через /start.",
            show_alert=True,
        )
        return

    await delete_last_menu_message(
        c.message,
        state
    )

    await state.clear()
    await state.set_state(
        GameStates.choosing_difficulty
    )

    await c.message.edit_text(
        CHOOSE_DIFFICULTY,
        reply_markup=game_modes(),
    )

    await state.update_data(
        last_menu_message_id=c.message.message_id
    )

    await c.answer()