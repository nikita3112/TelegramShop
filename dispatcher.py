from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config
import logging

file_log = logging.FileHandler(filename='logs.log')
file_log.setLevel(logging.INFO)

console_out = logging.StreamHandler()
console_out.setLevel(logging.INFO)

logging.basicConfig(handlers=(console_out, file_log, ), format='[%(asctime)s | %(levelname)s]: %(message)s', datefmt='%d.%m.%Y %H:%M:%S', level=logging.INFO)

if not config.BOT_TOKEN:
    exit('Нет токена!')


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())