from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config
from aiogram import Bot, Dispatcher

bot = Bot(token=config.TOKEN)

dp = Dispatcher(bot, storage=MemoryStorage())

