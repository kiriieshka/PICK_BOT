from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎮 НОВАЯ ИГРА"), KeyboardButton(text="📊 СТАТИСТИКА")],
            [KeyboardButton(text="🏆 ОБЩАЯ СТАТИСТИКА"), KeyboardButton(text="🔄 РЕСТАРТ")],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Выберите действие…",
    )
