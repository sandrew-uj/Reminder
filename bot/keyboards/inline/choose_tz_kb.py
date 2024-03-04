from aiogram import types
from keyboards.inline.callbacks import choose_tz_callback
from utils.get_timezone_title import get_title_by_tz


def get_kb(pos: int = 0):
    timezones = [i for i in range(2, 13)]
    keyboard = types.InlineKeyboardMarkup()

    for i in range(pos, pos + 5):
        if i >= len(timezones):
            break
        tz = timezones[i]

        title = get_title_by_tz(tz)

        button = types.InlineKeyboardButton(text=title,
                                            callback_data=choose_tz_callback.new(
                                                tz=tz,
                                                temp=1))

        keyboard.add(button)

    bottom_buttons = []
    if pos > 0:
        bottom_buttons.append(types.InlineKeyboardButton(text='<',
                                                         callback_data=choose_tz_callback.new(
                                                             tz=pos - 5,
                                                             temp="arrow")))

    if pos + 5 < len(timezones):
        bottom_buttons.append(types.InlineKeyboardButton(text='>',
                                                         callback_data=choose_tz_callback.new(
                                                             tz=pos + 5,
                                                             temp="arrow")))

    keyboard.add(*bottom_buttons)

    return keyboard
