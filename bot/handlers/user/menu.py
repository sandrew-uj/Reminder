from aiogram.types import WebAppInfo

from keyboards import menu_callback
from keyboards.inline import menu_kb
from loader import dp, bot
from aiogram import types
from models import User
# from models.User import get_user_data
import config


@dp.message_handler(commands='menu', state='*')
async def menu_start(message: types.Message):
    user: User = await User.get_user_data(message)

    if not user.exists():
        user.add_user()

    await message.answer(text="Добро пожаловать в меню", reply_markup=menu_kb.get_kb())
