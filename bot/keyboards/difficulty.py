from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def game_modes():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🏀 ИГРА ДО 5 ОЧКОВ", callback_data="mode:5", style = "success"),
        InlineKeyboardButton(text="🔥 ИГРА ДО 15 ОЧКОВ", callback_data="mode:15", style = "primary"),
        InlineKeyboardButton(text="🏆 ИГРА НА ВСЮ КОЛОДУ", callback_data="mode:50", style = "danger"),
    )
    builder.adjust(1)
    return builder.as_markup()

def player_count():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=str(i), callback_data=f"players:{i}") for i in (1,2,3)],
        [InlineKeyboardButton(text=str(i), callback_data=f"players:{i}") for i in (4,5)],
    ])
