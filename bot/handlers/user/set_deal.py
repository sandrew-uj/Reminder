from aiogram import types

from handlers.user.with_menu import on_show_calendar
from keyboards import delete_unsorted_callback, delete_callback
from loader import dp
from models.UnsortedDeal import UnsortedDeal
from utils.send_message_with_keyboard import sender
import os
import json


@dp.callback_query_handler(delete_unsorted_callback.filter(is_del="2"), state='*')
async def deal_set(call: types.CallbackQuery):
    await call.answer()
    # UnsortedDeal.delete_deal_by_id(int(delete_callback.parse(call.data)["deal_id"]))
    deal = UnsortedDeal.get_deal(int(delete_unsorted_callback.parse(call.data)["deal_id"]))

    if not os.path.exists(f"data/{call.from_user.id}/"):
        os.mkdir(f"data/{call.from_user.id}/")

    file = open(f"data/{call.from_user.id}/user_deal.json", 'w')
    file.write(json.dumps(deal.to_dict()))
    file.close()

    await sender(call=call, message_text="Укажите куда поставить дело:")
    await on_show_calendar(call.message, deal=1, call=call)
