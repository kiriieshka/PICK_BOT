from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.states.game_states import GameStates
from bot.services.activation_service import activate_code


router = Router()


ACTIVATION_REQUEST = """🔐 ДЛЯ ДОСТУПА НУЖНА АКТИВАЦИЯ

Введите 10-значный код активации:"""


ACTIVATION_SUCCESS = """✅ АКТИВАЦИЯ УСПЕШНА!

Доступ к BASKETBALL CHALLENGE открыт 🏀

Теперь вы можете пользоваться ботом без повторного ввода кода."""


ACTIVATION_INVALID = """❌ НЕВЕРНЫЙ КОД

Проверьте код и попробуйте ещё раз."""


ACTIVATION_USED = """⚠️ ЭТОТ КОД УЖЕ ИСПОЛЬЗОВАН

Введите другой код активации."""


@router.message(GameStates.activation)
async def activation_code_handler(
    message: Message,
    state: FSMContext,
):
    code = (message.text or "").strip()

    # Код должен состоять ровно из 10 цифр.
    if len(code) != 10 or not code.isdigit():
        await message.answer(
            "❌ Код должен состоять ровно из 10 цифр.\n\n"
            "Попробуйте ещё раз:"
        )
        return

    result = activate_code(
        user_id=message.from_user.id,
        code=code,
    )

    if result == "activated":
        await state.clear()

        await message.answer(
            ACTIVATION_SUCCESS
        )

        # После активации запускаем обычное приветствие.
        from bot.handlers.start import send_welcome

        await send_welcome(message)
        return

    if result == "already_activated":
        await state.clear()

        from bot.handlers.start import send_welcome

        await send_welcome(message)
        return

    if result == "used":
        await message.answer(ACTIVATION_USED)
        return

    await message.answer(ACTIVATION_INVALID)