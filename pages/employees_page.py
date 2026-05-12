from functools import partial

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QVBoxLayout, QLabel, QComboBox
from database.models import Role
from PySide6.QtCore import Qt

from database.models import Users
from helper_functions import clear_layout


class EmployeesPage(QWidget):
    back_signal = Signal()
    def __init__(self, database):
        super().__init__()
        self.database = database
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



    def load_user(self, user_id):
        self.user_id = user_id
    def refresh_data(self):
        clear_layout(self.data_layout, grid_layout=True)
        with self.database.session() as session:
            employees = session.query(Users).all()
            counter = 0
            for emp in employees:
                label = QLabel(f"{emp.name or "Unknown name"} : {emp.email}")
                label.setStyleSheet("""
                    QLabel:hover { 
                        color: blue; 
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
                dropdown_menu.currentTextChanged.connect(partial(self.dropdown_menu_handler, emp.id,))
                if emp.id == self.user_id:
                    dropdown_menu.setEnabled(False)
                counter += 1
    def dropdown_menu_handler(self, employee_id, new_role_text):
        with self.database.session() as session:
            user = session.query(Users).get(employee_id)
            role = new_role_text
            if user:
                user.role = role
                session.commit()
                # self.refresh_data()

