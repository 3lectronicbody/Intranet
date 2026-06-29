from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QMessageBox, QLabel

from database.models import Users, Role


class MainMenuPage(QWidget):
    logout_signal = Signal()
    projects_signal = Signal()
    employees_signal = Signal()
    service_projects_signal =Signal()
    def __init__(self, database):
        super().__init__()

        self.user_id = None
        self.user = None
        self.database = database

        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        self.welcome_label = QLabel("__load data__")
        self.main_layout.addWidget(self.welcome_label, 0, 0, alignment=Qt.AlignCenter)

        self.menu_items = []

        self.projects_button = QPushButton("Projects", flat=True)
        # self.projects_button.setStyleSheet("background-color:#2c3e50; border-radius: 4px;")
        self.main_layout.addWidget(self.projects_button, 1, 0)
        self.projects_button.clicked.connect(lambda: self.projects_signal.emit())
        self.menu_items.append(self.projects_button)

        self.employees_button = QPushButton("Employees", flat=True)
        self.main_layout.addWidget(self.employees_button, 2, 0)
        self.employees_button.clicked.connect(self.employees_button_handler)
        self.menu_items.append(self.employees_button)

        self.service_projects_button = QPushButton("Service Projects", flat=True)
        self.main_layout.addWidget(self.service_projects_button, 3, 0)
        self.service_projects_button.clicked.connect(self.service_projects_button_handler)
        self.menu_items.append(self.service_projects_button)

        for flat_button in self.menu_items:
            flat_button.setStyleSheet("""
                    :hover {
                        background-color: darkgrey;
                    }
                """)


        self.main_layout.setRowStretch(4, 1)



        self.logout_button = QPushButton("Logout")
        self.main_layout.addWidget(self.logout_button, 5, 0)
        self.logout_button.clicked.connect(self.logout_button_handler)

    def load_user(self, user_id):
        self.user_id = user_id
        with self.database.session() as session:
            self.user = session.query(Users).get(user_id)
            is_authorized = self.user.role in [Role.DEVELOPER.value, Role.ADMIN.value, Role.USER.value]
            self.employees_button.setEnabled(is_authorized)
            self.welcome_label.setText(f"Welcome <b>{self.user.email}</b>")


    def showEvent(self, event, /):
        super().showEvent(event)

    def logout_button_handler(self):
        message = QMessageBox()
        message.setText("Do You want to logout?")
        message.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = message.exec()
        if result == QMessageBox.Yes:
            self.logout_signal.emit()
            return
        elif result == QMessageBox.No:
            return
    def employees_button_handler(self):
        self.employees_signal.emit()
    def service_projects_button_handler(self):
        pass

