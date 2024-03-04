import os

from loader import bot
from aiogram import executor
from handlers import dp
from utils.set_bot_commands import set_default_commands


async def on_startup(dp):
    await set_default_commands(dp)

if __name__ == '__main__':
    if not os.path.exists(f"data/"):
        os.mkdir("data/")

    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
