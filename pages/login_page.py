from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QLineEdit, QHBoxLayout, \
    QMessageBox
from custom_widgets_folder.custom_widgets import CustomPushButton
from database.models import Users
import platform
import ctypes
from API.main import client


class LoginPage(QWidget):
    login_signal = Signal(int)
    close_signal = Signal()
    sign_up_signal = Signal()

    def __init__(self, database):
        super().__init__()

        self.database = database

        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        self.caps_timer = QTimer(self)
        self.caps_timer.timeout.connect(self.check_caps_lock)
        self.caps_timer.start(100)  # Checks every 100 milliseconds




        self.email_label = QLabel("Email: ")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        self.email_input.setMinimumWidth(200)
        self.main_layout.addWidget(self.email_label, 0, 0)
        self.main_layout.addWidget(self.email_input, 0, 1)

        self.password_label = QLabel("Password: ")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password: ")
        self.main_layout.addWidget(self.password_label, 1, 0)
        self.main_layout.addWidget(self.password_input, 1, 1)

        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout, 2,0,1,2)


        self.login_button = CustomPushButton("LOGIN")
        self.button_layout.addWidget(self.login_button)
        self.login_button.clicked.connect(self.login_handler)

        self.cancel_button = QPushButton("CANCEL")
        self.button_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.cancel_handler)

        self.sign_up_link = QPushButton("Sign Up", flat=True)
        self.sign_up_link.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #0000FF; /* Standard Blue */;
                text-transform: none;  /* This stops the capitalization */
                
            }
            QPushButton:hover {
                color: #0000AA; /* Darker blue when hovering */
                text-decoration: underline;
            }
            QPushButton:pressed {
                color: grey; 
            }
        """)
        self.sign_up_link.setCursor(Qt.PointingHandCursor)
        self.main_layout.addWidget(self.sign_up_link, 3,0,1,2, alignment=Qt.AlignCenter)
        self.sign_up_link.clicked.connect(self.sign_up_handler)

        self.caps_on_label = QLabel("")
        self.caps_on_label.setStyleSheet("color: red;")
        self.main_layout.addWidget(self.caps_on_label, 4,0,1,2, alignment=Qt.AlignCenter)

        # self.main_layout.setRowStretch(5, 1)
        # Adjust the widget to its minimum necessary size
        self.adjustSize()





    def login_handler(self):
        email = self.email_input.text()
        password = self.password_input.text()
        # Role is set default in database model

        response = client.get("/login", params={"user_email": email, "user_password": password})
        if response.json():
            self.login_signal.emit(response.json()["user_id"])
            self.email_input.setText("")
            self.password_input.setText("")
        else:
            QMessageBox.warning(self, "Error", "Invalid email or password")
            self.email_input.setText("")
            self.password_input.setText("")



    def cancel_handler(self):
        self.close_signal.emit()

    def sign_up_handler(self):
        self.email_input.setText("")
        self.password_input.setText("")
        self.sign_up_signal.emit()

    def check_caps_lock(self):
        platform_name = platform.system()
        if platform_name == "Windows":
            if ctypes.windll.user32.GetKeyState(0x14) & 1 != 0:
                self.caps_on_label.setText("Caps Lock is ON")
            else:
                self.caps_on_label.setText("")
        elif platform_name == "Darwin":
            pass
    def showEvent(self, event):
        super().showEvent(event)





