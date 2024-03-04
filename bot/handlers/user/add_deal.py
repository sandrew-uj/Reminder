import json
import shutil

from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from FSM import FSM
from handlers.user.with_menu import on_show_calendar, get_user_data, set_user_data
from keyboards import menu_callback, remind_type_callback, settings_callback, choose_tz_callback, \
    choose_unsorted_callback
from keyboards.inline import choose_tz_kb
from loader import dp, bot
from aiogram import types

from models import User
from models.Deal import Deal
from models.Remind import Remind
import os
from datetime import datetime
import time

from models.UnsortedDeal import UnsortedDeal
from utils.send_message_with_keyboard import sender


async def get_time():
    return int(time.mktime(datetime.now().timetuple()))


@dp.callback_query_handler(choose_unsorted_callback.filter(temp='2'), state='*')
async def add_deal_start(call: types.CallbackQuery):
    # await call.message.answer("Напишите о чем мне напомнить (до 500 символов):")
    await sender(call=call, message_text="Напишите о чем будет дело (до 500 символов):")

    await FSM.text_state_deal.set()
    await call.answer()


@dp.message_handler(state=FSM.text_state_deal)
async def add_deal_text(message: types.Message, state: FSMContext):
    deal_text = message.text

    data = {
        "deal_id": 1,  # Optional[int]
        "user_added_id": message.from_user.id,  # int (replace with the actual user ID)
        "title": "",  # Optional[str]
        "text": deal_text,  # str
        "deal_time": 0,
    }

    user_deal = UnsortedDeal(**data)

    if not os.path.exists(f"data/{message.from_user.id}/"):
        os.mkdir(f"data/{message.from_user.id}/")

    file = open(f"data/{message.from_user.id}/user_deal.json", 'w')
    file.write(json.dumps(user_deal.to_dict()))
    file.close()

    await message.answer("Выберите продолжительность дела:")
    await on_show_calendar(message, deal=2)
    await state.finish()
