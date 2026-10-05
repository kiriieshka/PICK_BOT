from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext

from bot.texts.messages import WELCOME
from bot.states.game_states import GameStates
from bot.services.activation_service import is_activated

from config import CARDS_DIR


router = Router()


ACTIVATION_TEXT = """🔐 ДЛЯ ДОСТУПА НУЖЕН КОД

Введите 10-значный код активации:"""


async def send_welcome(message: Message):
    photo = FSInputFile(f"{CARDS_DIR}/instruction.png")

    await message.answer_photo(
        photo=photo,
        caption=WELCOME
    )


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    user_id = message.from_user.id

    # Пользователь уже активирован
    if is_activated(user_id):
        await state.clear()
        await send_welcome(message)
        return

    # Новый пользователь
    await state.set_state(GameStates.activation)

    photo = FSInputFile(f"{CARDS_DIR}/instruction.png")

    await message.answer_photo(
        photo=photo,
        caption=(
            f"{WELCOME}\n\n"
            f"{ACTIVATION_TEXT}"
        )
    )