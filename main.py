from kivy.properties import StringProperty, ListProperty
from kivymd.app import MDApp
from kivymd.material_resources import dp
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import MDList, OneLineIconListItem
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.picker import MDDatePicker, MDTimePicker
from datetime import datetime
from kivymd.uix.list import TwoLineAvatarIconListItem, ILeftBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.utils import platform

kivy.require("2.0.0")

if platform == "android":
    from android.permissions import request_permissions, Permission

    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

from database import Database

# Initialize database instance
db = Database()

class ListScreen(Screen):
    pass

class SettingScreen(Screen):
    pass

class ContentNavigationDrawer(MDBoxLayout):
    pass

class SortDrawer(MDBoxLayout):
    pass

class ThemeDialog(MDBoxLayout):
    """OPENS A DIALOG BOX THAT GETS THE THEME FROM THE USER"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class TaskDialog(MDBoxLayout):
    """OPENS A DIALOG BOX THAT SHOWS TASK INFO"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class ItemDrawer(OneLineIconListItem):
    icon = StringProperty()
    text_color = ListProperty((0, 0, 0, 1))

class DrawerList(ThemableBehavior, MDList):
    def set_color_item(self, instance_item):
        """Called when tap on a menu item."""

        # Set the color of the icon and text for the menu item.
        for item in self.children:
            if item.text_color == self.theme_cls.primary_color:
                item.text_color = self.theme_cls.text_color
                break
        instance_item.text_color = self.theme_cls.primary_color

class CreateTaskDialog(MDBoxLayout):
    """OPENS A DIALOG BOX THAT GETS THE TASK FROM THE USER"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.date_text.text = str(datetime.now().strftime('%A, %b %d, %Y'))
        self.ids.time_text.text = str(datetime.now().strftime('%I:%M %p'))

    def show_date_picker(self):
        """Opens the date picker"""
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()

    def show_time_picker(self):
        """Opens the time picker"""
        time_dialog = MDTimePicker()
        time_dialog.bind(time = self.get_time)
        time_dialog.open()

    def on_save(self, instance, value, date_range):
        """This function gets the date from the date picker and converts its into a
        more friendly form then changes the date label on the dialog to that"""

        date = value.strftime('%A, %b %d, %Y')
        self.ids.date_text.text = str(date)

    def get_time(self, instance, value):
        """Turn time from time picker to a friendlier form"""

        time = value.strftime('%I:%M %p')
        self.ids.time_text.text = str(time)

class ListItemWithCheckbox(TwoLineAvatarIconListItem):
    '''Custom list item'''

    def __init__(self, pk=None, **kwargs):
        super().__init__(**kwargs)
        # state a pk which we shall use link the list items with the database primary keys
        self.pk = pk

    def mark(self, check, the_list_item):
        '''mark the task as complete or incomplete'''
        if check.active == True:
            the_list_item.text = '[s]' + the_list_item.text + '[/s]'
            db.mark_task_as_complete(the_list_item.pk)  # here
        else:
            the_list_item.text = str(db.mark_task_as_incomplete(the_list_item.pk))  # Here

    def delete_item(self, the_list_item):
        '''Delete the task'''
        self.parent.remove_widget(the_list_item)
        db.delete_task(the_list_item.pk)  # Here


class LeftCheckbox(ILeftBodyTouch, MDCheckbox):
    '''Custom left container'''


class PlannerApp(MDApp):
    task_dialog = None
    theme_dialog = None
    checklist_dialog = None

    def build(self):
        pass

    def show_checklist_dialog(self):
        if not self.checklist_dialog:
            self.checklist_dialog = MDDialog(
                title="Create Task",
                type="custom",
                content_cls=CreateTaskDialog(),
            )
        self.checklist_dialog.content_cls.ids.desc_text.text = ""
        self.checklist_dialog.open()

    def show_theme_dialog(self):
        if not self.theme_dialog:
            self.theme_dialog = MDDialog(
                title="Change Theme",
                type="custom",
                content_cls=ThemeDialog(),
            )

        self.theme_dialog.open()

    def show_task_dialog(self, the_list_item):
        if not self.task_dialog:
            self.task_dialog = MDDialog(
                title="Task Description",
                type="custom",
                content_cls=TaskDialog(),
            )

        completed_tasks, uncomplete_tasks = db.get_tasks()

        # Loop through all the tasks to find the one that matches the id
        for task in uncomplete_tasks:
            if task[0] == the_list_item.pk:
                self.task_dialog.content_cls.ids.read_task_text.text = task[3]
        for task in completed_tasks:
            if task[0] == the_list_item.pk:
                self.task_dialog.content_cls.ids.read_task_text.text = task[3]

        self.task_dialog.open()

    def on_start(self):
        """Load the saved tasks and add them to the MDList widget when the application starts"""
        try:
            completed_tasks, uncomplete_tasks = db.get_tasks()

            self.load_tasks(uncomplete_tasks, completed_tasks)

        except Exception as e:
            print(e)
            pass

        """Load and apply themes"""
        try:
            themes = db.get_themes()

            if themes != []:
                self.theme_cls.theme_style = themes[0]
                self.theme_cls.primary_palette = themes[1]

            if self.theme_cls.theme_style == "Dark":
                self.root.ids.theme_switch.active = True
            else:
                self.root.ids.theme_switch.active = False
        except Exception as e:
            print(e)
            pass

        """Create the dropdown menu"""
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"Sort By:",
                "height": dp(56),
                "on_release": lambda x=f"Earliest to Latest": None,
            },
            {
                "viewclass": "OneLineListItem",
                "text": f"Earliest to Latest",
                "height": dp(56),
                "on_release": lambda x=f"Earliest to Latest": self.menu_callback(x, False, 2),
            },
            {
                "viewclass": "OneLineListItem",
                "text": f"Latest to Earliest",
                "height": dp(56),
                "on_release": lambda x=f"Latest to Earliest": self.menu_callback(x, True, 2),
            },
            {
                "viewclass": "OneLineListItem",
                "text": f"Date Created",
                "height": dp(56),
                "on_release": lambda x=f"Date Created": self.menu_callback(x, False, 0),
            },
            {
                "viewclass": "OneLineListItem",
                "text": f"Latest Date Created",
                "height": dp(56),
                "on_release": lambda x=f"Latest Date Created": self.menu_callback(x, True, 0),
            }
        ]
        self.menu = MDDropdownMenu(
            items=menu_items,
            width_mult=4,
        )

    def callback(self, button):
        self.menu.caller = button
        self.menu.open()

    def menu_callback(self, text_item, reverse, index):
        complete_tasks, uncomplete_tasks = db.get_tasks()

        if uncomplete_tasks != []:
            uncomplete_tasks = self.sort_list(uncomplete_tasks, reverse, index)
        if complete_tasks != []:
            complete_tasks = self.sort_list(complete_tasks, reverse, index)

        self.load_tasks(uncomplete_tasks, complete_tasks)

        self.menu.dismiss()

    # 0: IDs
    # 1: Name
    # 2: Date
    def sort_list(self, list, reverse, index):
        sorted_list = []

        if index == 0:
            sorted_list = list
            sorted_list.sort(key = lambda x: x[0], reverse = reverse)
        elif index == 1:
            sorted_list = list
            sorted_list.sort(key=lambda x: x[1], reverse = reverse)
        elif index == 2:
            date_list = []

            # Isolate dates and ids
            for task in list:
                # Convert date to a more easily manipulable format
                date = datetime.strptime(task[2], '%A, %b %d, %Y   %I:%M %p')
                #'2022-03-20 12:46:00'

                # Put dates and ids in a list
                temp = [task[0], date]

                #[1, datetime.datetime(2022, 3, 20, 12, 53)]
                date_list.append(temp)

            # Sort dates
            date_list.sort(key = lambda x: x[1], reverse = reverse)

            for date in date_list:
                for task in list:
                    if task[0] == date[0]:
                        sorted_list.append(task)

        return sorted_list

    def load_tasks(self, uncomplete_tasks, completed_tasks):
        # Clear checklist
        self.root.ids.checklist.clear_widgets()

        if uncomplete_tasks != []:
            for task in uncomplete_tasks:
                add_task = ListItemWithCheckbox(pk=task[0], text=task[1], secondary_text=task[2])
                self.root.ids.checklist.add_widget(add_task)

        if completed_tasks != []:
            for task in completed_tasks:
                add_task = ListItemWithCheckbox(pk=task[0], text='[s]' + task[1] + '[/s]', secondary_text=task[2])
                add_task.ids.check.active = True
                self.root.ids.checklist.add_widget(add_task)

    def close_checklist_dialog(self, *args):
        self.checklist_dialog.dismiss()

    def close_theme_dialog(self, *args):
        self.theme_dialog.dismiss()

        # Save theme
        db.save_theme(self.theme_cls.theme_style, self.theme_cls.primary_palette)

    def close_task_dialog(self, *args):
        self.task_dialog.dismiss()

    def set_theme(self, theme):
        self.theme_cls.primary_palette = theme

    def toggle_dark_mode(self):
        if self.theme_cls.theme_style == "Dark" and self.root.ids.theme_switch.active == False:
            self.theme_cls.theme_style = "Light"
        if self.theme_cls.theme_style == "Light" and self.root.ids.theme_switch.active == True:
            self.theme_cls.theme_style = "Dark"

        # Save theme
        db.save_theme(self.theme_cls.theme_style, self.theme_cls.primary_palette)

    def add_task(self, task, task_date, task_desc):
        '''Add task to the list of tasks'''

        # Add task to the db
        created_task = db.create_task(task.text, task_date, task_desc)  # Here

        # return the created task details and create a list item
        self.root.ids.checklist.add_widget(
            ListItemWithCheckbox(pk=created_task[0], text='[b]' + created_task[1] + '[/b]',
                                 secondary_text=created_task[2]))  # Here
        task.text = ''


if __name__ == '__main__':
    app = PlannerApp()
    app.run()