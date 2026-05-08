from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton
from database.models import ProjectDetails
from helper import clear_layout


class ItemsTab(QWidget):
    def __init__(self, database, project_id, user_id):
        super().__init__()

        self.database = database
        self.project_id = project_id
        self.user_id= user_id

        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        self.load_data()

    def load_data(self):
        clear_layout(self.main_layout, grid_layout=True)
        with self.database.session() as session:
            counter = 0
            project_details = session.query(ProjectDetails).filter_by(project_id=self.project_id).all()
            items = [detail for detail in project_details if detail.item is not None]
            for item in items:
                name_label = QLabel(item.item)
                self.main_layout.addWidget(name_label, counter, 0)
                code_label = QLabel(item.item_code)
                self.main_layout.addWidget(code_label, counter, 1)
                quantity_label = QLabel(str(item.quantity))
                self.main_layout.addWidget(quantity_label, counter, 2)
                delete_button = QPushButton("Delete")
                self.main_layout.addWidget(delete_button, counter, 3)
                edit_button = QPushButton("Edit")
                self.main_layout.addWidget(edit_button, counter, 4)
                counter += 1
        self.main_layout.setRowStretch(counter, 1)

class ActivitiesTab(QWidget):
    def __init__(self, database, project_id, user_id):
        super().__init__()
        self.database = database
        self.project_id = project_id
        self.user_id = user_id

        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        self.load_data()

    def load_data(self):
        clear_layout(self.main_layout, grid_layout=True)
        with self.database.session() as session:
            counter = 0
            project_details = session.query(ProjectDetails).filter_by(project_id=self.project_id).all()
            items = [detail for detail in project_details if detail.activity is not None]
            for item in items:
                name_label = QLabel(item.activity)
                self.main_layout.addWidget(name_label, counter, 0)
                quantity_label = QLabel(str(item.quantity))
                self.main_layout.addWidget(quantity_label, counter, 2)
                delete_button = QPushButton("Delete")
                self.main_layout.addWidget(delete_button, counter, 3)
                edit_button = QPushButton("Edit")
                self.main_layout.addWidget(edit_button, counter, 4)
                counter += 1
        self.main_layout.setRowStretch(counter, 1)





