import asyncio
import os

import config
from demon import demon
from loader import bot
from aiogram import executor

# from handlers import dp

if __name__ == '__main__':
    # if not os.path.exists(f"data/"):
    #     os.mkdir("data/")
    # executor.start_polling(dp, skip_updates=True)
    asyncio.run(bot.send_message(chat_id=config.OWNER, text="Демон стартанул"))
    asyncio.run(demon())
