from aiogram.fsm.state import State, StatesGroup


class GameStates(StatesGroup):
    activation = State()

    choosing_difficulty = State()
    choosing_players = State()
    entering_name = State()
    waiting_open = State()
    waiting_start = State()
    running = State()
    waiting_next = State()