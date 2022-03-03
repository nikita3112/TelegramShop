from aiogram.dispatcher.filters.state import State, StatesGroup


# Состояния для создания проекта
class AddProjectStates(StatesGroup):
    project_name = State()
    project_description = State()
    project_price = State()
    project_file = State()

class AdminState(StatesGroup):
    admin = State()
    add_admin = State()
    projects = State()

class DeleteAdminState(StatesGroup):
    delete_admin = State()
    delete_project = State()

class EditProjectState(StatesGroup):
    edit_project = State()
    edit_name = State()
    edit_description = State()
    edit_price = State()
    edit_file = State()

class Project(StatesGroup):
    project_choise = State()
    project_view = State()

class SoldProjects(StatesGroup):
    sold_project = State()