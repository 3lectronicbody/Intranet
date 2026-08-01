from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QGridLayout, QTextEdit, QPushButton, QMessageBox
from PySide6.QtCore import Signal
from datetime import datetime
from API.api import client


class CreateProjectPage(QWidget):
    create_signal = Signal(int)
    cancel_signal = Signal(int)
    def __init__(self, user_id = None):
        super().__init__()
        self.user_id = user_id

        response = client.get("last_project_number/")
        self.actual_number = response.json() + 1
        self.formatted_number = f"{self.actual_number:03d}"
        self.formatted_number = str(datetime.now().year) + "/" + self.formatted_number



        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        self.number_label = QLabel("Number: ")
        self.main_layout.addWidget(self.number_label, 0, 0)
        self.number_input = QLineEdit()

        self.number_input.setText(self.formatted_number)
        self.number_input.setStyleSheet("color: #3498db; font-weight: bold;")
        self.main_layout.addWidget(self.number_input, 0, 1)
        self.number_input.setReadOnly(True)

        self.name_label = QLabel("Project Name: ")
        self.name_input = QLineEdit()
        self.main_layout.addWidget(self.name_label, 1, 0)
        self.main_layout.addWidget(self.name_input, 1, 1)

        self.description_label = QLabel("Description: ")
        self.description_input = QTextEdit()
        self.main_layout.addWidget(self.description_label, 2, 0)
        self.main_layout.addWidget(self.description_input, 2, 1)

        self.main_layout.setRowStretch(3, 1)

        self.create_button = QPushButton("CREATE")
        self.create_button.setStyleSheet("color: green;")
        self.main_layout.addWidget(self.create_button, 4, 1)
        self.create_button.clicked.connect(lambda _:self.create_project_handler())

        self.cancel_button = QPushButton("Cancel")
        self.main_layout.addWidget(self.cancel_button, 4, 0)
        self.cancel_button.clicked.connect(lambda _: self.cancel_signal.emit(self.user_id))

    def load_user(self, user_id):
        self.user_id = user_id
    def create_project_handler(self):
        number = self.actual_number
        name = self.name_input.text()
        description = self.description_input.toPlainText()
        if not name:
            QMessageBox.warning(self, "Warning", "Project name cannot be empty")
            self.name_input.setFocus()
            return

        params = {
            "name": name,
            "number": number,
            "description": description,
            "project_owner": self.user_id
        }
        response = client.post("/new_project", params=params)

        if response.status_code == 200:
            self.name_input.setText("")
            self.description_input.setText("")
            self.create_signal.emit(self.user_id)
        else:
            QMessageBox.critical(self, "Error", "Could not create project")
