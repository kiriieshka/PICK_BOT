
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS

from bot.database.db import (
    get_overall_statistics,
    get_excluded_players,
    exclude_player,
    include_player,
)

from bot.services.statistics import overall_ranking


router = Router()


# ============================================================
# ПРОВЕРКА АДМИНА
# ============================================================

def is_admin(user_id):
    return user_id in ADMIN_IDS


# ============================================================
# АДМИН-ПАНЕЛЬ
# ============================================================

@router.message(Command("admin"))
async def admin_panel(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        await message.answer(
            "⛔ У вас нет доступа."
        )
        return

    await state.clear()

    await message.answer(
        "🛠 АДМИН-ПАНЕЛЬ\n\n"
        "Выберите действие:",
        reply_markup=admin_keyboard(),
    )


# ============================================================
# КЛАВИАТУРА АДМИНА
# ============================================================

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def admin_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(
            text="🏆 Управление рейтингом",
            callback_data="admin:ranking",
        ),
        InlineKeyboardButton(
            text="🚫 Исключённые игроки",
            callback_data="admin:excluded",
        ),
    )

    builder.adjust(1)

    return builder.as_markup()


# ============================================================
# УПРАВЛЕНИЕ РЕЙТИНГОМ
# ============================================================

@router.callback_query(F.data == "admin:ranking")
async def admin_ranking(
    c: CallbackQuery,
):
    if not is_admin(c.from_user.id):
        await c.answer(
            "⛔ Нет доступа.",
            show_alert=True,
        )
        return

    stats = await get_overall_statistics()

    if not stats:
        await c.message.edit_text(
            "🏆 Турнирная таблица пуста.",
            reply_markup=admin_keyboard(),
        )
        await c.answer()
        return

    builder = InlineKeyboardBuilder()

    for item in stats:
        name = item["name"]

        builder.add(
            InlineKeyboardButton(
                text=f"🚫 {name}",
                callback_data=f"admin:exclude:{name}",
            )
        )

    builder.add(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="admin:back",
        )
    )

    builder.adjust(1)

    await c.message.edit_text(
        "🏆 УПРАВЛЕНИЕ ТУРНИРНОЙ ТАБЛИЦЕЙ\n\n"
        "Нажмите на игрока, чтобы исключить его "
        "из общей статистики:",
        reply_markup=builder.as_markup(),
    )

    await c.answer()


# ============================================================
# ИСКЛЮЧИТЬ ИГРОКА
# ============================================================

@router.callback_query(
    F.data.startswith("admin:exclude:")
)
async def admin_exclude(
    c: CallbackQuery,
):
    if not is_admin(c.from_user.id):
        await c.answer(
            "⛔ Нет доступа.",
            show_alert=True,
        )
        return

    name = c.data.split(
        "admin:exclude:",
        1,
    )[1]

    await exclude_player(name)

    await c.answer(
        f"🚫 {name} исключён из рейтинга."
    )

    # Обновляем список
    stats = await get_overall_statistics()

    builder = InlineKeyboardBuilder()

    for item in stats:
        builder.add(
            InlineKeyboardButton(
                text=f"🚫 {item['name']}",
                callback_data=(
                    f"admin:exclude:{item['name']}"
                ),
            )
        )

    builder.add(
        InlineKeyboardButton(
            text="🚫 Исключённые игроки",
            callback_data="admin:excluded",
        )
    )

    builder.add(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="admin:back",
        )
    )

    builder.adjust(1)

    await c.message.edit_text(
        "🏆 УПРАВЛЕНИЕ ТУРНИРНОЙ ТАБЛИЦЕЙ\n\n"
        "Игрок исключён.\n\n"
        "Выберите следующего игрока:",
        reply_markup=builder.as_markup(),
    )


# ============================================================
# СПИСОК ИСКЛЮЧЁННЫХ
# ============================================================

@router.callback_query(
    F.data == "admin:excluded"
)
async def admin_excluded(
    c: CallbackQuery,
):
    if not is_admin(c.from_user.id):
        await c.answer(
            "⛔ Нет доступа.",
            show_alert=True,
        )
        return

    excluded = await get_excluded_players()

    if not excluded:
        text = (
            "🚫 ИСКЛЮЧЁННЫЕ ИГРОКИ\n\n"
            "Список пуст."
        )

        builder = InlineKeyboardBuilder()

    else:
        text = (
            "🚫 ИСКЛЮЧЁННЫЕ ИГРОКИ\n\n"
            "Нажмите на игрока, чтобы вернуть "
            "его в турнирную таблицу:"
        )

        builder = InlineKeyboardBuilder()

        for item in excluded:
            builder.add(
                InlineKeyboardButton(
                    text=f"↩️ {item['name']}",
                    callback_data=(
                        f"admin:include:"
                        f"{item['name']}"
                    ),
                )
            )

    builder.add(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="admin:back",
        )
    )

    builder.adjust(1)

    await c.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
    )

    await c.answer()


# ============================================================
# ВЕРНУТЬ В РЕЙТИНГ
# ============================================================

@router.callback_query(
    F.data.startswith("admin:include:")
)
async def admin_include(
    c: CallbackQuery,
):
    if not is_admin(c.from_user.id):
        await c.answer(
            "⛔ Нет доступа.",
            show_alert=True,
        )
        return

    name = c.data.split(
        "admin:include:",
        1,
    )[1]

    await include_player(name)

    await c.answer(
        f"↩️ {name} возвращён в рейтинг."
    )

    await admin_excluded(c)


# ============================================================
# НАЗАД
# ============================================================

@router.callback_query(
    F.data == "admin:back"
)
async def admin_back(
    c: CallbackQuery,
):
    if not is_admin(c.from_user.id):
        await c.answer(
            "⛔ Нет доступа.",
            show_alert=True,
        )
        return

    await c.message.edit_text(
        "🛠 АДМИН-ПАНЕЛЬ\n\n"
        "Выберите действие:",
        reply_markup=admin_keyboard(),
    )

    await c.answer()