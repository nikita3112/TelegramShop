from aiogram import executor
from dispatcher import dp
from SQL import SQLite
import handlers

db = SQLite('bd.db')

if __name__ == "__main__":
    executor.start_polling(dp)