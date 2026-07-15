from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QTextEdit, QHBoxLayout, QPushButton, \
    QWidget

from database.models import ServiceProjects


class EditServiceProject(QWidget):
    save_signal = Signal()
    def __init__(self, database, user_id, project_id, parent=None):
        super().__init__(parent)
        self.database = database
        self.user_id = user_id
        self.project_id = project_id
        self.parent = parent

        self.deactivate_slot = None
        self.activate_slot = None


        with self.database.session() as session:
            self.project = session.query(ServiceProjects).get(self.project_id)

        self.setWindowTitle("Edit Service Project")

        self.main_layout_vertical = QVBoxLayout()
        self.setLayout(self.main_layout_vertical)

        self.layout = QGridLayout()
        self.main_layout_vertical.addLayout(self.layout)
        self.number_title_label = QLabel("Number: ")
        self.layout.addWidget(self.number_title_label, 0, 0)

        self.number_input = QLineEdit()
        self.number_input.setText(self.project.number)
        self.number_input.setStyleSheet("color: #3498db; font-weight: bold;")
        self.number_input.setReadOnly(True)
        self.layout.addWidget(self.number_input, 0, 1)

        self.receive_date_label = QLabel("Date:")
        self.layout.addWidget(self.receive_date_label, 1, 0)
        self.receive_date_input = QLineEdit()
        self.receive_date_input.setText(self.project.start_date.strftime("%d-%m-%Y"))
        self.receive_date_input.setStyleSheet("color: #3498db;")
        self.receive_date_input.setReadOnly(True)
        self.layout.addWidget(self.receive_date_input, 1, 1)

        self.inputs = []

        self.owner_label = QLabel("Owner: ")
        self.layout.addWidget(self.owner_label, 2, 0)
        self.owner_input = QLineEdit()
        self.layout.addWidget(self.owner_input, 2, 1)
        self.inputs.append(self.owner_input)

        self.phone_number_label = QLabel("Phone Number: ")
        self.layout.addWidget(self.phone_number_label, 3, 0)
        self.phone_number_input = QLineEdit()
        self.layout.addWidget(self.phone_number_input, 3, 1)
        self.inputs.append(self.phone_number_input)

        self.email_label = QLabel("Email: ")
        self.layout.addWidget(self.email_label, 4, 0)
        self.email_input = QLineEdit()
        self.layout.addWidget(self.email_input, 4, 1)
        self.inputs.append(self.email_input)

        self.manufacturer_label = QLabel("Manufacturer: ")
        self.layout.addWidget(self.manufacturer_label, 5, 0)
        self.manufacturer_input = QLineEdit()
        self.layout.addWidget(self.manufacturer_input, 5, 1)
        self.inputs.append(self.manufacturer_input)

        self.model_label = QLabel("Model: ")
        self.layout.addWidget(self.model_label, 6, 0)
        self.model_input = QLineEdit()
        self.layout.addWidget(self.model_input, 6, 1)
        self.inputs.append(self.model_input)

        self.code_label = QLabel("Code: ")
        self.layout.addWidget(self.code_label, 7, 0)
        self.code_input = QLineEdit()
        self.layout.addWidget(self.code_input, 7, 1)
        self.inputs.append(self.code_input)

        self.serial_number_label = QLabel("Serial Number: ")
        self.layout.addWidget(self.serial_number_label, 8, 0)
        self.serial_number_input = QLineEdit()
        self.layout.addWidget(self.serial_number_input, 8, 1)
        self.inputs.append(self.serial_number_input)

        self.description_label = QLabel("Description: ")
        self.layout.addWidget(self.description_label, 9, 0)
        self.description_input = QTextEdit()
        self.layout.addWidget(self.description_input, 9, 1)
        self.inputs.append(self.description_input)


        self.main_layout_vertical.addStretch(1)


        self.button_layout = QHBoxLayout()
        self.main_layout_vertical.addLayout(self.button_layout)

        self.save_button = QPushButton("Save")
        self.save_button.setDisabled(True)
        self.button_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_button_handler)


        self.refresh()

        # self.inputs.append(self.description_input)
        for i in self.inputs:
            i.textChanged.connect(self.save_button_enabler)

    def refresh(self):
        with self.database.session() as session:
            self.project = session.query(ServiceProjects).get(self.project_id)
            self.owner_input.setText(self.project.owner)
            self.phone_number_input.setText(self.project.phone_number)
            self.email_input.setText(self.project.email)
            self.manufacturer_input.setText(self.project.manufacturer)
            self.model_input.setText(self.project.model)
            self.code_input.setText(self.project.code)
            self.serial_number_input.setText(self.project.serial_number)
            self.description_input.setText(self.project.description)

    def save_button_handler(self):

        with self.database.session() as session:
            project = session.query(ServiceProjects).get(self.project_id)
            project.owner = self.owner_input.text()
            project.phone_number = self.phone_number_input.text()
            project.email = self.email_input.text()
            project.manufacturer = self.manufacturer_input.text()
            project.model = self.model_input.text()
            project.code = self.code_input.text()
            project.serial_number = self.serial_number_input.text()
            project.description = self.description_input.toPlainText()
            session.commit()
            self.save_signal.emit()

    def save_button_enabler(self, *args):
        # compare state with state after textchange signal triggered in input

        if (self.project.owner or "").strip() != self.owner_input.text().strip() or \
            self.project.phone_number.strip() != self.phone_number_input.text().strip() or \
            self.project.email.strip() != self.email_input.text().strip() or \
            self.project.manufacturer.strip() != self.manufacturer_input.text().strip() or \
            self.project.model.strip() != self.model_input.text().strip() or \
            self.project.code.strip() != self.code_input.text().strip() or \
            self.project.serial_number.strip() != self.serial_number_input.text().strip() or \
            self.project.description.strip() != self.description_input.toPlainText().strip():
            self.save_button.setEnabled(True)
        else:
            self.save_button.setEnabled(False)
