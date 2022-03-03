from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData


# Text buttons
products = KeyboardButton("📦 Товары")
payments = KeyboardButton("💰 Мои покупки")
cancel = KeyboardButton("👈 Назад")
add = KeyboardButton("✏️ Добавить")
delete = KeyboardButton("❌ Удалить")
edit = KeyboardButton("✂️ Редактироать")

# Inline buttons
edit_name = InlineKeyboardButton("Название", callback_data="edit_name")
edit_description = InlineKeyboardButton("Описание", callback_data="edit_description")
edit_price = InlineKeyboardButton("Цену", callback_data="edit_price")
edit_file = InlineKeyboardButton("Файл проекта", callback_data="edit_file")
buy = InlineKeyboardButton("Купить", callback_data="buy_project")

start_markup = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True)
admins_markup = ReplyKeyboardMarkup(resize_keyboard=True)
projects_markup = ReplyKeyboardMarkup(resize_keyboard=True)
remove = ReplyKeyboardRemove()

edit_project_markup = InlineKeyboardMarkup()
buy_markup = InlineKeyboardMarkup()

start_markup.add(products, payments)
cancel_markup.add(cancel)
admins_markup.row(add, delete)
admins_markup.row(cancel)
projects_markup.row(add, edit, delete)
projects_markup.row(cancel)

edit_project_markup.row(edit_name)
edit_project_markup.row(edit_description)
edit_project_markup.row(edit_price)
edit_project_markup.row(edit_file)

buy_markup.row(buy)