from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def open_card(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🃏 ОТКРЫТЬ КАРТУ", callback_data="open_card")]])
def start_timer(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶️ НАЧАТЬ", callback_data="start_timer")]])
def result(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="😎 КРАСАВЧИК", callback_data="result:success"), InlineKeyboardButton(text="💀 ЛУЗЕР", callback_data="result:fail")]])
def next_player(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="➡️ СЛЕДУЮЩИЙ ИГРОК", callback_data="next_player")]])
def finish(): return InlineKeyboardMarkup(inline_keyboard=[])
