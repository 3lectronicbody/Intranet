from PySide6.QtWidgets import QVBoxLayout, QDialog, QGridLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton, QComboBox
from PySide6.QtCore import Signal

from database.models import ProjectDetails


class AddItemActivity(QDialog):
    save_signal = Signal()
    def __init__(self, database, project_id, user_id, flag=None):
        super().__init__()
        self.database = database
        self.project_id = project_id
        self.user_id = user_id
        self.flag = flag

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.data_layout = QGridLayout()
        self.layout.addLayout(self.data_layout)

        self.name_label = QLabel("Name: ")
        self.data_layout.addWidget(self.name_label, 0, 0)
        self.name_input = QLineEdit()
        self.data_layout.addWidget(self.name_input, 0, 1)
        if self.flag == "item":
            self.code_label = QLabel("Code: ")
            self.data_layout.addWidget(self.code_label, 1, 0)
            self.code_input = QLineEdit()
            self.data_layout.addWidget(self.code_input, 1, 1)
            self.quantity_label = QLabel("Quantity: ")
            self.data_layout.addWidget(self.quantity_label, 2, 0)
            units = ["mtr", "psc"]
            self.unit_label = QLabel("Unit: ")
            self.data_layout.addWidget(self.unit_label, 3, 0)
            self.unit_dropdown = QComboBox()
            self.unit_dropdown.addItems(units)
            self.data_layout.addWidget(self.unit_dropdown, 3, 1)
            self.unit_dropdown.setCurrentText("mtr")
            self.setWindowTitle("Add Item")

        elif self.flag == "activity":
            self.setWindowTitle("Add Activity")
            self.quantity_label = QLabel("Time: ")
            self.data_layout.addWidget(self.quantity_label, 2, 0)

        self.quantity_input = QLineEdit()
        self.data_layout.addWidget(self.quantity_input, 2, 1)

        self.buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.buttons_layout)

        self.save_button = QPushButton("Save")
        self.buttons_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_button_handler)
        self.cancel_button = QPushButton("Cancel")
        self.buttons_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.reject)

    def save_button_handler(self):
        if self.flag == "item":
            name = self.name_input.text() or None
            code = self.code_input.text() or None
            quantity = self.quantity_input.text() or None
            unit = self.unit_dropdown.currentText()
            with self.database.session() as session:
                new = ProjectDetails(project_id=self.project_id,
                                     item=name,
                                     item_code=code,
                                     quantity=quantity,
                                     unit=unit)
                session.add(new)
                session.commit()
                self.accept()
                self.save_signal.emit()
        elif self.flag == "activity":
            name = self.name_input.text() or None
            code = None
            quantity = self.quantity_input.text() or None
            with self.database.session() as session:
                new = ProjectDetails(project_id=self.project_id,
                                     activity=name,
                                     item_code=code,
                                     quantity=quantity)
                session.add(new)
                session.commit()
                self.accept()
                self.save_signal.emit()
class CustomPushButton(QPushButton):
    # Added "Enter" key press event to the button"
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        # "Enter" as default trigger key
    def keyPressEvent(self,event):
        if event.key() == 16777220:
            self.clicked.emit()
            return
        super().keyPressEvent(event)




