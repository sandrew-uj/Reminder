from FSM import FSM
from keyboards import menu_callback, choose_remind_callback, choose_unsorted_callback
from loader import dp, bot
from aiogram import types
from models import User
from keyboards.inline import menu_kb, choose_unsorted_kb
from utils.send_message_with_keyboard import sender


@dp.callback_query_handler(menu_callback.filter(cbtype='3'), state='*')
async def reactor(call: types.CallbackQuery):
    user: User = await User.get_user_data(call)

    unsorted = user.find_unsorted()
    # if unsorted is None or len(unsorted) == 0:
    #     return await call.answer(text=f"У вас нет несор типа {remind_type}", show_alert=True)

    await sender(call=call, message_text="Какое дело?", keyboard=choose_unsorted_kb.get_kb(user, 0))
    await call.answer()

@dp.callback_query_handler(choose_unsorted_callback.filter(temp="back"), state='*')
async def back(call: types.CallbackQuery):
    await sender(call=call, message_text="Добро пожаловать в меню", keyboard=menu_kb.get_kb())


@dp.callback_query_handler(choose_unsorted_callback.filter(temp="arrow"), state='*')
async def reactor_arrow(call: types.CallbackQuery):
    user: User = await User.get_user_data(call)

    await sender(call=call, keyboard=choose_unsorted_kb.get_kb(user,
                                                               int(choose_remind_callback.parse(call.data)["pos"])))
    await call.answer()
