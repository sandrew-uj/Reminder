from typing import Union

from aiogram import types


async def sender(call: types.CallbackQuery, message_text: Union[str, None] = None,
                 keyboard: Union[types.InlineKeyboardMarkup, None] = None):
    try:
        if message_text:
            await call.message.edit_text(message_text, reply_markup=keyboard, parse_mode="Markdown")
        else:
            await call.message.edit_reply_markup(reply_markup=keyboard)
    except Exception as e1:
        print(e1)
        try:
            await call.message.edit_reply_markup(reply_markup=keyboard)
        except Exception as e2:
            print(e2)
            pass
        if not message_text:
            message_text = call.message.text
        await call.message.answer(message_text, reply_markup=keyboard, parse_mode="Markdown")
        await call.message.delete()
