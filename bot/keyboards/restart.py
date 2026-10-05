from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def confirm():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ ДА, РЕСТАРТ", callback_data="restart_yes"),
            InlineKeyboardButton(text="❌ НЕТ", callback_data="restart_no"),
        ]
    ])
