from aiogram import types
from keyboards.inline.callbacks import choose_remind_callback
from models import User
import config


def get_kb(user: User, remind_type: str, pos: int):
    reminds = user.find_reminds_by_type(remind_type)

    keyboard = types.InlineKeyboardMarkup()

    for i in range(pos, pos + 5):
        if i >= len(reminds):
            break
        remind = reminds[i]

        title = remind.text[0:40]

        button = types.InlineKeyboardButton(text=title,
                                            callback_data=choose_remind_callback.new(remind_id=remind.remind_id,
                                                                                     pos=0,
                                                                                     temp=1))
        # button = types.InlineKeyboardButton(text=title, url=f"{config.FRONTEND_URL}/"
        #                                     )

        keyboard.add(button)

    bottom_buttons = []
    if pos > 0:
        bottom_buttons.append(types.InlineKeyboardButton(text='<',
                                                         callback_data=choose_remind_callback.new(
                                                             remind_id=remind_type,
                                                             pos=pos - 5,
                                                             temp="arrow")))

    bottom_buttons.append(types.InlineKeyboardButton(text='назад',
                                                     callback_data=choose_remind_callback.new(
                                                         remind_id=0,
                                                         pos=0,
                                                         temp="back")))

    if pos + 5 < len(reminds):
        bottom_buttons.append(types.InlineKeyboardButton(text='>',
                                                         callback_data=choose_remind_callback.new(
                                                             remind_id=remind_type,
                                                             pos=pos + 5,
                                                             temp="arrow")))

    keyboard.add(*bottom_buttons)

    return keyboard
