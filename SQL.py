import sqlite3

class SQLite:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()
    
    # User

    def add_new_user(self, user_id, user_name):
        '''Add new user to users'''
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`, `username`) VALUES (?, ?)", (user_id, user_name, ))
    
    def user_exists(self, user_id):
        '''Check if user already exists'''
        with self.connection:
            res = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id, )).fetchall()
        return bool(len(res))
    
    def get_all_users(self):
        '''Get all users'''
        with self.connection:
            return self.cursor.execute("SELECT * FROM `users`").fetchall()

    def user_info(self, user_id):
        '''Get info about user'''
        with self.connection:
            return self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id, )).fetchone()

    def is_admin(self, user_id):
        '''Check if user is admin'''
        with self.connection:
            res = self.cursor.execute("SELECT * FROM `admins` WHERE `user_id` = ?", (user_id, )).fetchall()
        return bool(len(res))

    def add_admin(self, user_id):
        '''Add admin'''
        with self.connection:
            return self.cursor.execute("INSERT OR IGNORE INTO `admins` (`user_id`) VALUES (?)", (user_id, ))
    
    def delete_admin(self, user_id):
        '''Delete admin'''
        with self.connection:
            return self.cursor.execute("DELETE FROM `admins` WHERE `user_id` = ?", (user_id, ))

    def get_admins(self):
        '''Get all admins'''
        with self.connection:
            return self.cursor.execute("SELECT * FROM `admins`").fetchall()

    # Project

    def add_new_project(self, name, description, price, file_path):
        '''Add new project to projects'''
        with self.connection:
            return self.cursor.execute("INSERT INTO `projects` (`project_name`, `project_description`, `project_price`, `file_path`) VALUES (?, ?, ?, ?)", (name, description, price, file_path, ))
    
    def get_project_info(self, p_id):
        '''Get info about project'''
        with self.connection:
            return self.cursor.execute("SELECT * FROM `projects` WHERE `id` = ?", (p_id, )).fetchone()
    
    def get_all_projects(self):
        '''Get all projects'''
        with self.connection:
            return self.cursor.execute("SELECT * FROM `projects`").fetchall()
    
    def update_project_info(self, p_id, name, description, price, path):
        '''Update info about projects'''
        with self.connection:
            return self.cursor.execute("UPDATE `projects` SET `project_name` = ?, `project_description` = ?, `project_price` = ?, `file_path` = ? WHERE `id` = ?", (name, description, price, path, p_id, ))
    
    def delete_project(self, p_id):
        '''Delete project'''
        with self.connection:
            return self.cursor.execute("DELETE FROM `projects` WHERE `id` = ?", (p_id, ))
    
    # Payment

    def create_payment(self, user_id, payment_id, payment_sum):
        '''Create payment'''
        with self.connection:
            return self.cursor.execute("INSERT INTO `payments` (`user_id`, `payment_id`, `payment_sum`) VALUES (?, ?, ?)", (user_id, payment_id, payment_sum, ))
    
    def get_payment(self, payment_id):
        '''Get payment info'''
        with self.connection:
            return self.cursor.execute("SELECT * FROM `payments` WHERE `payment_id` = ?", (payment_id, )).fetchone()
    
    def change_payment_status(self, payment_id, status):
        '''Change status'''
        with self.connection:
            return self.cursor.execute("UPDATE `payments` SET `is_complete` = ? WHERE `payment_id` = ?", (status, payment_id, ))
    
    # Accesses

    def add_access(self, user_id, p_id, payment_id):
        '''Add access to user'''
        with self.connection:
            return self.cursor.execute("INSERT INTO `accesses` (`user_id`, `project_id`, `payment_id`) VALUES (?, ?, ?)", (user_id, p_id, payment_id, ))
    
    def get_user_accesses(self, user_id):
        '''Get all user accesses'''
        with self.connection:
            return self.cursor.execute("SELECT `project_id` FROM `accesses` WHERE `user_id` = ?", (user_id, )).fetchall()