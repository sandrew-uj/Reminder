from aiogram import types
from keyboards.inline.callbacks import choose_remind_callback, choose_unsorted_callback
from models import User
import config


def get_kb(user: User, pos: int):
    unsorted = user.find_unsorted()

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Добавить дело",
                                            callback_data=choose_unsorted_callback.new(deal_id=0,
                                                                                       pos=pos,
                                                                                       temp=2)))

    for i in range(pos, pos + 5):
        if i >= len(unsorted):
            break
        deal = unsorted[i]

        title = deal.text[0:40]

        button = types.InlineKeyboardButton(text=title,
                                            callback_data=choose_unsorted_callback.new(deal_id=deal.deal_id,
                                                                                       pos=0,
                                                                                       temp=1))

        keyboard.add(button)

    bottom_buttons = []
    if pos > 0:
        bottom_buttons.append(types.InlineKeyboardButton(text='<',
                                                         callback_data=choose_unsorted_callback.new(
                                                             deal_id=0,
                                                             pos=pos - 5,
                                                             temp="arrow")))

    bottom_buttons.append(types.InlineKeyboardButton(text='назад',
                                                     callback_data=choose_unsorted_callback.new(
                                                         deal_id=0,
                                                         pos=0,
                                                         temp="back")))

    if pos + 5 < len(unsorted):
        bottom_buttons.append(types.InlineKeyboardButton(text='>',
                                                         callback_data=choose_unsorted_callback.new(
                                                             deal_id=0,
                                                             pos=pos + 5,
                                                             temp="arrow")))

    keyboard.add(*bottom_buttons)

    return keyboard
