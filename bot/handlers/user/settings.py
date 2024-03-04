from aiogram import types
from aiogram.dispatcher import FSMContext

from FSM import FSM
from keyboards import menu_callback, settings_callback, choose_tz_callback
from keyboards.inline import choose_tz_kb
from loader import bot, dp
from models import User


@dp.callback_query_handler(menu_callback.filter(cbtype='2'), state='*')
async def reactor(call: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="настроить часовой пояс",
                                         callback_data=settings_callback.new(cbtype='1'))
    keyboard.add(button1)
    await call.message.edit_text(text="Настройки", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(settings_callback.filter(cbtype='1'), state='*')
async def reactor_timezone(call: types.CallbackQuery):
    await call.message.edit_text(text="Выберите пояс:", reply_markup=choose_tz_kb.get_kb())
    await FSM.settings_timezone.set()
    await call.answer()


@dp.callback_query_handler(choose_tz_callback.filter(temp="arrow"), state='*')
async def reactor_arrow(call: types.CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=choose_tz_kb.get_kb(
        int(choose_tz_callback.parse(call.data)["tz"])))
    await call.answer()


@dp.callback_query_handler(choose_tz_callback.filter(temp="1"), state=FSM.settings_timezone)
async def reactor_tz(call: types.CallbackQuery, state: FSMContext):
    tz = int(choose_tz_callback.parse(call.data)["tz"])
    user: User = await User.get_user_data(call)

    user.update_tz(tz)
    await call.message.edit_text("Часовой пояс успешно обновлен!")
    await call.answer()
    await state.finish()


