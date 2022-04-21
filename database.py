import sqlite3
import os

from kivy.utils import platform

class Database:
    def __init__(self):
        PATH = '.'
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            app_folder = os.path.dirname(os.path.abspath(__file__))
            PATH = "/storage/emulated/0/DCIM"
        self.con = sqlite3.connect(os.path.join(PATH, 'todo.db'))
        self.cursor = self.con.cursor()
        self.create_task_table()
        self.create_theme_table()
        print(PATH + 'todo.db')

    def create_theme_table(self):
        """Create them table"""
        self.cursor.execute("CREATE TABLE IF NOT EXISTS themes(theme text, colour text)")
        self.con.commit()

    def save_theme(self, theme, colour):
        """Save theme"""
        self.cursor.execute("DELETE FROM themes")
        self.cursor.execute("INSERT INTO themes(theme, colour) VALUES(?, ?)", (theme, colour))
        self.con.commit()

    def get_themes(self):
        """Get themes"""
        themes = self.cursor.execute("SELECT theme, colour FROM themes").fetchone()

        return themes

    def create_task_table(self):
        """Create tasks table"""
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS tasks(id integer PRIMARY KEY AUTOINCREMENT, task varchar(50) NOT NULL, due_date varchar(50), desc text, completed BOOLEAN NOT NULL CHECK (completed IN (0, 1)))")
        self.con.commit()

    def create_task(self, task, due_date = None, desc = None):
        """Create a task"""
        self.cursor.execute("INSERT INTO tasks(task, due_date, desc, completed) VALUES(?, ?, ?, ?)", (task, due_date, desc, 0))
        self.con.commit()

        # GETTING THE LAST ENTERED ITEM SO WE CAN ADD IT TO THE TASK LIST
        created_task = self.cursor.execute("SELECT id, task, due_date FROM tasks WHERE task = ? and completed = 0",
                                           (task,)).fetchall()
        return created_task[-1]

    def get_tasks(self):
        """Get tasks"""
        uncomplete_tasks = self.cursor.execute("SELECT id, task, due_date, desc, completed FROM tasks WHERE completed = 0").fetchall()
        completed_tasks = self.cursor.execute("SELECT id, task, due_date, desc, completed FROM tasks WHERE completed = 1").fetchall()

        return completed_tasks, uncomplete_tasks

    def mark_task_as_complete(self, taskid):
        """Marking tasks as complete"""
        self.cursor.execute("UPDATE tasks SET completed=1 WHERE id=?", (taskid,))
        self.con.commit()

    def mark_task_as_incomplete(self, taskid):
        """Mark task as uncomplete"""
        self.cursor.execute("UPDATE tasks SET completed=0 WHERE id=?", (taskid,))
        self.con.commit()

        # return the text of the task
        task_text = self.cursor.execute("SELECT task FROM tasks WHERE id=?", (taskid,)).fetchall()
        return task_text[0][0]

    def delete_task(self, taskid):
        """Delete a task"""
        self.cursor.execute("DELETE FROM tasks WHERE id=?", (taskid,))
        self.con.commit()

    def close_db_connection(self):
        self.con.close()
