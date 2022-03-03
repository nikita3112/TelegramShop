import logging
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from dispatcher import dp
from bot import db
from keyboards import start_markup, remove, cancel_markup, admins_markup, projects_markup, edit_project_markup, buy_markup
from states import AddProjectStates, AdminState, DeleteAdminState, EditProjectState, Project, SoldProjects
from texts import *
import os
from qiwi import p2p
from uuid import uuid4


# Commands

@dp.message_handler(commands='start')
async def start(message: types.Message):
    logging.info(f"User - {message.from_user.username} | /start")
    if not db.user_exists(message.from_user.id):
        db.add_new_user(message.from_user.id, message.from_user.username)
    await message.bot.send_message(message.from_user.id, start_msg, reply_markup=start_markup)

@dp.message_handler(commands="products")
async def projects(message: types.Message, state: FSMContext):
    logging.info(f"User - {message.from_user.username} | /products")
    if db.is_admin(message.from_user.id):
        projects = db.get_all_projects()
        if projects:
            await state.update_data(projects=projects)
            text = "📌 Список загруженных проектов:\n"
            for i in range(len(projects)):
                text += f'{i + 1}. {projects[i][1]}\n'
            await AdminState.projects.set()
            await message.bot.send_message(message.from_user.id, text, reply_markup=projects_markup)
        else:
            await AdminState.projects.set()
            await message.bot.send_message(message.from_user.id, no_projects, reply_markup=projects_markup)
    else:
        await message.bot.send_message(message.from_user.id, not_admin_msg, reply_markup=start_markup)

@dp.message_handler(commands='admins')
async def admins(message: types.Message, state: FSMContext):
    logging.info(f"User - {message.from_user.username} | /admins")
    if db.is_admin(message.from_user.id):
        admins = db.get_admins()
        await state.update_data(admins=admins)
        text = "👤 Список админов:\n"
        for i in range(len(admins)):
            admin_name = db.user_info(admins[i][0])[2]
            text += f'{i + 1}. {admin_name}\n'
        await AdminState.admin.set()
        await message.bot.send_message(message.from_user.id, text, reply_markup=admins_markup)
    else:
        await message.bot.send_message(message.from_user.id, not_admin_msg, reply_markup=start_markup)

@dp.message_handler(commands='stats')
async def stats(message: types.Message):
    if db.is_admin(message.from_user.id):
        users = db.get_all_users()
        text = ''
        for i in users:
            text += f'{i}\n'
        await message.bot.send_message(message.from_user.id, text)


# Messages

@dp.message_handler(text="👈 Назад", state='*')
async def cancel(message: types.Message, state: FSMContext):
    logging.info(f"User - {message.from_user.username} | Назад")
    await state.finish()
    await message.bot.send_message(message.from_user.id, start_msg, reply_markup=start_markup)

# States project

@dp.message_handler(text="💰 Мои покупки")
async def payments(message: types.Message, state: FSMContext):
    logging.info(f"User - {message.from_user.username} | Мои покупки")
    projects = db.get_user_accesses(message.from_user.id)
    if projects:
        await state.update_data(p_ids=projects)
        text = '📌 Ваши покупки:\n'
        for i in range(len(projects)):
            project_info = db.get_project_info(projects[i][0])
            text += f'      {i + 1}. {project_info[1]}\n'
        text += '\nДля получения товара введите номер'
        await SoldProjects.sold_project.set()
        await message.bot.send_message(message.from_user.id, text, reply_markup=cancel_markup)
    else:
        await message.bot.send_message(message.from_user.id, no_payments, reply_markup=cancel_markup)

@dp.message_handler(state=SoldProjects.sold_project)
async def get_project(message: types.Message, state: FSMContext):
    logging.info(f"User - {message.from_user.username} | Получить проект")
    text = message.text
    try:
        text = int(text)
    except ValueError:
        await message.bot.send_message(message.from_user.id, invalid_value)
    
    projects = await state.get_data()
    ids = projects['p_ids']
    project = ids[text - 1][0]
    project_info = db.get_project_info(project)
    text = f'Информация о проекте:\nНазвание: {project_info[1]}\nОписание:\n{project_info[2]}'
    file = types.InputFile(project_info[4])
    await state.finish()
    await message.bot.send_message(message.from_user.id, text, reply_markup=cancel_markup)
    await message.bot.send_document(message.from_user.id, file)


@dp.message_handler(text="📦 Товары")
async def products(message: types.Message, state: FSMContext):
    logging.info(f"User - {message.from_user.username} | Товары")
    projects = db.get_all_projects()
    await state.update_data(projects=projects)
    if projects:
        text = '📌 Магазин программ:\n'
        for i in range(len(projects)):
            text += f'      {i + 1}. {projects[i][1]}\n'
        text += '\nДля просмотра информации или покупки введите номер:'
        await Project.project_choise.set()
        await message.bot.send_message(message.from_user.id, text, reply_markup=cancel_markup)
    else:
        await message.bot.send_message(message.from_user.id, no_projects, reply_markup=cancel_markup)

@dp.message_handler(state=Project.project_choise)
async def project_choise(message: types.Message, state: FSMContext):
    text = message.text
    try:
        text = int(text)
    except ValueError:
        await message.bot.send_message(message.from_user.id, invalid_value)
    
    projects = await state.get_data()
    project = projects['projects'][text - 1]
    await state.reset_data()
    await state.update_data(project=project)
    text = f'Информация о проекте:\nНазвание: {project[1]}\nОписание:\n{project[2]}\nЦена: {project[3]} руб.'
    await Project.project_view.set()
    await message.bot.send_message(message.from_user.id, text, reply_markup=buy_markup)


@dp.message_handler(text="✏️ Добавить", state=AdminState.projects)
async def add_project(message: types.Message):
    logging.info(f"User - {message.from_user.username} | Добавить")
    if db.is_admin(message.from_user.id):
        await AddProjectStates.project_name.set()
        await message.bot.send_message(message.from_user.id, project_name, reply_markup=cancel_markup)
    else:
        await message.bot.send_message(message.from_user.id, not_admin_msg, reply_markup=start_markup)

@dp.message_handler(state=AddProjectStates.project_name)
async def set_project_name(message: types.Message, state: FSMContext):
    await state.update_data(project_name=message.text)
    await AddProjectStates.next()
    await message.bot.send_message(message.from_user.id, project_description, reply_markup=cancel_markup)

@dp.message_handler(state=AddProjectStates.project_description)
async def set_project_description(message: types.Message, state: FSMContext):
    await state.update_data(project_description=message.text)
    await AddProjectStates.next()
    await message.bot.send_message(message.from_user.id, project_price, reply_markup=cancel_markup)

@dp.message_handler(state=AddProjectStates.project_price)
async def set_project_price(message: types.Message, state: FSMContext):
    await state.update_data(project_price=message.text)
    await AddProjectStates.next()
    await message.bot.send_message(message.from_user.id, project_file, reply_markup=cancel_markup)
    
@dp.message_handler(state=AddProjectStates.project_file, content_types=['document'])
async def set_project_file(message: types.Message, state: FSMContext):
    file_path = f'projects/{message.document.file_name}'
    await message.bot.download_file_by_id(message.document.file_id, file_path)
    await state.update_data(path=file_path)
    project_data = await state.get_data()
    db.add_new_project(project_data["project_name"], project_data["project_description"], project_data["project_price"], project_data["path"])
    logging.info(f"User - {message.from_user.username} | {message.from_user.username} добавил проект {project_data['project_name']}")
    await state.finish()
    await message.bot.send_message(message.from_user.id, project_success, reply_markup=start_markup)

@dp.message_handler(text="❌ Удалить", state=AdminState.projects)
async def delete_project_call(message: types.Message, state: FSMContext):
    logging.info(f"User - {message.from_user.username} | Удалить")
    projects = await state.get_data()
    if projects:
        await DeleteAdminState.delete_project.set()
        await message.bot.send_message(message.from_user.id, delete_project_text, reply_markup=cancel_markup)
    else:
        await message.bot.send_message(message.from_user.id, no_projects, reply_markup=projects_markup)

@dp.message_handler(state=DeleteAdminState.delete_project)
async def delete_project(message: types.Message, state: FSMContext):
    p_id = int(message.text)
    projects = await state.get_data()
    project = projects['projects'][p_id - 1]
    db.delete_project(project[0])
    os.remove(project[4])
    await state.finish()
    await message.bot.send_message(message.from_user.id, delete_project_success_text, reply_markup=start_markup)

@dp.message_handler(text="✂️ Редактироать", state=AdminState.projects)
async def edit_project_call(message: types.Message, state: FSMContext):
    logging.info(f"User - {message.from_user.username} | Редактировать")
    projects = await state.get_data()
    if projects:
        await EditProjectState.edit_project.set()
        await message.bot.send_message(message.from_user.id, edit_project_text, reply_markup=cancel_markup)
    else:
        await message.bot.send_message(message.from_user.id, no_projects, reply_markup=projects_markup)

@dp.message_handler(state=EditProjectState.edit_project)
async def edit_project(message: types.Message, state: FSMContext):
    p_id = int(message.text)
    projects = await state.get_data()
    project = projects['projects'][p_id - 1]
    await state.reset_data()
    await state.update_data(project=project)
    text = f'Информация о проекте:\nНазвание: {project[1]}\nОписание:\n{project[2]}\nЦена: {project[3]} руб.'
    await message.bot.send_message(message.from_user.id, text, reply_markup=edit_project_markup)

@dp.message_handler(state=EditProjectState.edit_name)
async def edit_project_name(message: types.Message, state: FSMContext):
    new_name = message.text
    data = await state.get_data()
    project = data['project']
    db.update_project_info(project[0], new_name, project[2], project[3], project[4])
    await state.finish()
    await message.bot.send_message(message.from_user.id, edit_project_name_success, reply_markup=start_markup)

@dp.message_handler(state=EditProjectState.edit_description)
async def edit_project_description(message: types.Message, state: FSMContext):
    new_description = message.text
    data = await state.get_data()
    project = data['project']
    db.update_project_info(project[0], project[1], new_description, project[3], project[4])
    await state.finish()
    await message.bot.send_message(message.from_user.id, edit_project_description_success, reply_markup=start_markup)

@dp.message_handler(state=EditProjectState.edit_price)
async def edit_project_price(message: types.Message, state: FSMContext):
    new_price = message.text
    data = await state.get_data()
    project = data['project']
    db.update_project_info(project[0], project[1], project[2], new_price, project[4])
    await state.finish()
    await message.bot.send_message(message.from_user.id, edit_project_price_success, reply_markup=start_markup)

@dp.message_handler(state=EditProjectState.edit_file, content_types=['document'])
async def edit_project_file(message: types.Message, state: FSMContext):
    data = await state.get_data()
    project = data['project']
    os.remove(project[4])
    file_path = f'projects/{message.document.file_name}'
    await message.bot.download_file_by_id(message.document.file_id, file_path)
    db.update_project_info(project[0], project[1], project[2], project[3], file_path)
    await state.finish()
    await message.bot.send_message(message.from_user.id, edit_project_file_success, reply_markup=start_markup)


@dp.message_handler(text="✏️ Добавить", state=AdminState.admin)
async def add_admin(message: types.Message):
    logging.info(f"User - {message.from_user.username} | Добавить")
    if db.is_admin(message.from_user.id):
        await AdminState.add_admin.set()
        await message.bot.send_message(message.from_user.id, add_admin_text, reply_markup=cancel_markup)
    else:
        await message.bot.send_message(message.from_user.id, not_admin_msg, reply_markup=start_markup)

@dp.message_handler(text="❌ Удалить", state=AdminState.admin)
async def delete_admin_call(message: types.Message):
    logging.info(f"User - {message.from_user.username} | Удалить")
    if db.is_admin(message.from_user.id):
        await DeleteAdminState.delete_admin.set()
        await message.bot.send_message(message.from_user.id, delete_admin_text, reply_markup=cancel_markup)
    else:
        await message.bot.send_message(message.from_user.id, not_admin_msg, reply_markup=start_markup)

@dp.message_handler(state=AdminState.add_admin)
async def add_admin(message: types.Message, state: FSMContext):
    user_id = message.text
    if db.user_exists(user_id):
        db.add_admin(user_id)
        logging.info(f"User - {message.from_user.username} | Добавил админа {user_id}")
        await message.bot.send_message(message.from_user.id, add_admin_success_text, reply_markup=admins_markup)
    else:
        await message.bot.send_message(message.from_user.id, add_admin_lose_text, reply_markup=admins_markup)
    await state.finish()

@dp.message_handler(state=DeleteAdminState.delete_admin)
async def delete_admin(message: types.Message, state: FSMContext):
    admin_id = int(message.text)
    admins = await state.get_data()
    admin = admins['admins'][admin_id - 1]
    db.delete_admin(admin[0])
    username = db.user_info(admin[0])[2]
    logging.info(f"User - {message.from_user.username} | Удалил админа {username}")
    await state.finish()
    await message.bot.send_message(message.from_user.id, delete_admin_success_text, reply_markup=admins_markup)

# Callback handlers

@dp.callback_query_handler(text="edit_name", state=EditProjectState.edit_project)
async def edit_name_call(message: types.CallbackQuery):
    logging.info(f"User - {message.from_user.username} | Изменение имени проекта")
    await message.bot.delete_message(message.from_user.id, message.message.message_id)
    await EditProjectState.edit_name.set()
    await message.bot.send_message(message.from_user.id, project_name)

@dp.callback_query_handler(text="edit_description", state=EditProjectState.edit_project)
async def edit_description_call(message: types.CallbackQuery):
    logging.info(f"User - {message.from_user.username} | Изменение описания проекта")
    await message.bot.delete_message(message.from_user.id, message.message.message_id)
    await EditProjectState.edit_description.set()
    await message.bot.send_message(message.from_user.id, project_description)

@dp.callback_query_handler(text="edit_price", state=EditProjectState.edit_project)
async def edit_price_call(message: types.CallbackQuery):
    logging.info(f"User - {message.from_user.username} | Изменение цены проекта")
    await message.bot.delete_message(message.from_user.id, message.message.message_id)
    await EditProjectState.edit_price.set()
    await message.bot.send_message(message.from_user.id, project_price)

@dp.callback_query_handler(text="edit_file", state=EditProjectState.edit_project)
async def edit_project_call(message: types.CallbackQuery):
    logging.info(f"User - {message.from_user.username} | Изменение файла проекта")
    await message.bot.delete_message(message.from_user.id, message.message.message_id)
    await EditProjectState.edit_file.set()
    await message.bot.send_message(message.from_user.id, project_file)

@dp.callback_query_handler(text="buy_project", state=Project.project_view)
async def buy_project(message: types.CallbackQuery, state: FSMContext):
    logging.info(f"User - {message.from_user.username} | Купить проект")
    await message.bot.delete_message(message.from_user.id, message.message.message_id)
    data = await state.get_data()
    project = data['project']
    await state.reset_data()
    comment = project[1] + str(uuid4())
    money = project[3]
    bill = p2p.bill(amount=money, comment=comment, lifetime=10)
    db.create_payment(message.from_user.id, bill.bill_id, money)
    payment_btn = InlineKeyboardButton("Оплатить", url=bill.pay_url)
    check_btn = InlineKeyboardButton("Проверить оплату", callback_data=f"check_{bill.bill_id}___{project[0]}")
    markup = InlineKeyboardMarkup()
    markup.row(payment_btn)
    markup.row(check_btn)
    text = f"Счет на оплату товара - {project[1]}\nСумма к оплате - {money} руб.\nСчет действителен в течении 10 минут!"
    await message.bot.send_message(message.from_user.id, text, reply_markup=markup)

@dp.callback_query_handler(text_contains='check_', state='*')
async def check_payment(message: types.CallbackQuery, state: FSMContext):
    data = str(message.data.split('check_', maxsplit=1)[1])
    bill = str(data.split('___', maxsplit=1)[0])
    p_id = int(data.split('___', maxsplit=1)[1])
    info = db.get_payment(bill)
    if info:
        if str(p2p.check(bill_id=bill).status) == "PAID":
            user_id = message.from_user.id
            db.change_payment_status(bill, True)
            db.add_access(user_id, p_id, bill)
            await state.finish()
            await message.bot.delete_message(message.from_user.id, message.message.message_id)
            await message.bot.send_message(message.from_user.id, payment_success, reply_markup=start_markup)
        else:
            await message.bot.send_message(message.from_user.id, payment_failed)
    else:
        await message.bot.send_message(message.from_user.id, "Счет не найден!")
    

# Other messages handler
@dp.message_handler(content_types=['text'])
async def standart(message: types.Message):
    logging.info(f"User - {message.from_user.username} | {message.text}")
    await message.bot.send_message(message.from_user.id, other_text)