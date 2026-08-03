from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QFrame, QMessageBox, QVBoxLayout
from database.models import ProjectDetails
from helper_functions import clear_layout
from custom_widgets_folder.custom_widgets import EditItem, EditActivity, EditToDo
from helper_functions import confirmation_dialog
from PySide6.QtGui import Qt
from API.api import API_CLIENT
from types import SimpleNamespace


class ItemsTab(QWidget):
    def __init__(self, project_id, user_id):
        super().__init__()

        self.project_id = project_id
        self.user_id= user_id

        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        # First data initialization
        self.load_data()

    def load_data(self):
        clear_layout(self.main_layout, grid_layout=True)
        # ADD HEADER
        name_label = QLabel("Name")
        name_label.setStyleSheet("font-weight: bold;")
        code_label = QLabel("Code")
        code_label.setStyleSheet("font-weight: bold;")
        quantity_label = QLabel("Quantity")
        quantity_label.setStyleSheet("font-weight: bold;")
        unit_label = QLabel("Unit")
        unit_label.setStyleSheet("font-weight: bold;")
        self.main_layout.addWidget(name_label, 0, 0)
        self.main_layout.addWidget(code_label, 0, 1)
        self.main_layout.addWidget(quantity_label, 0, 2)
        self.main_layout.addWidget(unit_label, 0, 3)
        # ADD VERTICAL HORIZONTAL LINE
        hor_line = QFrame()
        hor_line.setFrameShape(QFrame.HLine)
        hor_line.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(hor_line, 1, 0, 1, 6)



        counter = 2
        project_details = API_CLIENT.get(f"/projects/project/details/{self.project_id}").json()

        items = [SimpleNamespace(**detail) for detail in project_details if detail['item'] is not None]
        for item in items:
            name_label = QLabel(item.item)
            self.main_layout.addWidget(name_label, counter, 0)
            name_label.setToolTip(str(item.description))
            code_label = QLabel(item.item_code or "")
            self.main_layout.addWidget(code_label, counter, 1)
            quantity_label = QLabel(str(item.quantity))
            self.main_layout.addWidget(quantity_label, counter, 2)
            unit_label = QLabel(str(item.unit))
            self.main_layout.addWidget(unit_label, counter, 3)
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda _, item_id=item.id: self.delete_button_handler(item_id))
            self.main_layout.addWidget(delete_button, counter, 4)
            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda _, item_id=item.id: self.edit_button_handler(item_id))
            self.main_layout.addWidget(edit_button, counter, 5)
            counter += 1
        self.main_layout.setRowStretch(counter, 1)

    def edit_button_handler(self, item_id):
        edit_dialog = EditItem(self.project_id,self.user_id, item_id)
        edit_dialog.save_signal.connect(self.load_data)
        edit_dialog.exec()


    def delete_button_handler(self, item_id):
        confirmation = confirmation_dialog(self, title="Warning", message="Are you sure you want to delete this item?")
        if confirmation == QMessageBox.Yes:
            with self.database.session() as session:
                item = session.query(ProjectDetails).get(item_id)
                session.delete(item)
                session.commit()
            self.load_data()

class ActivitiesTab(QWidget):
    def __init__(self,project_id, user_id):
        super().__init__()

        self.project_id = project_id
        self.user_id = user_id

        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        self.load_data()

    def load_data(self):
        clear_layout(self.main_layout, grid_layout=True)

        # ADD HEADER
        name_label = QLabel("Name")
        name_label.setStyleSheet("font-weight: bold;")
        time_label = QLabel("Time")
        time_label.setStyleSheet("font-weight: bold;")
        self.main_layout.addWidget(name_label, 0, 0)
        self.main_layout.addWidget(time_label, 0, 1)
        # ADD VERTICAL HORIZONTAL LINE
        hor_line = QFrame()
        hor_line.setFrameShape(QFrame.HLine)
        hor_line.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(hor_line, 1, 0, 1, 5)

        project_details = API_CLIENT.get(f"/projects/project/details/{self.project_id}")
        counter = 2
        activities = [SimpleNamespace(**detail) for detail in project_details.json() if detail['activity'] is not None]
        for activity in activities:
            name_label = QLabel(activity.activity)
            self.main_layout.addWidget(name_label, counter, 0)
            quantity_label = QLabel(str(activity.quantity))
            self.main_layout.addWidget(quantity_label, counter, 1)
            delete_button = QPushButton("Delete")
            self.main_layout.addWidget(delete_button, counter, 3)
            delete_button.clicked.connect(lambda _, item_id=activity.id: self.delete_button_handler(item_id))
            edit_button = QPushButton("Edit")
            self.main_layout.addWidget(edit_button, counter, 4)
            edit_button.clicked.connect(lambda _, item_id=activity.id: self.edit_button_handler(item_id))
            counter += 1
        self.main_layout.setRowStretch(counter, 1)
    def edit_button_handler(self, item_id):
        dialog = EditActivity(self.database, self.project_id, self.user_id, item_id)
        dialog.save_signal.connect(self.load_data)
        dialog.exec()
        # self.load_data()
    def delete_button_handler(self, item_id):
        confirm = confirmation_dialog(self, title="Warning", message="Are you sure you want to delete this activity?")
        if confirm == QMessageBox.Yes:
            with self.database.session() as session:
                item = session.query(ProjectDetails).get(item_id)
                session.delete(item)
                session.commit()
            self.load_ddata()

class ToDoTab(QWidget):
    def __init__(self, project_id, user_id):
        super().__init__()

        self.project_id = project_id
        self.user_id = user_id

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.empty_list_label = QLabel("No To-Do activities")
        self.layout.addWidget(self.empty_list_label, alignment=Qt.AlignmentFlag.AlignCenter)


        self.main_layout = QGridLayout()
        self.layout.addLayout(self.main_layout)

        self.load_data()
        self.layout.addStretch()

    def load_data(self):
        clear_layout(self.main_layout, grid_layout=True)
        project_details = API_CLIENT.get(f"/projects/project/details/{self.project_id}").json()

        todos = [SimpleNamespace(**detail) for detail in project_details if detail['todo'] is not None]
        if todos:
            self.empty_list_label.hide()
            counter = 1
            for index, item in enumerate(todos, start=1):
                id_label = QLabel(str(index))
                self.main_layout.addWidget(id_label, index-1,0)
                todo_label = QLabel(item.todo)
                self.main_layout.addWidget(todo_label, index-1,1)
                quantity_label = QLabel(str(item.quantity))
                self.main_layout.addWidget(quantity_label, index-1,2)
                complete_button = QPushButton("Complete")
                complete_button.clicked.connect(lambda _, item_id = item.id: self.complete_button_handler(item_id))
                self.main_layout.addWidget(complete_button, index-1,3)
                edit_button = QPushButton("Edit")
                edit_button.clicked.connect(lambda _, item_id = item.id: self.edit_button_handler(item_id))
                self.main_layout.addWidget(edit_button, index-1,4)

                counter += 1
            self.main_layout.setRowStretch(counter, 1)


        else:
            self.empty_list_label.show()
    def complete_button_handler(self, item_id):
        confirm = confirmation_dialog(self, title="Warning", message="Are you sure you want to complete this item?")
        if confirm == QMessageBox.Yes:
            with self.database.session() as session:
                item = session.query(ProjectDetails).get(item_id)
                item.activity = item.todo
                item.todo = None
                session.commit()
            self.load_data()
    def edit_button_handler(self, item_id):
        dialog = EditToDo(self.database, self.project_id, self.user_id, item_id)
        dialog.save_signal.connect(self.load_data)
        dialog.exec()








