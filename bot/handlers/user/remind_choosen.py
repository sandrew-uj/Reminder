import datetime
import time

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline import choose_remind_kb
from keyboards.inline.callbacks import choose_remind_callback, delete_callback
from loader import dp, bot
from models import User
from models.Remind import Remind
from utils.send_message_with_keyboard import sender


# from models.User import get_user_data


@dp.callback_query_handler(choose_remind_callback.filter(temp="1"), state='*')
async def reactor(call: types.CallbackQuery):
    remind_id = int(choose_remind_callback.parse(call.data)["remind_id"])
    remind = Remind.get_remind(int(choose_remind_callback.parse(call.data)["remind_id"]))
    if not remind:
        return await call.message.answer("Нет напоминания")

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Удалить", callback_data=delete_callback.new(is_del=1, remind_id=remind_id)))
    keyboard.add(
        InlineKeyboardButton(text="Назад", callback_data=delete_callback.new(is_del=0, remind_id=remind.remind_type)))

    remind_datetime = datetime.datetime.fromtimestamp(remind.date)
    remind_type: str = "не знаю"
    if remind.remind_type == "single":
        remind_type = "единоразовое"
    elif remind.remind_type == "yearly":
        remind_type = "ежегодное"
    elif remind.remind_type == "monthly":
        remind_type = "ежемесячное"
    elif remind.remind_type == "daily":
        remind_type = "ежедневное"
    elif remind.remind_type == "weekly":
        remind_type = "еженедельное"
    # await call.message.edit_text(f"Напоминание: {remind.text}\n"
    #                              f"Когда: {time.strftime('%Y.%m.%d в %H:%M', remind_datetime.timetuple())} \n"
    #                              f"Тип: {remind_type}", reply_markup=keyboard)

    await sender(call=call, message_text=f"Напоминание: {remind.text}\n"
                                         f"Когда: {time.strftime('%Y.%m.%d в %H:%M', remind_datetime.timetuple())} \n"
                                         f"Тип: {remind_type}", keyboard=keyboard)

    await call.answer()


@dp.callback_query_handler(delete_callback.filter(is_del="1"), state='*')
async def deleter(call: types.CallbackQuery):
    await call.answer()
    Remind.delete_remind_by_id(int(delete_callback.parse(call.data)["remind_id"]))
    # await call.message.edit_text("Успешно удалено")
    await sender(call=call, message_text="Успешно удалено")


@dp.callback_query_handler(delete_callback.filter(is_del="0"), state='*')
async def back(call: types.CallbackQuery):
    user: User = await User.get_user_data(call)
    await sender(call=call, message_text="Ваши напоминания:", keyboard=choose_remind_kb.get_kb(user,
                                                                                               delete_callback.parse(
                                                                                                   call.data)[
                                                                                                   "remind_id"],
                                                                                               0))
    await call.answer()


@dp.callback_query_handler(choose_remind_callback.filter(temp="arrow"), state='*')
async def reactor_arrow(call: types.CallbackQuery):
    user: User = await User.get_user_data(call)

    await sender(call=call, keyboard=choose_remind_kb.get_kb(user,
                                                             choose_remind_callback.parse(call.data)["remind_id"],
                                                             int(choose_remind_callback.parse(call.data)["pos"])))
    await call.answer()
