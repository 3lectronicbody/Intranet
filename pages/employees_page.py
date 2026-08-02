from functools import partial

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QVBoxLayout, QLabel, QComboBox
from helper_functions import clear_layout
from API.api import API_CLIENT
from API.pydantic_models import UsersSchema, Role





class EmployeesPage(QWidget):
    back_signal = Signal()
    def __init__(self):
        super().__init__()
        self.user_id = None

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.data_layout = QGridLayout()
        self.main_layout.addLayout(self.data_layout)

        # Put next widgets at the bottom of the page
        self.main_layout.addStretch()

        self.back_button = QPushButton("Back")
        self.main_layout.addWidget(self.back_button)
        self.back_button.clicked.connect(self.back_signal.emit)
    def refresh_data(self):
        clear_layout(self.data_layout, grid_layout=True)
        response = API_CLIENT.get("/users").json()
        employees = [UsersSchema.model_validate(emp) for emp in response]
        counter = 0
        for emp in employees:
            label = QLabel(f"{emp.name or "Unknown name"} : {emp.email}")
            if emp.id == self.user_id:
                label.setStyleSheet("""
                    QLabel:hover { 
                        color: blue;
                        background-color: darkgrey; 
                    }
                    QLabel {
                    font-weight: bold;
                    text-decoration: underline;
                    color: lightblue;
                    }
                """)
            else:
                label.setStyleSheet("""
                    QLabel:hover { 
                        color: blue;
                        background-color: darkgrey;  
                    }
                """)

            label.setToolTip(
                f"ID: {emp.id}, Role: {emp.role}, Email: {emp.email}"
            )
            self.data_layout.addWidget(label,counter, 0)
            # Add dropdown menu
            dropdown_menu = QComboBox()
            dropdown_menu.addItems([role.value for role in Role])
            self.data_layout.addWidget(dropdown_menu, counter, 1)
            dropdown_menu.setCurrentText(emp.role)
            dropdown_menu.currentTextChanged.connect(partial(self.dropdown_menu_handler, emp.id, ))

            counter += 1
    @staticmethod
    def dropdown_menu_handler(user_id, new_role_text):
        API_CLIENT.patch(f"/users/{user_id}", json={"role": new_role_text})
    def load_user(self, user_id):
        self.user_id = user_id




