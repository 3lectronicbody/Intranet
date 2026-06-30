from PySide6.QtWidgets import QVBoxLayout, QDialog, QGridLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton, QComboBox, \
    QMenuBar, QFileDialog, QMessageBox, QApplication, QWidget
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
    def __init__(self, database, user_id, parent=None):
        # if create_flag = False -> edit mode
        super().__init__(parent)
        self.database = database
        self.user_id = user_id
        self.parent = parent

        self.setWindowTitle("Create Service Project")
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.owner_label = QLabel("Owner: ")
        self.layout.addWidget(self.owner_label, 0, 0)
        self.owner_input = QLineEdit()
        self.layout.addWidget(self.owner_input, 0, 1)

        self.number_title_label = QLabel("Number: ")
        self.layout.addWidget(self.number_title_label, 1, 0)
        with (self.database.session() as session):
            last_project = session.query(ServiceProjects).order_by(ServiceProjects.id.desc()).first()

            if last_project:
                last_number = int(last_project.number[-3:])
                actual_number = last_number + 1
                formatted_actual_number = f"{actual_number:03d}"
                actual_number = str(datetime.now().year)+"/"+str(formatted_actual_number)
            else:
                actual_number = str(datetime.now().year)+"/001"
        self.number_input = QLineEdit()
        self.number_input.setText(actual_number)
        self.number_input.setReadOnly(True)
        self.layout.addWidget(self.number_input, 1, 1)

        self.receive_date_label = QLabel("Receive date:")
        self.layout.addWidget(self.receive_date_label, 2, 0)
        self.receive_date_input = QLineEdit()
        actual_date = datetime.now().strftime("%d-%m-%Y")
        self.receive_date_input.setText(actual_date)
        self.layout.addWidget(self.receive_date_input, 2, 1)














