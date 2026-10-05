from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from bot.states.game_states import GameStates
from bot.keyboards.difficulty import player_count
from bot.keyboards.game import open_card
from bot.services.game_service import create_game
from bot.texts.messages import CHOOSE_PLAYERS, ASK_PLAYER_NAME, YOUR_TURN

router = Router()

@router.callback_query(GameStates.choosing_difficulty, F.data.startswith("mode:"))
async def mode(c: CallbackQuery, state: FSMContext):
    game_mode = int(c.data.split(":")[1])
    await state.update_data(mode=game_mode)
    await state.set_state(GameStates.choosing_players)
    await c.message.edit_text(CHOOSE_PLAYERS, reply_markup=player_count())
    await c.answer()

@router.callback_query(GameStates.choosing_players, F.data.startswith("players:"))
async def count(c: CallbackQuery, state: FSMContext):
    await state.update_data(count=int(c.data.split(":")[1]), names=[])
    await state.set_state(GameStates.entering_name)
    await c.message.edit_text(ASK_PLAYER_NAME.format(number=1))
    await c.answer()

@router.message(GameStates.entering_name)
async def name(m: Message, state: FSMContext):
    # Кнопки постоянного меню не должны становиться именами игроков.
    if m.text in {"🎮 НОВАЯ ИГРА", "📊 СТАТИСТИКА", "🏆 ОБЩАЯ СТАТИСТИКА", "🔄 РЕСТАРТ"}:
        return
    player_name = m.text.strip()[:30] if m.text else ""
    if not player_name:
        await m.answer("Введите имя текстом.")
        return
    d = await state.get_data()
    names = d["names"]
    names.append(player_name)
    await state.update_data(names=names)
    if len(names) < d["count"]:
        await m.answer(ASK_PLAYER_NAME.format(number=len(names) + 1))
        return
    game = create_game(m.chat.id, d["mode"], names)
    await state.set_state(GameStates.waiting_open)
    await m.answer(YOUR_TURN.format(player=game.player.name), reply_markup=open_card())
