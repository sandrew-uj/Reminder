from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageCantBeDeleted

import config
from handlers.user.menu import menu_start
from handlers.user.with_menu import get_user_last_calendar_message
from loader import dp, bot
from models import User
# from models.User import get_user_data


@dp.message_handler(commands='start', state='*')
async def start(message: types.Message, state: FSMContext):
    last_calendar_id = get_user_last_calendar_message(message.from_user.id)
    if last_calendar_id:
        try:
            await bot.delete_message(message.chat.id, int(last_calendar_id))
        except (MessageToDeleteNotFound, MessageCantBeDeleted):
            pass
    user: User = await User.get_user_data(message)

    if not user.exists():
        user.add_user()
        mes = await bot.forward_message(chat_id=config.OWNER, from_chat_id=message.from_user.id,
                                        message_id=message.message_id)
        await mes.answer("Добавил в базу")
    # else:
    #     mes = await bot.forward_message(chat_id=config.OWNER, from_chat_id=message.from_user.id,
    #                                       message_id=message.message_id)
    #     await mes.answer("пользователь уже в базе")

    await menu_start(message)
