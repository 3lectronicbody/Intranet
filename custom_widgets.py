from PySide6.QtWidgets import QVBoxLayout, QDialog, QGridLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton, QComboBox, \
    QMenuBar, QFileDialog, QMessageBox, QApplication, QWidget, QTextEdit
from PySide6.QtCore import Signal
from fpdf import FPDF
from database.models import ProjectDetails, Projects, ServiceProjects
from datetime import datetime

class AddItem(QDialog):
    save_signal = Signal()
    def __init__(self, database, project_id, user_id):
        super().__init__()
        self.database = database
        self.project_id = project_id
        self.user_id = user_id

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.data_layout = QGridLayout()
        self.layout.addLayout(self.data_layout)

        self.name_label = QLabel("Name: ")
        self.data_layout.addWidget(self.name_label, 0, 0)
        self.name_input = QLineEdit()
        self.data_layout.addWidget(self.name_input, 0, 1)

        self.code_label = QLabel("Code: ")
        self.data_layout.addWidget(self.code_label, 1, 0)
        self.code_input = QLineEdit()
        self.data_layout.addWidget(self.code_input, 1, 1)

        self.quantity_label = QLabel("Quantity: ")
        self.data_layout.addWidget(self.quantity_label, 2, 0)
        self.quantity_input = QLineEdit()
        self.data_layout.addWidget(self.quantity_input, 2, 1)
        units = ["mtr", "psc"]
        self.unit_label = QLabel("Unit: ")
        self.data_layout.addWidget(self.unit_label, 3, 0)
        self.unit_dropdown = QComboBox()
        self.unit_dropdown.addItems(units)
        self.data_layout.addWidget(self.unit_dropdown, 3, 1)
        self.unit_dropdown.setCurrentText("mtr")
        self.setWindowTitle("Add Item")

        self.buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.buttons_layout)
        self.save_button = QPushButton("Save")
        self.buttons_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_button_handler)
        self.cancel_button = QPushButton("Cancel")
        self.buttons_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.reject)
    def save_button_handler(self):
        self.name_input.setStyleSheet("")
        self.code_input.setStyleSheet("")
        self.quantity_input.setStyleSheet("")
        name = self.name_input.text().strip()
        code = self.code_input.text().strip()
        quantity = self.quantity_input.text().replace(",", ".").strip()
        unit = self.unit_dropdown.currentText()
        if not name:
            warning = QMessageBox()
            warning.setText("Item name cannot be empty")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.name_input.setStyleSheet("border: 2px solid red;")
            self.name_input.setFocus()
            return
        if not code:
            warning = QMessageBox()
            warning.setText("Item code cannot be empty")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.code_input.setStyleSheet("border: 2px solid red;")
            self.code_input.setFocus()
            return

        if not quantity:
            warning = QMessageBox()
            warning.setText("Quantity cannot be empty")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.quantity_input.clear()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return
        try:
            quantity = float(quantity)
        except ValueError:
            warning = QMessageBox()
            warning.setText("Quantity must be a number")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return

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
class EditItem(QDialog):
    save_signal = Signal()

    def __init__(self, database, project_id, user_id, item_id):
        super().__init__()
        self.database = database
        self.project_id = project_id
        self.user_id = user_id
        self.item_id = item_id
        self.setWindowTitle("Edit Item")

        with self.database.session() as session:
            item = session.query(ProjectDetails).get(item_id)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data_layout = QGridLayout()
        self.layout.addLayout(self.data_layout)

        self.name_label = QLabel("Name: ")
        self.data_layout.addWidget(self.name_label, 0, 0)

        self.name_input = QLineEdit()
        self.name_input.setText(item.item)
        self.data_layout.addWidget(self.name_input, 0, 1)

        self.code_label = QLabel("Code: ")
        self.data_layout.addWidget(self.code_label, 1, 0)

        self.code_input = QLineEdit()
        self.code_input.setText(item.item_code)
        self.data_layout.addWidget(self.code_input, 1, 1)

        self.quantity_label = QLabel("Quantity: ")
        self.data_layout.addWidget(self.quantity_label, 2, 0)

        self.quantity_input = QLineEdit()
        self.quantity_input.setText(str(item.quantity))
        self.data_layout.addWidget(self.quantity_input, 2, 1)

        self.unit_label = QLabel("Unit: ")
        self.data_layout.addWidget(self.unit_label, 3, 0)

        self.unit_dropdown = QComboBox()
        units = ["mtr", "psc"]
        self.unit_dropdown.addItems(units)
        if item.unit in units:
            self.unit_dropdown.setCurrentText(item.unit)
        else:
            self.unit_dropdown.setCurrentIndex(0)
        self.data_layout.addWidget(self.unit_dropdown, 3, 1)

        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.save_button = QPushButton("Save")
        self.button_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_button_handler)

        self.cancel_button = QPushButton("Cancel")
        self.button_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.reject)

    def save_button_handler(self):
        name = self.name_input.text()
        quantity = self.quantity_input.text()
        code = self.code_input.text()
        unit = self.unit_dropdown.currentText()
        if not name:
            warning = QMessageBox()
            warning.setText("Item name cannot be empty")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.name_input.setStyleSheet("border: 2px solid red;")
            self.name_input.setFocus()
            return
        if not code:
            warning = QMessageBox()
            warning.setText("Item code cannot be empty")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.code_input.setStyleSheet("border: 2px solid red;")
            self.code_input.setFocus()
            return

        if not quantity:
            warning = QMessageBox()
            warning.setText("Quantity cannot be empty")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.quantity_input.clear()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return
        try:
            quantity = float(quantity)
        except ValueError:
            warning = QMessageBox()
            warning.setText("Quantity must be a number")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return
        with self.database.session() as session:
            item = session.query(ProjectDetails).get(self.item_id)
            item.name = name
            item.quantity = quantity
            item.unit = unit
            item.item_code = code
            session.commit()
            self.accept()
            self.save_signal.emit()
class AddActivity(QDialog):
    save_signal = Signal()

    def __init__(self, database, project_id, user_id):
        super().__init__()
        self.database = database
        self.project_id = project_id
        self.user_id = user_id

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.data_layout = QGridLayout()
        self.layout.addLayout(self.data_layout)

        self.name_label = QLabel("Name: ")
        self.data_layout.addWidget(self.name_label, 0, 0)
        self.name_input = QLineEdit()
        self.data_layout.addWidget(self.name_input, 0, 1)

        self.quantity_label = QLabel("Time: ")
        self.data_layout.addWidget(self.quantity_label, 1, 0)
        self.quantity_input = QLineEdit()
        self.data_layout.addWidget(self.quantity_input, 1, 1)

        self.setWindowTitle("Add Activity")

        self.buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.buttons_layout)
        self.save_button = QPushButton("Save")
        self.buttons_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_button_handler)
        self.cancel_button = QPushButton("Cancel")
        self.buttons_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.reject)

    def save_button_handler(self):
        name = self.name_input.text() or None
        quantity = self.quantity_input.text() or None
        if not name:
            warning = QMessageBox()
            warning.setText("Activity name cannot be empty")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.name_input.setStyleSheet("border: 2px solid red;")
            self.name_input.setFocus()
            return
        if not quantity or not quantity.isnumeric():
            warning = QMessageBox()
            warning.setText("Quantity must be a number")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return

        else:
            with self.database.session() as session:
                new = ProjectDetails(project_id=self.project_id,
                                     activity=name,
                                     quantity=quantity)
                session.add(new)
                session.commit()
                self.accept()
                self.save_signal.emit()
class EditActivity(QDialog):
    save_signal = Signal()

    def __init__(self, database, project_id, user_id, item_id):
        super().__init__()
        self.database = database
        self.project_id = project_id
        self.user_id = user_id
        self.item_id = item_id
        self.setWindowTitle("Edit Item")



        with self.database.session() as session:
            item = session.query(ProjectDetails).get(item_id)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data_layout = QGridLayout()
        self.layout.addLayout(self.data_layout)

        self.name_label = QLabel("Name: ")
        self.data_layout.addWidget(self.name_label, 0, 0)

        self.name_input = QLineEdit()
        self.name_input.setText(item.activity)
        self.data_layout.addWidget(self.name_input, 0, 1)


        self.quantity_label = QLabel("Quantity: ")
        self.data_layout.addWidget(self.quantity_label, 1, 0)

        self.quantity_input = QLineEdit()
        self.quantity_input.setText(str(item.quantity))
        self.data_layout.addWidget(self.quantity_input, 1, 1)


        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.save_button = QPushButton("Save")
        self.button_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_button_handler)

        self.cancel_button = QPushButton("Cancel")
        self.button_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.reject)

    def save_button_handler(self):
        activity = self.name_input.text()
        quantity = self.quantity_input.text().strip().replace(",", ".")

        self.quantity_input.setStyleSheet("")
        self.name_input.setStyleSheet("")

        if not activity:
            message = QMessageBox()
            message.setText("Please enter a name")
            message.exec()
            self.name_input.setStyleSheet("border: 2px solid red;")
            return
        if not quantity:
            message = QMessageBox()
            message.setText(f"Please enter a quantity")
            message.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            return
        try:
            quantity = float(quantity)
        except ValueError:
            message = QMessageBox()
            message.setText("Please enter a number")
            message.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            return
        if quantity <= 0:
            message = QMessageBox()
            message.setText("Quantity value must be greater than zero")
            message.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return


        with self.database.session() as session:

            item = session.query(ProjectDetails).get(self.item_id)
            item.activity = activity
            item.quantity = quantity
            session.commit()
            self.accept()
            self.save_signal.emit()
class AddToDo(QDialog):
    save_signal = Signal()

    def __init__(self, database, project_id, user_id):
        super().__init__()
        self.database = database
        self.project_id = project_id
        self.user_id = user_id

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.data_layout = QGridLayout()
        self.layout.addLayout(self.data_layout)

        self.name_label = QLabel("Name: ")
        self.data_layout.addWidget(self.name_label, 0, 0)
        self.name_input = QLineEdit()
        self.data_layout.addWidget(self.name_input, 0, 1)

        self.quantity_label = QLabel("Time: ")
        self.data_layout.addWidget(self.quantity_label, 1, 0)
        self.quantity_input = QLineEdit()
        self.data_layout.addWidget(self.quantity_input, 1, 1)

        self.setWindowTitle("Add Todo")

        self.buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.buttons_layout)
        self.save_button = QPushButton("Save")
        self.buttons_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_button_handler)
        self.cancel_button = QPushButton("Cancel")
        self.buttons_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.reject)

    def save_button_handler(self):
        name = self.name_input.text()
        quantity = self.quantity_input.text()
        if not name:
            warning = QMessageBox()
            warning.setText("Todo name cannot be empty")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.name_input.setStyleSheet("border: 2px solid red;")
            self.name_input.setFocus()
            return
        if not quantity or not quantity.isnumeric():
            warning = QMessageBox()
            warning.setText("Quantity must be a number")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return

        else:
            with self.database.session() as session:
                new = ProjectDetails(project_id=self.project_id,
                                     todo=name,
                                     quantity=quantity)
                session.add(new)
                session.commit()
                self.accept()
                self.save_signal.emit()
class EditToDo(QDialog):
    save_signal = Signal()

    def __init__(self, database, project_id, user_id, item_id):
        super().__init__()
        self.database = database
        self.project_id = project_id
        self.user_id = user_id
        self.item_id = item_id
        self.setWindowTitle("Edit Item")

        with self.database.session() as session:
            item = session.query(ProjectDetails).get(item_id)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data_layout = QGridLayout()
        self.layout.addLayout(self.data_layout)

        self.name_label = QLabel("Name: ")
        self.data_layout.addWidget(self.name_label, 0, 0)

        self.name_input = QLineEdit()
        self.name_input.setText(item.todo)
        self.data_layout.addWidget(self.name_input, 0, 1)

        self.quantity_label = QLabel("Quantity: ")
        self.data_layout.addWidget(self.quantity_label, 1, 0)

        self.quantity_input = QLineEdit()
        self.quantity_input.setText(str(item.quantity))
        self.data_layout.addWidget(self.quantity_input, 1, 1)

        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.save_button = QPushButton("Save")
        self.button_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_button_handler)

        self.cancel_button = QPushButton("Cancel")
        self.button_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.reject)

    def save_button_handler(self):
        with self.database.session() as session:
            item = session.query(ProjectDetails).get(self.item_id)
            item.todo = self.name_input.text()
            item.quantity = self.quantity_input.text()
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

class MenuBar(QMenuBar):
    def __init__(self, parent, database, user_id, project_id=None, flag=None):
        # flag=project: Menu bar for project window
        # flag=main: Menu bar for main menu
        super().__init__(parent)

        self.parent = parent
        self.database = database
        self.project_id = project_id
        self.user_id = user_id
        self.flag = flag

        self.setStyleSheet("background-color: #2c3e50; border-radius: 2px;")
        # ADD FILE MENU TO MENU BAR
        self.file_menu = self.addMenu("File")

        if self.flag == "project":
            self.export_project = self.file_menu.addAction("Export Project...")
            self.export_project.triggered.connect(self.export_project_handler)

            self.main_menu = self.addAction("Main Menu")
            self.main_menu.triggered.connect(self.main_menu_handler)


        # EXIT BUTTON MENU
        self.exit = self.addAction("Exit")
        self.exit.triggered.connect(lambda _: self.exit_button_handler())

    def export_project_handler(self):
        file_path, selected_filter = QFileDialog.getSaveFileName(self)
        if file_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            with self.database.session() as session:
                all_items = session.query(ProjectDetails).filter_by(project_id=self.project_id).all()
                items = [item for item in all_items if item.activity is None and item.todo is None]
                activities = [item for item in all_items if item.activity is not None]

                item_column_width = {"name": 60, "quantity": 20, "code": 40, "unit": 20}

                pdf.cell(100, 10, txt=f"Project Name: {session.query(Projects).get(self.project_id).name}", ln=1)
                pdf.cell(100, 10, txt="ITEMS", ln=1)

                for i in items:
                    pdf.cell(item_column_width["name"], 10, txt=i.item or "", ln=0)
                    pdf.cell(item_column_width["quantity"], 10, txt=str(i.quantity), ln=0)
                    pdf.cell(item_column_width["code"], 10, txt=i.item_code, ln=0)
                    pdf.cell(item_column_width["unit"], 10, txt=i.unit, ln=1)


                activity_column_width = {"name": 60, "quantity": 20}
                pdf.cell(100, 10, txt="ACTIVITIES", ln=1)

                for i in activities:
                    pdf.cell(activity_column_width["name"], 10, txt=i.activity or "", ln=0)
                    pdf.cell(activity_column_width["quantity"], 10, txt=str(i.quantity), ln=1)

            if file_path[-4:] != ".pdf":
                file_path += ".pdf"

            pdf.output(file_path)
    @staticmethod
    def exit_button_handler():
        app_instance = QApplication.instance()
        if app_instance:
            app_instance.quit()
    def main_menu_handler(self):
        if self.parent:
            self.parent.accept()

class CreateServiceProject(QDialog):
    save_signal = Signal()
    def __init__(self, database, user_id, project_id=None, parent=None):
        super().__init__(parent)
        self.database = database
        self.user_id = user_id
        self.project_id = project_id
        if self.project_id:
            with self.database.session() as session:
                self.project = session.query(ServiceProjects).get(self.project_id)
        self.parent = parent

        self.setWindowTitle("Create Service Project")

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)


        self.layout = QGridLayout()
        self.main_layout.addLayout(self.layout)

        self.number_title_label = QLabel("Number: ")
        self.layout.addWidget(self.number_title_label, 0, 0)
        with (self.database.session() as session):
            last_project = session.query(ServiceProjects).order_by(ServiceProjects.id.desc()).first()

            if last_project:
                last_number = int(last_project.number[-3:])
                actual_number = last_number + 1
                formatted_actual_number = f"{actual_number:03d}"
                actual_number = str(datetime.now().year) + "/" + str(formatted_actual_number)
            else:
                actual_number = str(datetime.now().year) + "/001"
        self.number_input = QLineEdit()
        self.number_input.setText(actual_number)
        self.number_input.setStyleSheet("color: #3498db;")
        self.number_input.setReadOnly(True)
        self.layout.addWidget(self.number_input, 0, 1)

        self.receive_date_label = QLabel("Date:")
        self.layout.addWidget(self.receive_date_label, 1, 0)
        self.receive_date_input = QLineEdit()
        actual_date = datetime.now().strftime("%d-%m-%Y")
        self.receive_date_input.setText(actual_date)
        self.receive_date_input.setStyleSheet("color: #3498db;")
        self.receive_date_input.setReadOnly(True)
        self.layout.addWidget(self.receive_date_input, 1, 1)

        self.owner_label = QLabel("Owner: ")
        self.layout.addWidget(self.owner_label, 2, 0)
        self.owner_input = QLineEdit()
        self.layout.addWidget(self.owner_input, 2, 1)

        self.phone_number_label = QLabel("Phone Number: ")
        self.layout.addWidget(self.phone_number_label, 3, 0)
        self.phone_number_input = QLineEdit()
        self.layout.addWidget(self.phone_number_input, 3, 1)

        self.email_label = QLabel("Email: ")
        self.layout.addWidget(self.email_label, 4, 0)
        self.email_input = QLineEdit()
        self.layout.addWidget(self.email_input, 4, 1)

        self.manufacturer_label = QLabel("Manufacturer: ")
        self.layout.addWidget(self.manufacturer_label, 5, 0)
        self.manufacturer_input = QLineEdit()
        self.layout.addWidget(self.manufacturer_input, 5, 1)

        self.model_label = QLabel("Model: ")
        self.layout.addWidget(self.model_label, 6, 0)
        self.model_input = QLineEdit()
        self.layout.addWidget(self.model_input, 6, 1)

        self.code_label = QLabel("Code: ")
        self.layout.addWidget(self.code_label, 7, 0)
        self.code_input = QLineEdit()
        self.layout.addWidget(self.code_input, 7, 1)

        self.serial_number_label = QLabel("Serial Number: ")
        self.layout.addWidget(self.serial_number_label, 8, 0)
        self.serial_number_input = QLineEdit()
        self.layout.addWidget(self.serial_number_input, 8, 1)

        self.description_label = QLabel("Description: ")
        self.layout.addWidget(self.description_label, 9, 0)
        self.description_input = QTextEdit()
        self.layout.addWidget(self.description_input, 9 ,1)

        self.main_layout.addStretch(1)

        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        self.create_button = QPushButton("Create")
        self.button_layout.addWidget(self.create_button)
        self.create_button.clicked.connect(self.create_button_handler)
        self.cancel_button = QPushButton("Cancel")
        self.button_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.cancel_button_handler)
    @classmethod
    def details(cls, database, user_id, project_id, parent=None, editable=False):
        instance = cls(database, user_id,project_id, parent)
        with database.session() as session:
            project = session.query(ServiceProjects).get(project_id)
            instance.setWindowTitle("Service Project Details")
            instance.receive_date_input.setText(project.start_date.strftime("%d-%m-%Y"))
            instance.owner_input.setText(project.owner)
            instance.phone_number_input.setText(project.phone_number)
            instance.email_input.setText(project.email)
            instance.manufacturer_input.setText(project.manufacturer)
            instance.model_input.setText(project.model)
            instance.code_input.setText(project.code)
            instance.serial_number_input.setText(project.serial_number)
            instance.description_input.setText(project.description)

        for widget in instance.findChildren(QLineEdit)+instance.findChildren(QTextEdit):
            widget.setReadOnly(True)
        instance.create_button.hide()
        instance.cancel_button.setText("Back")

        if not editable:
            activate_button = QPushButton("Activate")
            instance.main_layout.addWidget(activate_button)
            activate_button.clicked.connect(lambda _, pid=project_id: instance.activate_button_handler(pid))
            if project.active:
                activate_button.setEnabled(False)
        if editable:
            instance.create_button.show()
            instance.create_button.clicked.disconnect()
            instance.create_button.setText("Save")
            instance.create_button.clicked.connect(lambda _, pid=project_id  :instance.save_button_handler(pid))
            for widget in instance.findChildren(QLineEdit) + instance.findChildren(QTextEdit):
                widget.setReadOnly(False)
            instance.number_input.setReadOnly(True)
            instance.receive_date_input.setReadOnly(True)


        return instance


    def create_button_handler(self):
        formatted_date = datetime.strptime(self.receive_date_input.text(), "%d-%m-%Y")
        with self.database.session() as session:
            new_project = ServiceProjects(number=self.number_input.text(),
                                         start_date=formatted_date,
                                         owner=self.owner_input.text(),
                                         phone_number=self.phone_number_input.text(),
                                         email=self.email_input.text(),
                                         manufacturer=self.manufacturer_input.text(),
                                         model=self.model_input.text(),
                                         code=self.code_input.text(),
                                         serial_number=self.serial_number_input.text(),
                                         description=self.description_input.toPlainText(),
            )
            session.add(new_project)
            session.commit()
            self.save_signal.emit()
            self.accept()
    def cancel_button_handler(self):
        self.reject()
    def save_button_handler(self, project_id):
        with self.database.session() as session:
            project = session.query(ServiceProjects).get(project_id)
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
            self.accept()
    def activate_button_handler(self, project_id):
        with self.database.session() as session:
            project = session.query(ServiceProjects).get(project_id)
            project.active = True
            project.end_date = None
            session.commit()
            self.save_signal.emit()
            self.accept()




















