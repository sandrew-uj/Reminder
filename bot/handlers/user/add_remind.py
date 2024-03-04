import json
import shutil

from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from FSM import FSM
from handlers.user.with_menu import on_show_calendar, get_user_data, set_user_data
from keyboards import menu_callback, remind_type_callback, settings_callback, choose_tz_callback
from keyboards.inline import choose_tz_kb
from loader import dp, bot
from aiogram import types

from models import User
from models.Remind import Remind
import os
from datetime import datetime
import time

from utils.send_message_with_keyboard import sender


async def get_time():
    return int(time.mktime(datetime.now().timetuple()))


@dp.callback_query_handler(menu_callback.filter(cbtype='1'), state='*')
async def add_remind_start(call: types.CallbackQuery):
    # await call.message.answer("Напишите о чем мне напомнить (до 500 символов):")
    await sender(call=call, message_text="Напишите о чем мне напомнить (до 500 символов):")

    await FSM.text_state.set()
    await call.answer()


@dp.message_handler(state=FSM.text_state)
async def add_remind_text(message: types.Message, state: FSMContext):
    remind_text = message.text

    data = {
        "remind_id": 1,
        "user_added_id": message.from_user.id,
        "title": "",
        "text": "",
        "date": -1,
        "remind_type": "",
        "remind_time": -1
    }
    user_remind = Remind(**data)
    user_remind.user_added_id = message.from_user.id
    user_remind.title = ""
    user_remind.text = remind_text
    user_remind.date = -1
    user_remind.remind_type = ""
    user_remind.remind_time = -1

    if not os.path.exists(f"data/{message.from_user.id}/"):
        os.mkdir(f"data/{message.from_user.id}/")

    file = open(f"data/{message.from_user.id}/user_remind.json", 'w')
    file.write(json.dumps(user_remind.to_dict()))
    file.close()

    # keyboard = types.InlineKeyboardMarkup()
    # user: User = await User.get_user_data(message)
    # tz: int = user.get_tz()
    # tz_str = f"UTC{tz}" if tz < 0 else f"UTC+{tz}"
    # keyboard.add(types.InlineKeyboardButton(text=f"Оставить текущий ({tz_str})",
    #                                         callback_data=settings_callback.new(cbtype='10')))
    # keyboard.add(
    #     types.InlineKeyboardButton(text=f"Выбрать часовой пояс", callback_data=settings_callback.new(cbtype='11')))
    #
    # await message.answer("Укажите часовой пояс", reply_markup=keyboard)

    await message.answer("Когда установить напоминание?")
    await on_show_calendar(message)
    await state.finish()


# @dp.callback_query_handler(settings_callback.filter(cbtype="10"), state='*')
# async def reactor_stay(call: types.CallbackQuery):
#     user: User = await User.get_user_data(call)
#     tz = user.get_tz()
#
#     user_id: int = call.from_user.id
#     user_data = get_user_data(user_id)
#     user_data["tz"] = tz
#     set_user_data(user_id, user_data)
#
#     await call.message.answer("Когда установить напоминание?")
#     await on_show_calendar(call)


# @dp.callback_query_handler(settings_callback.filter(cbtype="11"), state='*')
# async def reactor_change(call: types.CallbackQuery):
#     await call.message.edit_text(text="Выберите пояс:", reply_markup=choose_tz_kb.get_kb())
#     await FSM.add_remind_timezone.set()
#     await call.answer()


# @dp.callback_query_handler(choose_tz_callback.filter(temp="1"), state=FSM.add_remind_timezone)
# async def reactor_tz(call: types.CallbackQuery, state: FSMContext):
#     tz = int(choose_tz_callback.parse(call.data)["tz"])
#     user: User = await User.get_user_data(call)
#
#     user_id: int = call.from_user.id
#     user_data = get_user_data(user_id)
#     user_data["tz"] = tz
#     set_user_data(user_id, user_data)
#
#     await call.message.edit_text("Часовой пояс успешно установлен! \nКогда установить напоминание?")
#     await call.answer()
#     await state.finish()
#     await on_show_calendar(call)
