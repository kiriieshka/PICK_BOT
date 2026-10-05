import asyncio

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from bot.states.game_states import GameStates
from bot.services.game_service import get_game
from bot.services.card_service import CARDS
from bot.services.statistics import ranking
from bot.keyboards.game import start_timer, result, next_player, open_card
from bot.texts.messages import (
    CARD_OPENED,
    TIMER,
    SUCCESS,
    FAIL,
    TIMEOUT,
    RESULTS,
    YOUR_TURN,
)
from bot.database.db import save_game, save_history, delete_saved_game


router = Router()


# ============================================================
# ТАЙМЕР
# ============================================================

async def timeout_watcher(message, chat_id, state, card_id):
    game = get_game(chat_id)

    if not game or game.current_card != card_id:
        return

    # Если у карточки нет ограничения по времени,
    # таймер не запускаем.
    if CARDS[card_id]["time"] is None:
        return

    while game.current_card == card_id:
        await asyncio.sleep(0.5)

        if game.current_card != card_id:
            return

        time_left = game.time_left()

        if time_left is not None and time_left <= 0:
            game.fail()

            await save_game(chat_id, game)
            await state.set_state(GameStates.waiting_next)

            try:
                await message.edit_caption(
                    caption=TIMEOUT.format(
                        player=game.player.name
                    ),
                    reply_markup=next_player(),
                )
            except Exception:
                pass

            return


# ============================================================
# ОТКРЫТИЕ КАРТОЧКИ
# ============================================================

@router.callback_query(
    GameStates.waiting_open,
    F.data == "open_card"
)
async def open_card_handler(
    c: CallbackQuery,
    state: FSMContext
):
    game = get_game(c.message.chat.id)

    if not game:
        await c.answer(
            "Игра не найдена. Начните заново.",
            show_alert=True,
        )
        return

    cid = game.draw()

    if cid is None:
        await finish_game(c, game)
        return

    card = CARDS[cid]

    # Красивое отображение времени
    if card["time"] is None:
        time_text = "Без ограничения"
    else:
        time_text = f"{card['time']} сек."

    try:
        sent = await c.message.answer_photo(
            FSInputFile(card["file"]),
            caption=CARD_OPENED.format(
                player=game.player.name,
                seconds=time_text,
            ),
            reply_markup=start_timer(),
        )

    except (FileNotFoundError, TypeError):
        await c.message.answer(
            f"⚠️ Не найден PNG карточки №{cid}:\n"
            f"{card['file']}"
        )
        await c.answer()
        return

    await c.message.delete()

    await state.update_data(
        card_message_id=sent.message_id
    )

    await state.set_state(GameStates.waiting_start)

    await save_game(
        c.message.chat.id,
        game,
    )

    await c.answer()


# ============================================================
# СТАРТ ВЫПОЛНЕНИЯ
# ============================================================

@router.callback_query(
    GameStates.waiting_start,
    F.data == "start_timer"
)
async def start(
    c: CallbackQuery,
    state: FSMContext
):
    game = get_game(c.message.chat.id)

    if not game or game.current_card is None:
        await c.answer("Карточка уже завершена.")
        return

    card_id = game.current_card
    card_time = CARDS[card_id]["time"]

    game.start_timer()

    await state.set_state(GameStates.running)

    # Текст после нажатия "Старт"
    if card_time is None:
        timer_text = (
            f"🔥 {game.player.name}, ВПЕРЁД!\n\n"
            "⏱ Ограничения по времени нет.\n\n"
            "Когда закончишь — нажми результат."
        )
    else:
        timer_text = TIMER.format(
            player=game.player.name,
            seconds=card_time,
        )

    await c.message.edit_caption(
        caption=timer_text,
        reply_markup=result(),
    )

    await save_game(
        c.message.chat.id,
        game,
    )

    # Запускаем watcher только для карточек
    # с ограничением по времени.
    if card_time is not None:
        asyncio.create_task(
            timeout_watcher(
                c.message,
                c.message.chat.id,
                state,
                card_id,
            )
        )

    await c.answer()


# ============================================================
# РЕЗУЛЬТАТ
# ============================================================

@router.callback_query(
    GameStates.running,
    F.data.startswith("result:")
)
async def result_handler(
    c: CallbackQuery,
    state: FSMContext
):
    game = get_game(c.message.chat.id)

    if not game or game.current_card is None:
        await c.answer("Ход уже завершён.")
        return

    # Запоминаем номер карточки ДО game.success()/game.fail(),
    # потому что после этого current_card очищается.
    card_id = game.current_card

    time_left = game.time_left()

    # ========================================================
    # ВРЕМЯ ВЫШЛО
    # ========================================================

    if time_left is not None and time_left <= 0:
        game.fail()

        text = TIMEOUT.format(
            player=game.player.name
        )

    # ========================================================
    # ИГРОК ВЫПОЛНИЛ ЗАДАНИЕ
    # ========================================================

    elif c.data.endswith("success"):

        game.success()

        # ====================================================
        # 🏆 КАРТА №49 — МГНОВЕННАЯ ПОБЕДА
        # Только в режиме до 50 очков.
        # ====================================================

        if card_id == 49:

            await save_history(
                c.message.chat.id,
                game,
            )

            await delete_saved_game(
                c.message.chat.id
            )

            final_text = (
                "🏆 КАРТА №49!\n\n"
                f"🔥 {game.player.name} выполнил задание!\n\n"
                "👑 МГНОВЕННАЯ ПОБЕДА!\n\n"
                f"{ranking(game.players)}"
            )

            await c.message.edit_caption(
                caption=final_text,
                reply_markup=None,
            )

            await c.answer(
                "🏆 КАРТА №49! МГНОВЕННАЯ ПОБЕДА!",
                show_alert=True,
            )

            return

        text = SUCCESS.format(
            player=game.player.name
        )

    # ========================================================
    # ИГРОК НЕ ВЫПОЛНИЛ ЗАДАНИЕ
    # ========================================================

    else:
        game.fail()

        text = FAIL.format(
            player=game.player.name
        )

    await save_game(
        c.message.chat.id,
        game,
    )

    await state.set_state(
        GameStates.waiting_next
    )

    # ========================================================
    # ОБЫЧНАЯ ПОБЕДА ПО ОЧКАМ
    # ========================================================

    if game.winner():

        await save_history(
            c.message.chat.id,
            game,
        )

        await delete_saved_game(
            c.message.chat.id
        )

        winner = game.winner()

        final_text = RESULTS.format(
            winner=winner.name,
            ranking=ranking(game.players),
        )

        await c.message.edit_caption(
            caption=final_text,
            reply_markup=None,
        )

    # ========================================================
    # ИГРА ПРОДОЛЖАЕТСЯ
    # ========================================================

    else:

        await c.message.edit_caption(
            caption=text,
            reply_markup=next_player(),
        )

    await c.answer()


# ============================================================
# СЛЕДУЮЩИЙ ИГРОК
# ============================================================

@router.callback_query(
    GameStates.waiting_next,
    F.data == "next_player"
)
async def next(
    c: CallbackQuery,
    state: FSMContext
):
    game = get_game(c.message.chat.id)

    if not game:
        await c.answer("Игра не найдена.")
        return

    if game.is_finished():
        await finish_game(c, game)
        return

    game.next_player()

    await save_game(
        c.message.chat.id,
        game,
    )

    await state.set_state(
        GameStates.waiting_open
    )

    await c.message.delete()

    await c.message.answer(
        YOUR_TURN.format(
            player=game.player.name
        ),
        reply_markup=open_card(),
    )

    await c.answer()


# ============================================================
# ЗАВЕРШЕНИЕ ИГРЫ
# ============================================================

async def finish_game(
    c: CallbackQuery,
    game
):
    await save_history(
        c.message.chat.id,
        game,
    )

    await delete_saved_game(
        c.message.chat.id
    )

    winner = game.winner()

    winner_name = (
        winner.name
        if winner
        else "Никто — карточки закончились"
    )

    final_text = RESULTS.format(
        winner=winner_name,
        ranking=ranking(game.players),
    )

    try:
        await c.message.edit_text(
            final_text,
            reply_markup=None,
        )

    except Exception:
        try:
            await c.message.edit_caption(
                caption=final_text,
                reply_markup=None,
            )
        except Exception:
            await c.message.answer(
                final_text
            )

    await c.answer()