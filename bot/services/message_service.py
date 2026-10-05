async def delete_last_menu_message(message, state):
    data = await state.get_data()
    message_id = data.get("last_menu_message_id")

    if not message_id:
        return

    try:
        await message.bot.delete_message(
            chat_id=message.chat.id,
            message_id=message_id,
        )
    except Exception:
        pass

    await state.update_data(
        last_menu_message_id=None
    )


async def save_menu_message(message, state):
    await state.update_data(
        last_menu_message_id=message.message_id
    )