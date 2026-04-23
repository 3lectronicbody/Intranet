from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QLineEdit, QHBoxLayout, QPushButton
from database.models import Users


class SignUpPage(QWidget):
    cancel_signal = Signal()
    create_signal = Signal()
    def __init__(self, database):
        super().__init__()

        self.database = database

        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        self.name_label = QLabel("Email: ")
        self.main_layout.addWidget(self.name_label, 0, 0)
        self.name_input = QLineEdit()
        self.main_layout.addWidget(self.name_input, 0, 1)

        self.password_label = QLabel("Password: ")
        self.main_layout.addWidget(self.password_label, 1, 0)
        self.password_input = QLineEdit()
        self.main_layout.addWidget(self.password_input, 1, 1)

        self.main_layout.setRowStretch(2, 1)

        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout, 3, 0, 1, 2)

        self.cancel_button = QPushButton("Cancel")
        self.button_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.cancel_signal.emit)

        self.create_button = QPushButton("Create")
        self.button_layout.addWidget(self.create_button)
        self.create_button.clicked.connect(self.create_button_handler)

    def create_button_handler(self):
        email = self.name_input.text()
        password = self.password_input.text()
        with self.database.session() as session:
            user = Users(email=email, password=password)
            session.add(user)
            session.commit()
            self.create_signal.emit()
        self.name_input.setText("")
        self.password_input.setText("")


