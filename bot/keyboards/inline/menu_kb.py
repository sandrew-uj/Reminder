from aiogram import types
from keyboards.inline.callbacks import menu_callback
from models import User


def get_kb():
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="создать напоминание",
                                         callback_data=menu_callback.new(cbtype='1'))
    button2 = types.InlineKeyboardButton(text="список напоминаний",
                                         callback_data=menu_callback.new(cbtype='0'))
    button3 = types.InlineKeyboardButton(text="настройки",
                                         callback_data=menu_callback.new(cbtype='2'))
    button4 = types.InlineKeyboardButton(text="назначить дело",
                                         callback_data=menu_callback.new(cbtype='3'))
    button5 = types.InlineKeyboardButton(text="расписание на сегодня",
                                         callback_data=menu_callback.new(cbtype='4'))
    # button5 = types.InlineKeyboardButton(text="список дел",
    #                                      callback_data=menu_callback.new(cbtype='4'))


    keyboard.add(button1)
    keyboard.add(button4)
    keyboard.add(button2)
    keyboard.add(button5)
    keyboard.add(button3)

    return keyboard
