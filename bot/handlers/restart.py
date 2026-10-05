from aiogram import Router, F

from aiogram.types import CallbackQuery

from aiogram.fsm.context import FSMContext

from bot.services.game_service import delete_game
from bot.database.db import delete_saved_game
from bot.states.game_states import GameStates
from bot.keyboards.restart import confirm
from bot.keyboards.difficulty import game_modes
from bot.texts.messages import RESTART, CHOOSE_DIFFICULTY
from bot.services.activation_service import is_activated

router = Router()


@router.callback_query(F.data == "restart")
async def restart(c: CallbackQuery):

    if not is_activated(c.from_user.id):
        await c.answer(
            "🔐 Сначала активируйте бота через /start.",
            show_alert=True,
        )
        return

    await c.message.answer(
        RESTART,
        reply_markup=confirm()
    )

    await c.answer()


@router.callback_query(F.data == "restart_no")
async def no(c: CallbackQuery):

    if not is_activated(c.from_user.id):
        await c.answer(
            "🔐 Сначала активируйте бота через /start.",
            show_alert=True,
        )
        return

    try:
        await c.message.delete()
    except Exception:
        pass

    await c.answer("Игра продолжена.")


@router.callback_query(F.data == "restart_yes")
async def yes(c: CallbackQuery, state: FSMContext):

    if not is_activated(c.from_user.id):
        await c.answer(
            "🔐 Сначала активируйте бота через /start.",
            show_alert=True,
        )
        return

    delete_game(c.message.chat.id)
    await delete_saved_game(c.message.chat.id)

    await state.clear()
    await state.set_state(GameStates.choosing_difficulty)

    try:
        await c.message.edit_text(
            CHOOSE_DIFFICULTY,
            reply_markup=game_modes()
        )
    except Exception:
        await c.message.answer(
            CHOOSE_DIFFICULTY,
            reply_markup=game_modes()
        )

    await c.answer()