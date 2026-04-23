from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QMessageBox, QLabel

from database.models import Users, Role


class MainMenuPage(QWidget):
    logout_signal = Signal()
    projects_signal = Signal()
    employees_signal = Signal()
    def __init__(self, database):
        super().__init__()

        self.user_id = None
        self.user = None
        self.database = database



        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        self.welcome_label = QLabel("__load data__")
        self.main_layout.addWidget(self.welcome_label, 0, 0, alignment=Qt.AlignCenter)

        self.projects_button = QPushButton("Projects", flat=True)
        self.main_layout.addWidget(self.projects_button, 1, 0)
        self.projects_button.clicked.connect(lambda: self.projects_signal.emit())

        self.employees_button = QPushButton("Employees", flat=True)
        self.main_layout.addWidget(self.employees_button, 2, 0)
        self.employees_button.clicked.connect(self.employees_button_handler)


        self.main_layout.setRowStretch(3, 1)



        self.logout_button = QPushButton("Logout")
        self.main_layout.addWidget(self.logout_button, 4, 0)
        self.logout_button.clicked.connect(self.logout_button_handler)

    def load_user(self, user_id):
        self.user_id = user_id
        with self.database.session() as session:
            self.user = session.query(Users).get(user_id)
            is_authorized = self.user.role in [Role.DEVELOPER.value, Role.ADMIN.value]
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

