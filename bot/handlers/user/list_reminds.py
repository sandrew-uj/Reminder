import config
from handlers.user.menu import menu_start
from keyboards import menu_callback, choose_type_callback, choose_remind_callback
from loader import dp, bot
from aiogram import types
from models import User
from models.Remind import Remind
from keyboards.inline import choose_remind_kb, menu_kb
from utils.send_message_with_keyboard import sender


@dp.callback_query_handler(menu_callback.filter(cbtype='0'), state='*')
async def reactor(call: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()

    for (remind_type, remind_type_ru) in zip(config.remind_types, config.remind_types_ru):
        keyboard.add(types.InlineKeyboardButton(text=remind_type_ru,
                                                callback_data=choose_type_callback.new(choose="yes",
                                                                                       remind_type=remind_type)))

    keyboard.add(types.InlineKeyboardButton(text="назад",
                                            callback_data=choose_type_callback.new(choose="no",
                                                                                   remind_type=0)))

    await sender(call=call, message_text="Выберите тип напоминания:", keyboard=keyboard)


@dp.callback_query_handler(choose_type_callback.filter(choose='yes'), state='*')
async def reactor_type(call: types.CallbackQuery):
    user: User = await User.get_user_data(call)
    remind_type = choose_type_callback.parse(call.data)["remind_type"]

    reminds = user.find_reminds_by_type(remind_type=remind_type)
    if reminds is None or len(reminds) == 0:
        return await call.answer(text=f"У вас нет напоминаний типа {remind_type}", show_alert=True)

    await sender(call=call, message_text="Ваши напоминания:", keyboard=choose_remind_kb.get_kb(user, remind_type, 0))

    await call.answer()


@dp.callback_query_handler(choose_type_callback.filter(choose='no'), state='*')
async def reactor_back(call: types.CallbackQuery):
    await sender(call=call, message_text="Добро пожаловать в меню", keyboard=menu_kb.get_kb())


@dp.callback_query_handler(choose_remind_callback.filter(temp="back"), state='*')
async def back(call: types.CallbackQuery):
    await reactor(call)
