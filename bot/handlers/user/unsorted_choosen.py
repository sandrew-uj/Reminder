import datetime
import time

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.user.with_menu import convert_timedelta
from keyboards.inline import choose_remind_kb, choose_unsorted_kb
from keyboards.inline.callbacks import choose_remind_callback, delete_callback, choose_unsorted_callback, \
    delete_unsorted_callback
from loader import dp, bot
from models import User
from models.Remind import Remind
from models.UnsortedDeal import UnsortedDeal
from utils.send_message_with_keyboard import sender


@dp.callback_query_handler(choose_unsorted_callback.filter(temp="1"), state='*')
async def reactor(call: types.CallbackQuery):
    deal_id = int(choose_unsorted_callback.parse(call.data)["deal_id"])
    deal = UnsortedDeal.get_deal(deal_id)
    if not deal:
        return await call.message.answer("Нет дела")

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text="Назначить дело",
                             callback_data=delete_unsorted_callback.new(is_del=2, deal_id=deal_id)))
    keyboard.add(
        InlineKeyboardButton(text="Удалить", callback_data=delete_unsorted_callback.new(is_del=1, deal_id=deal_id)))
    keyboard.add(
        InlineKeyboardButton(text="Назад", callback_data=delete_unsorted_callback.new(is_del=0, deal_id=deal.deal_id)))

    await sender(call=call, message_text=f"Дело: {deal.text}\n" +
                                         convert_timedelta(deal.deal_time),
                 keyboard=keyboard)

    await call.answer()


@dp.callback_query_handler(delete_unsorted_callback.filter(is_del="1"), state='*')
async def deleter(call: types.CallbackQuery):
    await call.answer()
    UnsortedDeal.delete_deal_by_id(int(delete_callback.parse(call.data)["deal_id"]))
    await sender(call=call, message_text="Успешно удалено")


@dp.callback_query_handler(delete_unsorted_callback.filter(is_del="0"), state='*')
async def back(call: types.CallbackQuery):
    user: User = await User.get_user_data(call)
    await sender(call=call, message_text="Ваши дела:", keyboard=choose_unsorted_kb.get_kb(user, 0))
    await call.answer()


@dp.callback_query_handler(choose_unsorted_callback.filter(temp="arrow"), state='*')
async def reactor_arrow(call: types.CallbackQuery):
    user: User = await User.get_user_data(call)

    await sender(call=call, keyboard=choose_unsorted_kb.get_kb(user,
                                                               int(choose_unsorted_callback.parse(call.data)["pos"])))
    await call.answer()
